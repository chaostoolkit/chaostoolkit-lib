# -*- coding: utf-8 -*-
import itertools
import os
import os.path
from typing import Any

from logzero import logger
import requests

from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.types import Activity, Configuration, Secrets


__all__ = ["run_http_activity", "validate_http_activity"]


def run_http_activity(activity: Activity, configuration: Configuration,
                      secrets: Secrets) -> Any:
    """
    Run a HTTP activity.

    A HTTP activity is a call to a HTTP endpoint and its result is returned as
    the raw result of this activity.

    Raises :exc:`FailedActivity` when a timeout occurs for the request or when
    the endpoint returns a status in the 400 or 500 ranges.

    This should be considered as a private function.
    """
    provider = activity["provider"]
    url = provider["url"]
    method = provider.get("method", "GET").upper()
    headers = provider.get("headers", None)
    timeout = provider.get("timeout", None)
    args = provider.get("arguments", {})
    expected_status = provider.get("expected_status", 200)

    try:
        if method == "GET":
            r = requests.get(
                url, params=args, headers=headers, timeout=timeout)
        else:
            r = requests.request(
                method, url, data=args, headers=headers, timeout=timeout)

        if r.status_code != expected_status:
            raise FailedActivity(
                "HTTP call failed with code {s} (expected {c}): {t}".format(
                    s=r.status_code, c=expected_status, t=r.text))

        if r.headers.get("Content-Type") == "application/json":
            return r.json()

        return r.text

    except requests.exceptions.ConnectionError as cex:
        raise FailedActivity("failed to connect to {u}: {x}".format(
            u=url, x=str(cex)))
    except requests.exceptions.Timeout:
        raise FailedActivity("activity took too long to complete")


def validate_http_activity(activity: Activity):
    """
    Validate a HTTP activity.

    A process activity requires:

    * a `"url"` key which is the address to call

    In addition, you can pass the followings:

    * `"method"` which is the HTTP verb to use (default to `"GET"`)
    * `"headers"` which must be a mapping of string to string

    In all failing cases, raises :exc:`InvalidActivity`.

    This should be considered as a private function.
    """
    provider = activity["provider"]
    url = provider.get("url")
    if not url:
        raise InvalidActivity("a HTTP activity must have a URL")

    headers = provider.get("headers")
    if headers and not type(headers) == dict:
        raise InvalidActivity("a HTTP activities expect headers as a mapping")
