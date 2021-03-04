# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from enum import Enum
import importlib
import inspect
from typing import Any, Dict

from logzero import logger
import requests

from chaoslib.types import EventPayload, Settings

__all__ = ["DiscoverFlowEvent", "InitFlowEvent", "RunFlowEvent",
           "ValidateFlowEvent", "notify"]


class FlowEvent(Enum):
    pass


class DiscoverFlowEvent(FlowEvent):
    DiscoverStarted = "discovery-started"
    DiscoverFailed = "discovery-failed"
    DiscoverCompleted = "discovery-completed"


class InitFlowEvent(FlowEvent):
    InitStarted = "init-started"
    InitFailed = "init-failed"
    InitCompleted = "init-completed"


class RunFlowEvent(FlowEvent):
    RunStarted = "run-started"
    RunFailed = "run-failed"
    RunCompleted = "run-completed"
    RunDeviated = "run-deviated"


class ValidateFlowEvent(FlowEvent):
    ValidateStarted = "validate-started"
    ValidateFailed = "validate-failed"
    ValidateCompleted = "validate-completed"


def notify(settings: Settings, event: FlowEvent, payload: Any = None,  #noqa: C901
           error: Any = None):
    """
    Go through all the notification channels declared in the settings and
    call them one by one. Only call those matching the current event.

    As this function is blocking, make sure none of your channels take too
    long to run.

    Whenever an error happened in the notification, a debug message is logged
    into the chaostoolkit log for review but this should not impact the
    experiment itself.

    When no settings were provided, no notifications are sent. Equally, if the
    settings do not define a `notifications` entry. Here is an example of
    settings:

    ```yaml
    notifications:
      -
        type: plugin
        module: somepackage.somemodule
        events:
          - init-failed
          - run-failed
      -
        type: http
        url: http://example.com
        headers:
          Authorization: "Bearer token"
      -
        type: http
        url: https://private.com
        verify_tls: false
        forward_event_payload: false
        headers:
          Authorization: "Bearer token"
        events:
          - discovery-completed
          - run-failed
    ```

    In this sample, the first channel will be the `notify` function of the
    `somepackage.somemopdule` Python module. The other two notifications will
    be sent over HTTP with the third one not forwarding the event payload
    itself (hence being a GET rather than a POST).

    Notice how the first and third channels take an `events` sequence. That
    list represents the events which those endpoints are interested in. In
    other words, they will only be called for those specific events. The second
    channel will be applied to all events.

    The payload event is a dictionary made of the following entries:

    - `"event"`: the event name
    - `"payload"`: the payload associated to this event (may be None)
    - `"phase"`: which phase this event was raised from
    - `"error"`: if an error was passed on to the function
    - `"ts"`: a UTC timestamp of when the event was raised
    """
    if not settings:
        return

    notification_channels = settings.get("notifications")
    if not notification_channels:
        return

    event_payload = {
        "name": event.value,
        "payload": payload,
        "phase": "unknown",
        "ts": datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()
    }

    if error:
        event_payload["error"] = error

    event_class = event.__class__
    if event_class is DiscoverFlowEvent:
        event_payload["phase"] = "discovery"
    elif event_class is InitFlowEvent:
        event_payload["phase"] = "init"
    elif event_class is RunFlowEvent:
        event_payload["phase"] = "run"
    elif event_class is ValidateFlowEvent:
        event_payload["phase"] = "validate"

    for channel in notification_channels:
        events = channel.get("events")
        if events and event.value not in events:
            continue

        channel_type = channel.get("type")
        if channel_type == "http":
            notify_with_http(channel, event_payload)
        elif channel_type == "plugin":
            notify_via_plugin(channel, event_payload)


def notify_with_http(channel: Dict[str, str], payload: EventPayload):
    """
    Call a notification endpoint over HTTP.

    The `channel` dictionary should contain at least the `url` of the endpoint.
    In addition, it may define extra `headers` and turn off TLS verification
    (useful against local endpoint with self-signed certificates).

    You may also set `forward_event_payload` to send a GET request instead of
    the default POST. In that case, the event payload will not be forwarded
    along.
    """
    url = channel.get("url")
    headers = channel.get("headers")
    verify_tls = channel.get("verify_tls", True)
    forward_event_payload = channel.get("forward_event_payload", True)

    if url:
        try:
            if forward_event_payload:
                r = requests.post(
                    url, headers=headers, verify=verify_tls, timeout=(2, 5),
                    json=payload)
            else:
                r = requests.get(
                    url, headers=headers, verify=verify_tls, timeout=(2, 5))

            if r.status_code > 399:
                logger.debug(
                    "Notification sent to '{u}' failed with '{t}'".format(
                        u=url, t=r.text))
        except requests.exceptions.RequestException as err:
            logger.debug(
                "failed calling notification endpoint", exc_info=err)
    else:
        logger.debug("missing url in notification channel")


def notify_via_plugin(channel: Dict[str, str], payload: EventPayload):
    """
    Call a notification plugin as a Python function.

    The `channel` dictionary contains at least the `module` key of the package
    containing the function to be called. The function name defaults to
    `notify` but can be set via the `func` key of the dictionary.

    The function signature must take two positional arguments, a dict from the
    settings for that particular channel and the event payload.
    """
    mod_name = channel.get("module")
    func_name = channel.get("func", "notify")

    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        logger.debug("could not find Python plugin '{mod}' "
                     "for notification".format(mod=mod_name))
    else:
        funcs = inspect.getmembers(mod, inspect.isfunction)
        for (name, f) in funcs:
            if name == func_name:
                try:
                    f(channel, payload)
                except Exception as err:
                    logger.debug(
                        "failed calling notification plugin", exc_info=err)
                break
        else:
            logger.debug("could not find function '{f}' in plugin '{mod}' "
                         "for notification".format(mod=mod_name, f=func_name))
