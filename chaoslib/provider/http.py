# -*- coding: utf-8 -*-
import itertools
import os
import os.path
from typing import Any
import urllib3

from logzero import logger
import requests

from chaoslib import substitute
from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.types import Activity, Configuration, Secrets


__all__ = ["run_http_activity", "validate_http_activity"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    url = substitute(provider["url"], configuration, secrets)
    method = provider.get("method", "GET").upper()
    headers = substitute(provider.get("headers", None), configuration, secrets)
    timeout = provider.get("timeout", None)
    arguments = provider.get("arguments", {})
    verify_tls = provider.get("verify_tls", True)

    if configuration or secrets:
        arguments = substitute(arguments, configuration, secrets)

    try:
        if method == "GET":
            r = requests.get(
                url, params=arguments, headers=headers, timeout=timeout,
                verify=verify_tls)
        else:
            r = requests.request(
                method, url, data=arguments, headers=headers, timeout=timeout,
                verify=verify_tls)

        body = None
        if r.headers.get("Content-Type") == "application/json":
            body = r.json()
        else:
            body = r.text

        return {
            "status": r.status_code,
            "headers": dict(**r.headers),
            "body": body
        }
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
