# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from logzero import logger

from chaoslib.activity import ensure_activity_is_valid
from chaoslib.caching import with_cache, lookup_activity
from chaoslib.control import validate_controls
from chaoslib.deprecation import warn_about_deprecated_features, \
    warn_about_moved_function
from chaoslib.exceptions import InvalidActivity, InvalidExperiment
from chaoslib.extension import validate_extensions
from chaoslib.configuration import load_configuration
from chaoslib.hypothesis import ensure_hypothesis_is_valid
from chaoslib.loader import load_experiment
from chaoslib.run import Runner, RunEventHandler, \
    initialize_run_journal as init_journal, apply_activities as apply_act, \
    apply_rollbacks as apply_roll
from chaoslib.secret import load_secrets
from chaoslib.types import Configuration, Experiment, Journal, Run, \
    Schedule, Secrets, Settings, Strategy

__all__ = ["ensure_experiment_is_valid", "load_experiment"]


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
    if method is None:
        # we force the method key to be indicated, to make it clear
        # that the SSH will still be executed before & after the method block
        raise InvalidExperiment(
            "an experiment requires a method, "
            "which can be empty for only checking steady state hypothesis ")

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


@with_cache
def run_experiment(experiment: Experiment, settings: Settings = None,
                   experiment_vars: Dict[str, Any] = None,
                   strategy: Strategy = Strategy.DEFAULT,
                   schedule: Schedule = None,
                   event_handlers: List[RunEventHandler] = None) -> Journal:
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
    with Runner(strategy, schedule) as runner:
        if event_handlers:
            for h in event_handlers:
                runner.register_event_handler(h)
        return runner.run(
            experiment, settings, experiment_vars=experiment_vars)


def initialize_run_journal(experiment: Experiment) -> Journal:
    warn_about_moved_function(
        "The 'initialize_run_journal' function has now moved to the "
        "'chaoslib.run' package")
    return init_journal(experiment)


def apply_activities(experiment: Experiment, configuration: Configuration,
                     secrets: Secrets, pool: ThreadPoolExecutor,
                     journal: Journal, dry: bool = False) -> List[Run]:
    warn_about_moved_function(
        "The 'apply_activities' function has now moved to the "
        "'chaoslib.run' package")
    return apply_act(
        experiment, configuration, secrets, pool, journal, dry)


def apply_rollbacks(experiment: Experiment, configuration: Configuration,
                    secrets: Secrets, pool: ThreadPoolExecutor,
                    dry: bool = False) -> List[Run]:
    warn_about_moved_function(
        "The 'apply_rollbacks' function has now moved to the "
        "'chaoslib.run' package")
    return apply_roll(
        experiment, configuration, secrets, pool, dry)
