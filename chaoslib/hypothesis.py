# -*- coding: utf-8 -*-
from functools import singledispatch
from typing import Any

from logzero import logger

from chaoslib.activity import ensure_activity_is_valid, execute_activity, \
    run_activity
from chaoslib.exceptions import FailedActivity, InvalidActivity, \
    InvalidExperiment
from chaoslib.types import Configuration, Experiment, Run, Secrets


__all__ = ["ensure_hypothesis_is_valid", "run_steady_state_hypothesis"]


def ensure_hypothesis_is_valid(experiment: Experiment):
    """
    Validates that the steady state hypothesis entry has the expected schema
    or raises :exc:`InvalidExperiment` or :exc:`InvalidProbe`.
    """
    hypo = experiment.get("steady-state-hypothesis")
    if hypo is None:
        return

    if not hypo.get("title"):
        raise InvalidExperiment("hypothesis requires a title")

    probes = hypo.get("probes")
    if probes:
        for probe in probes:
            ensure_activity_is_valid(probe)

            if "tolerance" not in probe:
                raise InvalidActivity(
                    "hypothesis probe must have a tolerance entry")

            if not isinstance(probe["tolerance"], (
                    bool, int, list, str, dict)):
                raise InvalidActivity(
                    "hypothesis probe tolerance must either be an integer, "
                    "a string, a boolean or a pair of values for boundaries. "
                    "It can also be a dictionary which is a probe activity "
                    "definition that takes an argument called `value` with "
                    "the value of the probe itself to be validated")

            if isinstance(probe, dict):
                ensure_activity_is_valid(probe)


def run_steady_state_hypothesis(experiment: Experiment,
                                configuration: Configuration, secrets: Secrets,
                                dry: bool = False):
    """
    Run all probes in the hypothesis and fail the experiment as soon as any of
    the probe fails or is outside the tolerance zone.
    """
    state = {
        "steady_state_met": None,
        "probes": []
    }
    hypo = experiment.get("steady-state-hypothesis")
    if not hypo:
        logger.info(
            "No steady state hypothesis defined. That's ok, just exploring.")
        return

    logger.info("Steady state hypothesis: {h}".format(h=hypo.get("title")))

    probes = hypo.get("probes", [])
    for activity in probes:
        run = execute_activity(
            activity, configuration=configuration, secrets=secrets, dry=dry)
        run["tolerance_met"] = True
        state["probes"].append(run)
        if dry:
            # do not check for tolerance when dry mode is on
            continue

        tolerance = activity.get("tolerance")
        logger.debug("allowed tolerance is {t}".format(t=str(tolerance)))
        if not within_tolerance(tolerance, run["output"]):
            run["tolerance_met"] = False
            state["steady_state_met"] = False
            return state

    state["steady_state_met"] = True
    logger.info("Steady state hypothesis is met!")

    return state


@singledispatch
def within_tolerance(tolerance: Any, value: Any,
                     secrets: Secrets = None) -> bool:
    """
    Performs a quick validation of the probe's result `value` agains the
    `tolerance` that was provided.

    The tolerance is typed and is therefore dispatched to the right function
    at runtime based on the `tolerance` type.

    Note that the `tolerance` maybe a dictionary, in which case it should
    follow the activity provider specification so that it can be called with
    the probe's result `value` as an argument, returning a success when the
    `value` is within range.
    """
    pass


@within_tolerance.register(bool)
def _(tolerance: bool, value: bool, secrets: Secrets = None) -> bool:
    return value == tolerance


@within_tolerance.register(str)
def _(tolerance: str, value: str, secrets: Secrets = None) -> bool:
    return value == tolerance


@within_tolerance.register(int)
def _(tolerance: int, value: int, secrets: Secrets = None) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return value["status"] == tolerance

    return value == tolerance


@within_tolerance.register(list)
def _(tolerance: list, value: Any, secrets: Secrets = None) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return value["status"] in tolerance

    if len(tolerance) == 2:
        return tolerance[0] <= value <= tolerance[1]


@within_tolerance.register(dict)
def _(tolerance: dict, value: Any, secrets: Secrets = None) -> bool:
    tolerance["arguments"]["value"] = value
    run = run_activity(tolerance, secrets)
    return run["status"] == "succeeded"
