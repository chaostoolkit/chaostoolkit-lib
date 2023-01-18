import numbers
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator, List

from logzero import logger

from chaoslib import substitute
from chaoslib.caching import lookup_activity
from chaoslib.control import controls
from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.provider.http import run_http_activity, validate_http_activity
from chaoslib.provider.process import run_process_activity, validate_process_activity
from chaoslib.provider.python import run_python_activity, validate_python_activity
from chaoslib.types import Activity, Configuration, Dry, Experiment, Run, Secrets

if TYPE_CHECKING:
    from chaoslib.run import EventHandlerRegistry

__all__ = [
    "ensure_activity_is_valid",
    "get_all_activities_in_experiment",
    "run_activities",
]


def ensure_activity_is_valid(activity: Activity):  # noqa: C901
    """
    Goes through the activity and checks certain of its properties and raise
    :exc:`InvalidActivity` whenever one does not respect the expectations.

    An activity must at least take the following key:

    * `"type"` the kind of activity, one of `"python"`, `"process"` or `"http"`

    Depending on the type, an activity requires a variety of other keys.

    In all failing cases, raises :exc:`InvalidActivity`.
    """
    if not activity:
        raise InvalidActivity("empty activity is no activity")

    # when the activity is just a ref, there is little to validate
    ref = activity.get("ref")
    if ref is not None:
        if not isinstance(ref, str) or ref == "":
            raise InvalidActivity("reference to activity must be non-empty strings")
        return

    activity_type = activity.get("type")
    if not activity_type:
        raise InvalidActivity("an activity must have a type")

    if activity_type not in ("probe", "action"):
        raise InvalidActivity(f"'{activity_type}' is not a supported activity type")

    if not activity.get("name"):
        raise InvalidActivity("an activity must have a name")

    provider = activity.get("provider")
    if not provider:
        raise InvalidActivity("an activity requires a provider")

    provider_type = provider.get("type")
    if not provider_type:
        raise InvalidActivity("a provider must have a type")

    if provider_type not in ("python", "process", "http"):
        raise InvalidActivity(f"unknown provider type '{provider_type}'")

    if not activity.get("name"):
        raise InvalidActivity("activity must have a name (cannot be empty)")

    timeout = activity.get("timeout")
    if timeout is not None:
        if not isinstance(timeout, numbers.Number):
            raise InvalidActivity("activity timeout must be a number")

    pauses = activity.get("pauses")
    if pauses is not None:
        before = pauses.get("before")
        if before is not None:
            if isinstance(before, str):
                if (
                    not before.startswith("${") or not before.endswith("}")
                ) or isinstance(before, numbers.Number):
                    raise InvalidActivity(
                        "activity before pause must be a number or a pattern "
                        "to a variable from the configuration or secrets"
                    )
        after = pauses.get("after")
        if after is not None:
            if isinstance(after, str):
                if (
                    not after.startswith("${") or not after.endswith("}")
                ) or isinstance(after, numbers.Number):
                    raise InvalidActivity(
                        "activity after pause must be a number or a pattern "
                        "to a variable from the configuration or secrets"
                    )

    if "background" in activity:
        if not isinstance(activity["background"], bool):
            raise InvalidActivity("activity background must be a boolean")

    if provider_type == "python":
        validate_python_activity(activity)
    elif provider_type == "process":
        validate_process_activity(activity)
    elif provider_type == "http":
        validate_http_activity(activity)


def run_activities(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    pool: ThreadPoolExecutor,
    dry: Dry = None,
    event_registry: "EventHandlerRegistry" = None,
) -> Iterator[Run]:
    """
    Internal generator that iterates over all activities and execute them.
    Yields either the result of the run or a :class:`concurrent.futures.Future`
    if the activity was set to run in the `background`.
    """
    method = experiment.get("method", [])

    if not method:
        logger.info("No declared activities, let's move on.")

    for activity in method:
        if activity.get("background"):
            logger.debug("activity will run in the background")
            yield pool.submit(
                execute_activity,
                experiment=experiment,
                activity=activity,
                configuration=configuration,
                secrets=secrets,
                dry=dry,
                event_registry=event_registry,
            )
        else:
            yield execute_activity(
                experiment=experiment,
                activity=activity,
                configuration=configuration,
                secrets=secrets,
                dry=dry,
                event_registry=event_registry,
            )


###############################################################################
# Internal functions
###############################################################################
def execute_activity(
    experiment: Experiment,
    activity: Activity,
    configuration: Configuration,
    secrets: Secrets,
    dry: Dry,
    event_registry: "EventHandlerRegistry" = None,
) -> Run:
    """
    Low-level wrapper around the actual activity provider call to collect
    some meta data (like duration, start/end time, exceptions...) during
    the run.
    """
    ref = activity.get("ref")
    if ref:
        activity = lookup_activity(ref)
        if not activity:
            raise ActivityFailed(f"could not find referenced activity '{ref}'")

    with controls(
        level="activity",
        experiment=experiment,
        context=activity,
        configuration=configuration,
        secrets=secrets,
    ) as control:
        dry = activity.get("dry", dry)
        pauses = activity.get("pauses", {})
        pauses = substitute(pauses, configuration, secrets)
        pause_before = pauses.get("before")
        is_dry = False
        activity_type = activity["type"]
        if dry == Dry.ACTIONS:
            is_dry = activity_type == "action"
        elif dry == Dry.PROBES:
            is_dry = activity_type == "probe"
        elif dry == Dry.ACTIVITIES:
            is_dry = True
        if pause_before:
            logger.info(f"Pausing before next activity for {pause_before}s...")
            # pause when one of the dry flags are set
            if dry != Dry.PAUSE and not is_dry:
                time.sleep(pause_before)

        if activity.get("background"):
            logger.info(
                "{t}: {n} [in background]".format(
                    t=activity["type"].title(), n=activity.get("name")
                )
            )
        else:
            logger.info(
                "{t}: {n}".format(t=activity["type"].title(), n=activity.get("name"))
            )

        start = datetime.utcnow()

        run = {"activity": activity.copy(), "output": None}

        result = None
        interrupted = False
        try:
            if event_registry:
                event_registry.start_activity(activity)
            # pause when one of the dry flags are set
            if not is_dry:
                result = run_activity(activity, configuration, secrets)
            run["output"] = result
            run["status"] = "succeeded"
            if result is not None:
                logger.debug(f"  => succeeded with '{result}'")
            else:
                logger.debug("  => succeeded without any result value")
        except ActivityFailed as x:
            error_msg = str(x)
            run["status"] = "failed"
            run["output"] = result
            run["exception"] = traceback.format_exception(type(x), x, None)
            logger.error(f"  => failed: {error_msg}")
        finally:
            # capture the end time before we pause
            end = datetime.utcnow()
            run["start"] = start.isoformat()
            run["end"] = end.isoformat()
            run["duration"] = (end - start).total_seconds()

            if event_registry:
                event_registry.activity_completed(activity, run)

            pause_after = pauses.get("after")
            if pause_after and not interrupted:
                logger.info(f"Pausing after activity for {pause_after}s...")
                # pause when one of the dry flags are set
                if dry != Dry.PAUSE and not is_dry:
                    time.sleep(pause_after)

        control.with_state(run)

    return run


def run_activity(
    activity: Activity, configuration: Configuration, secrets: Secrets
) -> Any:
    """
    Run the given activity and return its result. If the activity defines a
    `timeout` this function raises :exc:`ActivityFailed`.

    This function assumes the activity is valid as per
    `ensure_layer_activity_is_valid`. Please be careful not to call this
    function without validating its input as this could be a security issue
    or simply fails miserably.

    This is an internal function and should probably avoid being called
    outside this package.
    """
    result = None
    try:
        provider = activity["provider"]
        activity_type = provider["type"]
        if activity_type == "python":
            result = run_python_activity(activity, configuration, secrets)
        elif activity_type == "process":
            result = run_process_activity(activity, configuration, secrets)
        elif activity_type == "http":
            result = run_http_activity(activity, configuration, secrets)
    except Exception:
        # just make sure we have a full traceback
        logger.debug("Activity failed", exc_info=True)
        raise

    return result


def get_all_activities_in_experiment(experiment: Experiment) -> List[Activity]:
    """
    Handy function to return all activities from a given experiment. Useful
    when you need to iterate over all the activities.
    """
    activities = []
    hypo = experiment.get("steady-state-hypothesis")
    if hypo:
        activities.extend(hypo.get("probes", []))

    method = experiment.get("method", [])
    activities.extend(method)

    rollbacks = experiment.get("rollbacks", [])
    activities.extend(rollbacks)

    return activities
