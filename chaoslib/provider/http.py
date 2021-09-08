from typing import Any

import requests
import urllib3
from logzero import logger

from chaoslib import substitute
from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.types import Activity, Configuration, Secrets

__all__ = ["run_http_activity", "validate_http_activity"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run_http_activity(
    activity: Activity, configuration: Configuration, secrets: Secrets
) -> Any:
    """
    Run a HTTP activity.

    A HTTP activity is a call to a HTTP endpoint and its result is returned as
    the raw result of this activity.

    Raises :exc:`ActivityFailed` when a timeout occurs for the request or when
    the endpoint returns a status in the 400 or 500 ranges.

    This should be considered as a private function.
    """
    provider = activity["provider"]
    url = substitute(provider["url"], configuration, secrets)
    method = provider.get("method", "GET").upper()
    headers = substitute(provider.get("headers", None), configuration, secrets)
    timeout = provider.get("timeout", None)
    arguments = provider.get("arguments", None)
    verify_tls = provider.get("verify_tls", True)
    max_retries = provider.get("max_retries", 0)

    if arguments and (configuration or secrets):
        arguments = substitute(arguments, configuration, secrets)

    if isinstance(timeout, list):
        timeout = tuple(timeout)

    try:
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=max_retries)
        s.mount("http://", a)
        s.mount("https://", a)
        if method == "GET":
            r = s.get(
                url,
                params=arguments,
                headers=headers,
                timeout=timeout,
                verify=verify_tls,
            )
        else:
            if headers and headers.get("Content-Type") == "application/json":
                r = s.request(
                    method,
                    url,
                    json=arguments,
                    headers=headers,
                    timeout=timeout,
                    verify=verify_tls,
                )
            else:
                r = s.request(
                    method,
                    url,
                    data=arguments,
                    headers=headers,
                    timeout=timeout,
                    verify=verify_tls,
                )

        body = None
        if r.headers.get("Content-Type") == "application/json":
            body = r.json()
        else:
            body = r.text

        # kind warning to the user that this HTTP call may be invalid
        # but not during the hypothesis check because that could also be
        # exactly what the user want. This warning is helpful during the
        # method and rollbacks
        if "tolerance" not in activity and r.status_code > 399:
            logger.warning(
                "This HTTP call returned a response with a HTTP status code "
                "above 400. This may indicate some error and not "
                "what you expected. Please have a look at the logs."
            )

        return {"status": r.status_code, "headers": dict(**r.headers), "body": body}
    except requests.exceptions.ConnectionError as cex:
        raise ActivityFailed(f"failed to connect to {url}: {str(cex)}")
    except requests.exceptions.Timeout:
        raise ActivityFailed("activity took too long to complete")


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
