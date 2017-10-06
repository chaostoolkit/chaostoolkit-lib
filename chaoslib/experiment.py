# -*- coding: utf-8 -*-
from datetime import datetime
import io
import json
import platform
import time
import traceback
from typing import Any, Callable

from logzero import logger

from chaoslib import __version__
from chaoslib.action import ensure_action_is_valid, run_action
from chaoslib.exceptions import FailedAction, FailedActivity, FailedProbe,\
    InvalidExperiment
from chaoslib.probe import ensure_probe_is_valid, run_probe
from chaoslib.types import Activity, Experiment, Journal, Run

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

    method = experiment.get("method")
    if not method:
        raise InvalidExperiment("an experiment requires a method with "
                                "at least one activity")

    for step in method:
        if "title" not in step:
            raise InvalidExperiment("an activity step must have a title")

        action = step.get("action")
        if action:
            ensure_action_is_valid(action)

        probes = step.get("probes")
        if probes:
            steady = probes.get("steady")
            if steady:
                ensure_probe_is_valid(steady)

            close = probes.get("close")
            if close:
                ensure_probe_is_valid(close)


def run_experiment(experiment: Experiment) -> Journal:
    """
    Run the given `experiment` method step by step, in the following sequence:
    steady probe, action, close probe.
    """
    logger.info("Running experiment: {t}".format(t=experiment["title"]))

    started_at = time.time()
    journal = {
        "chaoslib-version": __version__,
        "platform": platform.platform(),
        "node": platform.node(),
        "experiment": experiment.copy(),
        "start": datetime.utcnow().isoformat(),
        "run": []
    }

    method = experiment.get("method")
    for step in method:
        probes = step.get("probes", {})

        steady = probes.get("steady")
        if steady:
            run = run_activity(steady, "steady state", func=run_probe)
            journal["run"].append(run)

        action = step.get("action")
        if action:
            run = run_activity(action, "action", func=run_action)
            journal["run"].append(run)

        close = probes.get("close")
        if close:
            run = run_activity(close, "close state", func=run_probe)
            journal["run"].append(run)

    journal["end"] = datetime.utcnow().isoformat()
    journal["duration"] = time.time() - started_at

    logger.info("Experiment is now complete")

    return journal


def run_activity(activity: Activity, kind: str,
                 func: Callable[[Activity], Any]) -> Run:
    logger.info("Observing {n}: {t}".format(n=kind, t=activity["title"]))
    start = datetime.utcnow()

    run = {
        "activity": activity,
        "kind": kind
    }

    try:
        result = func(activity)
        run["status"] = "succeeded"
        run["output"] = result
        logger.info("{n} suceeeded".format(n=kind.title()))
    except FailedActivity as x:
        error_msg = str(x)
        run["status"] = "failed"
        run["output"] = str(x)
        run["exception"] = traceback.format_exception(type(x), x, None)
        logger.error("{n} failed: {x}".format(n=kind.title(), x=error_msg))

    end = datetime.utcnow()
    run["start"] = start.isoformat()
    run["end"] = end.isoformat()
    run["duration"] = (end - start).total_seconds()

    return run
