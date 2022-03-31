from contextlib import contextmanager
from copy import copy, deepcopy
from typing import List, Union

from logzero import logger

from chaoslib.control.python import (
    apply_python_control,
    cleanup_control,
    import_control,
    initialize_control,
    validate_python_control,
)
from chaoslib.exceptions import InterruptExecution, InvalidControl
from chaoslib.settings import get_loaded_settings
from chaoslib.types import Activity, Configuration
from chaoslib.types import Control as ControlType
from chaoslib.types import Experiment, Hypothesis, Journal, Run, Secrets, Settings

__all__ = [
    "controls",
    "initialize_controls",
    "cleanup_controls",
    "validate_controls",
    "Control",
    "initialize_global_controls",
    "cleanup_global_controls",
    "load_global_controls",
]

# Should this be protected in some fashion? chaoslib isn't meant to be used
# concurrently so there is little promise we can support several instances
# at once. When the day comes...
global_controls = []


def initialize_controls(
    experiment: Experiment,
    configuration: Configuration = None,
    secrets: Secrets = None,
    event_registry: "EventHandlerRegistry" = None,  # noqa: F821
):
    """
    Initialize all declared controls in the experiment.

    On Python controls, this means calling the `configure_control` function
    of the exposed module.

    Controls are initialized once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Initializing controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug(f"Initializing control '{name}'")

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            try:
                initialize_control(
                    control,
                    experiment,
                    configuration,
                    secrets,
                    event_registry=event_registry,
                )
            except Exception:
                logger.debug(
                    "Control initialization '{}' failed. "
                    "It will not be registered.".format(control["name"]),
                    exc_info=True,
                )


def cleanup_controls(experiment: Experiment):
    """
    Cleanup all declared controls in the experiment.

    On Python controls, this means calling the `cleanup_control` function
    of the exposed module.

    Controls are cleaned up once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Cleaning up controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug(f"Cleaning up control '{name}'")

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            cleanup_control(control)


def validate_controls(experiment: Experiment):
    """
    Validate that all declared controls respect the specification.

    Raises :exc:`chaoslib.exceptions.InvalidControl` when they are not valid.
    """
    controls = get_controls(experiment)
    references = [
        c["name"] for c in get_controls(experiment) if "ref" not in c and "name" in c
    ]
    for c in controls:
        if "ref" in c:
            if c["ref"] not in references:
                raise InvalidControl(
                    "Control reference '{}' declaration cannot be found"
                )

        if "name" not in c:
            raise InvalidControl("A control must have a `name` property")

        name = c["name"]
        if "provider" not in c:
            raise InvalidControl(f"Control '{name}' must have a `provider` property")

        scope = c.get("scope")
        if scope and scope not in ("before", "after"):
            raise InvalidControl(
                "Control '{}' scope property must be 'before' or "
                "'after' only".format(name)
            )

        provider_type = c.get("provider", {}).get("type")
        if provider_type == "python":
            validate_python_control(c)


def initialize_global_controls(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    settings: Settings,
    event_registry: "EventHandlerRegistry" = None,  # noqa: F821
):
    """
    Load and initialize controls declared in the settings.

    Notice, if a control fails during its initialization, it is deregistered
    and will not be applied throughout the experiment.
    """
    controls = get_global_controls()[:]
    for control in get_global_controls():
        name = control["name"]
        logger.debug(f"Initializing global control '{name}'")

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            try:
                initialize_control(
                    control,
                    experiment=experiment,
                    configuration=configuration,
                    secrets=secrets,
                    settings=settings,
                    event_registry=event_registry,
                )
            except Exception:
                logger.debug(
                    "Control initialization '{}' failed. "
                    "It will not be registered.".format(control["name"]),
                    exc_info=True,
                )
                controls.remove(control)
    set_global_controls(controls)


def load_global_controls(settings: Settings):
    """
    Import all controls declared in the settings and global to all experiments.

    This is called as early as possible, even before we loaded the experiment
    so the loaders controls have a chance to be applied. It does not perform
    any specific initialization yet, it only tries to load the controls
    declared in the settings.
    """
    controls = []
    for name, control in settings.get("controls", {}).items():
        control["name"] = name
        logger.debug(f"Loading global control '{name}'")

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            mod = import_control(control)
            if not mod:
                continue

        controls.append(control)
    set_global_controls(controls)


def cleanup_global_controls():
    """
    Unload and cleanup global controls
    """
    controls = get_global_controls()
    reset_global_controls()

    for control in controls:
        name = control["name"]
        logger.debug(f"Cleaning up global control '{name}'")

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            try:
                cleanup_control(control)
            except Exception:
                logger.debug(
                    "Control cleanup '{}' failed".format(control["name"]), exc_info=True
                )


def get_global_controls() -> List[ControlType]:
    """
    All the controls loaded from the settings.
    """
    return global_controls[:]


class Control:
    def begin(
        self,
        level: str,
        experiment: Experiment,
        context: Union[Activity, Hypothesis, Experiment],
        configuration: Configuration = None,
        secrets: Secrets = None,
    ):
        self.state = None
        apply_controls(
            level=level,
            experiment=experiment,
            context=context,
            scope="before",
            configuration=configuration,
            secrets=secrets,
        )

    def with_state(self, state):
        self.state = state

    def end(
        self,
        level: str,
        experiment: Experiment,
        context: Union[Activity, Hypothesis, Experiment],
        configuration: Configuration = None,
        secrets: Secrets = None,
    ):
        state = self.state
        apply_controls(
            level=level,
            experiment=experiment,
            context=context,
            scope="after",
            state=state,
            configuration=configuration,
            secrets=secrets,
        )
        self.state = None


@contextmanager
def controls(
    level: str,
    experiment: Experiment = None,
    context: Union[Activity, Hypothesis, Experiment, str] = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
):
    """
    Context manager for a block that needs to be wrapped by controls.
    """
    try:
        c = Control()
        c.begin(level, experiment, context, configuration, secrets)
        yield c
    finally:
        c.end(level, experiment, context, configuration, secrets)


###############################################################################
# Internals
###############################################################################
def get_all_activities(experiment: Experiment) -> List[Activity]:
    activities = []
    activities.extend(experiment.get("steady-state-hypothesis", {}).get("probes", []))
    activities.extend(experiment.get("method", []))
    activities.extend(experiment.get("rollbacks", []))
    return activities


def get_controls(experiment: Experiment) -> List[Control]:
    controls = []
    controls.extend(experiment.get("controls", []))
    controls.extend(experiment.get("steady-state-hypothesis", {}).get("controls", []))

    for activity in get_all_activities(experiment):
        controls.extend(activity.get("controls", []))
    return controls


def set_global_controls(controls: List[ControlType]):
    """
    Set the controls loaded from the settings.
    """
    global_controls.clear()
    global_controls.extend(controls)


def reset_global_controls():
    """
    Invalidate all loaded global controls.
    """
    global_controls.clear()


def get_context_controls(
    level: str,
    experiment: Experiment = None,  # noqa: C901
    context: Union[Activity, Experiment] = None,
) -> List[Control]:
    """
    Get the controls at the given level by merging those declared at the
    experiment level with the current's context.

    If a control is declared at the current level, do override it with an
    top-level ine.
    """
    glbl_controls = get_global_controls()
    if not experiment:
        return glbl_controls

    top_level_controls = experiment.get("controls", [])
    controls = copy(context.get("controls", []))
    controls.extend(glbl_controls)

    # do we even have something at the top level to be merged?
    if not top_level_controls:
        return controls

    if not controls:
        return [deepcopy(c) for c in top_level_controls if c.get("automatic", True)]

    if level in ["method", "rollback"]:
        return [deepcopy(c) for c in top_level_controls if c.get("automatic", True)]

    for c in controls[:]:
        if "ref" in c:
            for top_level_control in top_level_controls:
                if c["ref"] == top_level_control["name"]:
                    controls.append(deepcopy(top_level_control))
                    break
        else:
            for tc in reversed(top_level_controls):
                if c.get("name") == tc.get("name"):
                    continue
                if (level != "experiment") and tc.get("automatic", True):
                    controls.insert(0, deepcopy(tc))

    return controls


def apply_controls(
    level: str,
    experiment: Experiment,
    context: Union[Activity, Hypothesis, Experiment],
    scope: str,
    state: Union[Journal, Run, List[Run]] = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
):
    """
    Apply the controls at given level

    The ̀ level` parameter is one of `"experiment", "hypothesis", "method",
    "rollback", "activity"` or `"loader"`. The `context` is usually an
    experiment except at the `"activity"` when it must be an activity. The
    `scope` is one of `"before", "after"` and the `state` is only set on
    `"after"` scope.
    """
    settings = get_loaded_settings() or None
    controls = get_context_controls(level, experiment, context)
    if not controls:
        logger.debug(f"No controls to apply on '{level}'")
        return

    for control in controls:
        control_name = control.get("name")
        target_scope = control.get("scope")

        if target_scope and target_scope != scope:
            continue

        logger.debug(f"Applying {scope}-control '{control_name}' on '{level}'")
        provider = control.get("provider", {})
        provider_type = provider.get("type")

        try:
            if provider_type == "python":
                apply_python_control(
                    level=f"{level}-{scope}",
                    control=control,
                    context=context,
                    state=state,
                    experiment=experiment,
                    configuration=configuration,
                    secrets=secrets,
                    settings=settings,
                )
        except InterruptExecution:
            logger.debug(
                "{}-control '{}' interrupted the execution".format(
                    scope.title(), control_name
                ),
                exc_info=True,
            )
            raise
        except Exception:
            logger.debug(
                f"{scope.title()}-control '{control_name}' failed",
                exc_info=True,
            )
