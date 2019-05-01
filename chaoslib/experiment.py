# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import platform
import time
from typing import List

from logzero import logger

from chaoslib import __version__
from chaoslib.activity import ensure_activity_is_valid, run_activities
from chaoslib.caching import with_cache, lookup_activity
from chaoslib.control import initialize_controls, controls, cleanup_controls, \
    validate_controls, Control, initialize_global_controls, \
    cleanup_global_controls
from chaoslib.deprecation import warn_about_deprecated_features
from chaoslib.exceptions import ActivityFailed, ChaosException, \
    InterruptExecution, InvalidActivity, InvalidExperiment
from chaoslib.extension import validate_extensions
from chaoslib.configuration import load_configuration
from chaoslib.hypothesis import ensure_hypothesis_is_valid, \
    run_steady_state_hypothesis
from chaoslib.loader import load_experiment
from chaoslib.rollback import run_rollbacks
from chaoslib.secret import load_secrets
from chaoslib.settings import get_loaded_settings
from chaoslib.types import Configuration, Experiment, Journal, Run, Secrets, \
    Settings

initialize_global_controls
__all__ = ["ensure_experiment_is_valid", "run_experiment", "load_experiment"]


@with_cache
def ensure_experiment_is_valid(experiment: Experiment):
    """
    A chaos experiment consists of a method made of activities to carry
    sequentially.

    There are two kinds of activities:

    * probe: detecting the state of a resource in your system or external to it
      There are two kinds of probes: `steady` and `close`
    * action: an operation to apply against your system

    Usually, an experiment is made of a set of `steady` probes that ensure the
    system is sound to carry further the experiment. Then, an action before
    another set of of  ̀close` probes to sense the state of the system
    post-action.

    This function raises :exc:`InvalidExperiment`, :exc:`InvalidProbe` or
    :exc:`InvalidAction` depending on where it fails.
    """
    logger.info("Validating the experiment's syntax")

    if not experiment:
        raise InvalidExperiment("an empty experiment is not an experiment")

    if not experiment.get("title"):
        raise InvalidExperiment("experiment requires a title")

    if not experiment.get("description"):
        raise InvalidExperiment("experiment requires a description")

    tags = experiment.get("tags")
    if tags:
        if list(filter(lambda t: t == '' or not isinstance(t, str), tags)):
            raise InvalidExperiment(
                "experiment tags must be a non-empty string")

    validate_extensions(experiment)

    config = load_configuration(experiment.get("configuration", {}))
    load_secrets(experiment.get("secrets", {}), config)

    ensure_hypothesis_is_valid(experiment)

    method = experiment.get("method")
    if not method:
        raise InvalidExperiment("an experiment requires a method with "
                                "at least one activity")

    for activity in method:
        ensure_activity_is_valid(activity)

        # let's see if a ref is indeed found in the experiment
        ref = activity.get("ref")
        if ref and not lookup_activity(ref):
            raise InvalidActivity("referenced activity '{r}' could not be "
                                  "found in the experiment".format(r=ref))

    rollbacks = experiment.get("rollbacks", [])
    for activity in rollbacks:
        ensure_activity_is_valid(activity)

    warn_about_deprecated_features(experiment)

    validate_controls(experiment)

    logger.info("Experiment looks valid")


def initialize_run_journal(experiment: Experiment) -> Journal:
    return {
        "chaoslib-version": __version__,
        "platform": platform.platform(),
        "node": platform.node(),
        "experiment": experiment.copy(),
        "start": datetime.utcnow().isoformat(),
        "status": None,
        "deviated": False,
        "steady_states": {
            "before": None,
            "after": None
        },
        "run": [],
        "rollbacks": []
    }


def get_background_pools(experiment: Experiment) -> ThreadPoolExecutor:
    """
    Create a pool for background activities. The pool is as big as the number
    of declared background activities. If none are declared, returned `None`.
    """
    method = experiment.get("method")
    rollbacks = experiment.get("rollbacks", [])

    activity_background_count = 0
    for activity in method:
        if activity and activity.get("background"):
            activity_background_count = activity_background_count + 1

    activity_pool = None
    if activity_background_count:
        logger.debug(
            "{c} activities will be run in the background".format(
                c=activity_background_count))
        activity_pool = ThreadPoolExecutor(activity_background_count)

    rollback_background_pool = 0
    for activity in rollbacks:
        if activity and activity.get("background"):
            rollback_background_pool = rollback_background_pool + 1

    rollback_pool = None
    if rollback_background_pool:
        logger.debug(
            "{c} rollbacks will be run in the background".format(
                c=rollback_background_pool))
        rollback_pool = ThreadPoolExecutor(rollback_background_pool)

    return activity_pool, rollback_pool


@with_cache
def run_experiment(experiment: Experiment,
                   settings: Settings = None) -> Journal:
    """
    Run the given `experiment` method step by step, in the following sequence:
    steady probe, action, close probe.

    Activities can be executed in background when they have the
    `"background"` property set to `true`. In that case, the activity is run in
    a thread. By the end of runs, those threads block until they are all
    complete.

    If the experiment has the `"dry"` property set to `False`, the experiment
    runs without actually executing the activities.

    NOTE: Tricky to make a decision whether we should rollback when exiting
    abnormally (Ctrl-C, SIGTERM...). Afterall, there is a chance we actually
    cannot afford to rollback properly. Better bailing to a conservative
    approach. This means we swallow :exc:`KeyboardInterrupt` and
    :exc:`SystemExit` and do not bubble it back up to the caller. We when were
    interrupted, we set the `interrupted` flag of the result accordingly to
    notify the caller this was indeed not terminated properly.
    """
    logger.info("Running experiment: {t}".format(t=experiment["title"]))

    dry = experiment.get("dry", False)
    if dry:
        logger.warning("Dry mode enabled")

    started_at = time.time()
    settings = settings if settings is not None else get_loaded_settings()
    config = load_configuration(experiment.get("configuration", {}))
    secrets = load_secrets(experiment.get("secrets", {}), config)
    initialize_global_controls(experiment, config, secrets, settings)
    initialize_controls(experiment, config, secrets)
    activity_pool, rollback_pool = get_background_pools(experiment)

    control = Control()
    journal = initialize_run_journal(experiment)

    try:
        try:
            control.begin(
                "experiment", experiment, experiment, config, secrets)
            # this may fail the entire experiment right there if any of the
            # probes fail or fall out of their tolerance zone
            try:
                state = run_steady_state_hypothesis(
                    experiment, config, secrets, dry=dry)
                journal["steady_states"]["before"] = state
                if state is not None and not state["steady_state_met"]:
                    p = state["probes"][-1]
                    raise ActivityFailed(
                        "Steady state probe '{p}' is not in the given "
                        "tolerance so failing this experiment".format(
                            p=p["activity"]["name"]))
            except ActivityFailed as a:
                journal["steady_states"]["before"] = state
                journal["status"] = "failed"
                logger.fatal(str(a))
            else:
                try:
                    journal["run"] = apply_activities(
                        experiment, config, secrets, activity_pool, dry)
                except Exception:
                    journal["status"] = "aborted"
                    logger.fatal(
                        "Experiment ran into an un expected fatal error, "
                        "aborting now.", exc_info=True)
                else:
                    try:
                        state = run_steady_state_hypothesis(
                            experiment, config, secrets, dry=dry)
                        journal["steady_states"]["after"] = state
                        if state is not None and not state["steady_state_met"]:
                            journal["deviated"] = True
                            p = state["probes"][-1]
                            raise ActivityFailed(
                                "Steady state probe '{p}' is not in the given "
                                "tolerance so failing this experiment".format(
                                    p=p["activity"]["name"]))
                    except ActivityFailed as a:
                        journal["status"] = "failed"
                        logger.fatal(str(a))
        except InterruptExecution as i:
            journal["status"] = "interrupted"
            logger.fatal(str(i))
        except (KeyboardInterrupt, SystemExit):
            journal["status"] = "interrupted"
            logger.warn("Received an exit signal, "
                        "leaving without applying rollbacks.")
        else:
            journal["status"] = journal["status"] or "completed"
            journal["rollbacks"] = apply_rollbacks(
                experiment, config, secrets, rollback_pool, dry)

        journal["end"] = datetime.utcnow().isoformat()
        journal["duration"] = time.time() - started_at

        has_deviated = journal["deviated"]
        status = "deviated" if has_deviated else journal["status"]

        logger.info(
            "Experiment ended with status: {s}".format(s=status))

        if has_deviated:
            logger.info(
                "The steady-state has deviated, a weakness may have been "
                "discovered")

        control.with_state(journal)

        try:
            control.end("experiment", experiment, experiment, config, secrets)
        except ChaosException:
            logger.debug("Failed to close controls", exc_info=True)

    finally:
        cleanup_controls(experiment)
        cleanup_global_controls()

    return journal


def apply_activities(experiment: Experiment, configuration: Configuration,
                     secrets: Secrets, pool: ThreadPoolExecutor,
                     dry: bool = False) -> List[Run]:
    with controls(level="method", experiment=experiment, context=experiment,
                  configuration=configuration, secrets=secrets) as control:
        runs = list(
            run_activities(experiment, configuration, secrets, pool, dry))

        if pool:
            logger.debug("Waiting for background activities to complete...")
            pool.shutdown(wait=True)

        result = []
        for run in runs:
            if not run:
                continue
            if isinstance(run, dict):
                result.append(run)
            else:
                result.append(run.result())

        control.with_state(result)

    return result


def apply_rollbacks(experiment: Experiment, configuration: Configuration,
                    secrets: Secrets, pool: ThreadPoolExecutor,
                    dry: bool = False) -> List[Run]:
    logger.info("Let's rollback...")
    with controls(level="rollback", experiment=experiment, context=experiment,
                  configuration=configuration, secrets=secrets) as control:
        rollbacks = list(
            run_rollbacks(experiment, configuration, secrets, pool, dry))

        if pool:
            logger.debug("Waiting for background rollbacks to complete...")
            pool.shutdown(wait=True)

        result = []
        for rollback in rollbacks:
            if not rollback:
                continue
            if isinstance(rollback, dict):
                result.append(rollback)
            else:
                result.append(rollback.result())

        control.with_state(result)

    return result
