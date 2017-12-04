# -*- coding: utf-8 -*-
import logging
import numbers
import os
import os.path
import sys
import time
import traceback
from typing import Any

from logzero import logger

from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.provider.http import run_http_activity, validate_http_activity
from chaoslib.provider.native import run_python_activity, \
    validate_python_activity
from chaoslib.provider.proc import run_process_activity, \
    validate_process_activity
from chaoslib.types import Activity, Secrets


__all__ = ["ensure_activity_is_valid", "run_activity"]


def ensure_activity_is_valid(activity: Activity):
    """
    Goes through the activity and checks certain of its properties and raise
    :exc:`InvalidActivity` whenever one does not respect the expectations.

    An activity must at least take the following key:

    * `"type"` the kind of activity, one of `"python"`, `"process"` or `"http"`

    Dependending on the type, an activity requires a variety of other keys.

    In all failing cases, raises :exc:`InvalidActivity`.
    """
    if not activity:
        raise InvalidActivity("empty activity is no activity")

    activity_type = activity.get("type")
    if not activity_type:
        raise InvalidActivity("an activity must have a type")

    if activity_type not in ("probe", "action"):
        raise InvalidActivity(
            "'{t}' is not a supported activity type".format(t=activity_type))

    provider = activity.get("provider")
    if not provider:
        raise InvalidActivity("an activity requires a provider")

    provider_type = provider.get("type")
    if not provider_type:
        raise InvalidActivity("a provider must have a type")

    if provider_type not in ("python", "process", "http"):
        raise InvalidActivity(
            "unknown provider type '{type}'".format(type=provider_type))

    if not activity.get("name"):
        raise InvalidActivity("activity must have a name (cannot be empty)")

    timeout = activity.get("timeout")
    if timeout is not None:
        if not isinstance(timeout, numbers.Number):
            raise InvalidActivity("activity timeout must be a number")

    pauses = activity.get("pauses")
    if pauses is not None:
        before = pauses.get("before")
        if before is not None and not isinstance(before, numbers.Number):
            raise InvalidActivity("activity before pause must be a number")
        after = pauses.get("after")
        if after is not None and not isinstance(after, numbers.Number):
            raise InvalidActivity("activity after pause must be a number")

    if "background" in activity:
        if not isinstance(activity["background"], bool):
            raise InvalidActivity("activity background must be a boolean")

    if provider_type == "python":
        validate_python_activity(activity)
    elif provider_type == "process":
        validate_process_activity(activity)
    elif provider_type == "http":
        validate_http_activity(activity)


def run_activity(activity: Activity, secrets: Secrets) -> Any:
    """
    Run the given activity and return its result. If the activity defines a
    `timeout` this function raises :exc:`FailedActivity`.

    This function assumes the activity is valid as per
    `ensure_layer_activity_is_valid`. Please be careful not to call this
    function without validating its input as this could be a security issue
    or simply fails miserably.
    """
    pauses = activity.get("pauses", {})
    pause_before = pauses.get("before")
    if pause_before:
        logger.info("  Pausing for {d}s...".format(d=pause_before))
        time.sleep(pause_before)

    try:
        provider = activity["provider"]
        activity_type = provider["type"]
        if activity_type == "python":
            result = run_python_activity(activity, secrets)
        elif activity_type == "process":
            result = run_process_activity(activity, secrets)
        elif activity_type == "http":
            result = run_http_activity(activity, secrets)
    except Exception:
        # just make sure we have a full traceback
        logger.debug("Activity failed", exc_info=True)
        raise
    finally:
        pause_after = pauses.get("after")
        if pause_after:
            logger.info("  Pausing for {d}s...".format(d=pause_after))
            time.sleep(pause_after)

    return result
