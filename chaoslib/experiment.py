# -*- coding: utf-8 -*-
import io
import json

from chaoslib.action import ensure_action_is_valid, run_action
from chaoslib.exceptions import InvalidExperiment
from chaoslib.probe import ensure_probe_is_valid, run_probe
from chaoslib.types import Experiment

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


def run_experiment(experiment: Experiment):
    """
    Run the given `experiment` method step by step, in the following sequence:
    steady probe, action, close probe. 
    """
    method = experiment.get("method")
    for step in method:
        probes = step.get("probes", {})

        steady = probes.get("steady")
        if steady:
            run_probe(steady)

        action = step.get("action")
        if action:
            run_action(action)

        close = probes.get("close")
        if close:
            run_probe(close)
