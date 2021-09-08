# Builds an in-memory cache of all declared activities so they can be
# referenced from other places in the experiment
import inspect
from functools import wraps
from typing import Any, Dict, List, Union

from logzero import logger

import chaoslib
from chaoslib.types import Activity, Experiment, Schedule, Settings, Strategy

__all__ = ["cache_activities", "clear_cache", "lookup_activity", "with_cache"]


# global objects are frown upon but as we write to it once
# (from a single place) and we only read afterwards, that's likely okay.
_cache = {}


def cache_activities(experiment: Experiment) -> List[Activity]:
    """
    Cache all activities into a map so we can quickly lookup ref.
    """
    logger.debug("Building activity cache...")

    lot = experiment.get("method", []) + experiment.get(
        "steady-state-hypothesis", {}
    ).get("probes", [])

    for activity in lot:
        name = activity.get("name")
        if name:
            _cache[name] = activity

    logger.debug(f"Cached {len(_cache)} activities")


def clear_cache():
    """
    Clear the cache
    """
    logger.debug("Clearing activities cache")
    _cache.clear()


def with_cache(f):
    """
    Ensure the activities cache is populated before calling the wrapped
    function.
    """

    @wraps(f)
    def wrapped(
        experiment: Experiment,
        settings: Settings = None,
        experiment_vars: Dict[str, Any] = None,
        strategy: Strategy = Strategy.DEFAULT,
        schedule: Schedule = None,
        event_handlers: List[chaoslib.run.RunEventHandler] = None,
    ):
        try:
            if experiment:
                cache_activities(experiment)

            sig = inspect.signature(f)
            arguments = {"experiment": experiment}

            if "settings" in sig.parameters:
                arguments["settings"] = settings
            if "experiment_vars" in sig.parameters:
                arguments["experiment_vars"] = experiment_vars
            if "strategy" in sig.parameters:
                arguments["strategy"] = strategy
            if "schedule" in sig.parameters:
                arguments["schedule"] = schedule
            if "event_handlers" in sig.parameters:
                arguments["event_handlers"] = event_handlers
            return f(**arguments)
        finally:
            clear_cache()

    return wrapped


def lookup_activity(ref: str) -> Union[Activity, None]:
    """
    Lookup an activity by name and return it or `None`.
    """
    activity = _cache.get(ref)
    if not activity:
        logger.debug(f"cache miss for '{ref}'")
    return activity
