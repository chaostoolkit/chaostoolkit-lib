# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import io
import json
import platform
import time
import traceback
from typing import Any, Callable, Dict, Iterator

from logzero import logger

from chaoslib import __version__
from chaoslib.activity import ensure_activity_is_valid, run_activity
from chaoslib.exceptions import FailedActivity, InvalidActivity, \
    InvalidExperiment
from chaoslib.secret import load_secrets
from chaoslib.types import Action, Activity, Experiment, Journal, Probe, Run, \
    Secrets, Step


__all__ = ["ensure_experiment_is_valid", "run_experiment"]


def load_experiment(path: str) -> Experiment:
    """
    Parse the given experiment from `path` and return it.
    """
    with io.open(path) as f:
        return json.load(f)


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

    ensure_hypothesis_is_valid(experiment)

    method = experiment.get("method")
    if not method:
        raise InvalidExperiment("an experiment requires a method with "
                                "at least one activity")

    for step in method:
        if "name" not in step:
            raise InvalidExperiment("an activity must have a name")

        if "type" not in step:
            raise InvalidExperiment("an activity must have a type")

        if step["type"] not in ("action", "probe"):
            raise InvalidExperiment(
                "only 'action' and 'probe' activities are supported")

        ensure_activity_is_valid(step)


def ensure_hypothesis_is_valid(experiment: Experiment):
    """
    Validates that the steady state hypothesis entry has the expected schema
    or raises :exc:`InvalidExperiment` or :exc:`InvalidProbe`.
    """
    hypo = experiment.get("steady-state-hypothesis")
    if hypo is None:
        raise InvalidExperiment(
            "experiment must declare a steady-state-hypothesis")

    if not hypo.get("title"):
        raise InvalidExperiment("hypothesis requires a title")

    probes = hypo.get("probes")
    if probes:
        for probe in probes:
            ensure_probe_is_valid(probe)

            if "tolerance" not in probe:
                raise InvalidProbe(
                    "hypothesis probe must have a tolerance entry")


def initialize_run_journal(experiment: Experiment) -> Journal:
    return {
        "chaoslib-version": __version__,
        "platform": platform.platform(),
        "node": platform.node(),
        "experiment": experiment.copy(),
        "start": datetime.utcnow().isoformat(),
        "run": []
    }


def get_background_pool(experiment: Experiment) -> ThreadPoolExecutor:
    """
    Create a pool for background activities. The pool is as big as the number
    of declared background activities. If none are declared, returned `None`.
    """
    method = experiment.get("method")

    background_count = 0
    for activity in method:
        if activity and activity.get("background"):
            background_count = background_count + 1

    if background_count:
        logger.debug(
            "{c} activities will be run in the background".format(
                c=background_count))
        return ThreadPoolExecutor(background_count)


def run_experiment(experiment: Experiment) -> Journal:
    """
    Run the given `experiment` method step by step, in the following sequence:
    steady probe, action, close probe.

    Activities can be executed in background when they have the
    `"background"` property set to `true`. In that case, the activity is run in
    a thread. By the end of runs, those threads block until they are all
    complete.

    If the experiment has the `"dry"` property set to `False`, the experiment
    runs without actually executing the activities.
    """
    logger.info("Experiment: {t}".format(t=experiment["title"]))

    dry = experiment.get("dry", False)
    if dry:
        logger.warning("Dry mode enabled")

    started_at = time.time()
    secrets = load_secrets(experiment.get("secrets", {}))
    pool = get_background_pool(experiment)

    journal = initialize_run_journal(experiment)

    runs = list(run_activities(experiment, secrets, pool, dry))

    journal["end"] = datetime.utcnow().isoformat()
    journal["duration"] = time.time() - started_at

    if pool:
        logger.debug("Waiting for background actions to complete...")
        pool.shutdown(wait=True)

    for run in runs:
        if not run:
            continue
        if isinstance(run, dict):
            journal["run"].append(run)
        else:
            journal["run"].append(run.result())

    logger.info("Experiment is now complete")

    return journal


def run_activities(experiment: Experiment, secrets: Secrets,
                   pool: ThreadPoolExecutor,
                   dry: bool = False) -> Iterator[Run]:
    """
    Iternal generator that iterates over all activities and execute them.
    Yields either the result of the run or a :class:`concurrent.futures.Future`
    if the activity was set to run in the `background`.
    """
    method = experiment.get("method")
    for activity in method:
        logger.info("Step: {t}".format(t=activity.get("title")))

        if activity.get("background"):
            logger.debug("activity will run in the background")
            yield pool.submit(execute_activity, activity=activity,
                              secrets=secrets, dry=dry)
        else:
            yield execute_activity(activity, secrets=secrets, dry=dry)


def execute_activity(activity: Activity, secrets: Secrets,
                     dry: bool = False) -> Run:
    """
    Low-level wrapper around the actual activity provider call to collect
    some meta data (like duration, start/end time, exceptions...) during
    the run.
    """
    logger.info("  {n}: {t}".format(
        n=activity["type"].title(), t=activity["name"]))
    start = datetime.utcnow()

    run = {
        "activity": activity.copy(),
        "output": None
    }

    try:
        result = None
        if not dry:
            result = run_activity(activity, secrets)
            run["output"] = result
        run["status"] = "succeeded"
        if result is None:
            logger.info("  => succeeded with '{r}'".format(r=result))
        else:
            logger.info("  => succeeded without any result value")
    except FailedActivity as x:
        error_msg = str(x)
        run["status"] = "failed"
        run["output"] = str(x)
        run["exception"] = traceback.format_exception(type(x), x, None)
        logger.error("   => failed: {x}".format(x=error_msg))

    end = datetime.utcnow()
    run["start"] = start.isoformat()
    run["end"] = end.isoformat()
    run["duration"] = (end - start).total_seconds()

    return run
