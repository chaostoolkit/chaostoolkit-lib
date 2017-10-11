# -*- coding: utf-8 -*-
import importlib
import inspect
import itertools
import numbers
import os
import os.path
import subprocess
import sys
import traceback
from typing import Any

import requests

from chaoslib.exceptions import FailedActivity, InvalidActivity
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

    if not activity.get("type"):
        raise InvalidActivity("a activity must have a type")

    activity_type = activity["type"]
    if activity_type not in ("python", "process", "http"):
        raise InvalidActivity(
            "unknown activity type '{type}'".format(type=activity_type))

    if not activity.get("layer"):
        raise InvalidActivity("activity must have a target layer")

    if not activity.get("title"):
        raise InvalidActivity("activity must have a title (cannot be empty)")

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

    if activity_type == "python":
        validate_python_activity(activity)
    elif activity_type == "process":
        validate_process_activity(activity)
    elif activity_type == "http":
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
    activity_type = activity["type"]
    if activity_type == "python":
        return run_python_activity(activity, secrets)
    elif activity_type == "process":
        return run_process_activity(activity, secrets)
    elif activity_type == "http":
        return run_http_activity(activity, secrets)


###############################################################################
# Internal functions
###############################################################################


def run_python_activity(activity: Activity, secrets: Secrets) -> Any:
    """
    Run a Python activity.

    A python activity is a function from any importable module. The result
    of that function is returned as the activity's output.

    This should be considered as a private function.
    """
    mod_path = activity["module"]
    func_name = activity["func"]
    mod = importlib.import_module(mod_path)
    func = getattr(mod, func_name)
    arguments = activity.get("arguments", {}).copy()

    if "secrets" in activity:
        arguments["secrets"] = secrets.get(activity["secrets"]).copy()

    try:
        return func(**arguments)
    except Exception as x:
        title = activity["title"]
        raise FailedActivity(
            traceback.format_exception_only(
                type(x), x)[0].strip()).with_traceback(
                    sys.exc_info()[2])


def run_process_activity(activity: Activity, secrets: Secrets) -> Any:
    """
    Run the a process activity.

    A process activity is an executable the current user is allowed to apply.
    The raw result of that command is returned as bytes of this activity.

    Raises :exc:`FailedActivity` when a the process takes longer than the
    timeout defined in the activity. There is no timeout by default so be
    careful when you do not explicitely provide one.

    This should be considered as a private function.
    """
    timeout = activity.get("timeout", None)
    args = list(itertools.chain.from_iterable(activity["arguments"].items()))
    if "" in args:
        args.remove("")
    if None in args:
        args.remove(None)
    args.insert(0, activity["path"])

    try:
        proc = subprocess.run(
            args, timeout=timeout, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        raise FailedActivity("activity took too long to complete")

    return proc.stdout


def run_http_activity(activity: Activity, secrets: Secrets) -> Any:
    """
    Run a HTTP activity.

    A HTTP activity is a call to a HTTP endpoint and its result is returned as
    the raw result of this activity.

    Raises :exc:`FailedActivity` when a timeout occurs for the request or when
    the endpoint returns a status in the 400 or 500 ranges.

    This should be considered as a private function.
    """
    url = activity["url"]
    method = activity.get("method", "GET").upper()
    headers = activity.get("headers", None)
    timeout = activity.get("timeout", None)
    args = activity.get("arguments", {})

    try:
        if method == "GET":
            r = requests.get(
                url, params=args, headers=headers, timeout=timeout)
        else:
            r = requests.request(
                method, url, data=args, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        raise FailedActivity("activity took too long to complete")

    if r.status_code > 399:
        raise FailedActivity(r.text)

    if r.headers.get("Content-Type") == "application/json":
        return r.json()

    return r.text


def validate_python_activity(activity: Activity):
    """
    Validate a Python activity.

    A Python activity requires:

    * a `"module"` key which is an absolute Python dotted path for a Python
      module this process can import
    * a `func"` key which is the name of a function in that module

    The `"arguments"` activity key must match the function's signature.

    In all failing cases, raises :exc:`InvalidActivity`.

    This should be considered as a private function.
    """
    title = activity["title"]
    mod_name = activity.get("module")
    if not mod_name:
        raise InvalidActivity("a Python activity must have a module path")

    func = activity.get("func")
    if not func:
        raise InvalidActivity("a Python activity must have a function name")

    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        raise InvalidActivity("could not find Python module '{mod}' "
                              "in activity '{title}'".format(
                                  mod=mod_name, title=title))

    found_func = False
    arguments = activity.get("arguments", {})
    needs_secrets = "secrets" in activity
    candidates = set(
        inspect.getmembers(mod, inspect.isfunction)).union(
            inspect.getmembers(mod, inspect.isbuiltin))
    for (name, cb) in candidates:
        if name == func:
            found_func = True

            # let's try to bind the activity's arguments with the function
            # signature see if they match
            sig = inspect.signature(cb)
            try:
                # secrets are provided through a `secrets` parameter to an
                # activity that needs them. However, they are declared out of
                # band of the `arguments` mapping. Here, we simply ensure the
                # signature of the activity is valid by injecting a fake
                # `secrets` argument into the mapping.
                args = arguments.copy()
                if needs_secrets:
                    args["secrets"] = None

                sig.bind(**args)
            except TypeError as x:
                # I dislike this sort of lookup but not sure we can
                # differentiate them otherwise
                msg = str(x)
                if "missing" in msg:
                    arg = msg.rsplit(":", 1)[1].strip()
                    raise InvalidActivity(
                        "required argument {name} is missing from "
                        "activity '{title}'".format(name=arg, title=title))
                elif "unexpected" in msg:
                    arg = msg.rsplit(" ", 1)[1].strip()
                    raise InvalidActivity(
                        "argument {name} is not part of the "
                        "function signature in activity '{title}'".format(
                            name=arg, title=title))
                else:
                    # another error? let's fail fast
                    raise
            break

    if not found_func:
        raise InvalidActivity(
            "'{mod}' does not expose '{func}' in activity '{title}'".format(
                mod=mod_name, func=func, title=title))


def validate_process_activity(activity: Activity):
    """
    Validate a process activity.

    A process activity requires:

    * a `"path"` key which is an absolute path to an executable the current
      user can call

    In all failing cases, raises :exc:`InvalidActivity`.

    This should be considered as a private function.
    """
    title = activity["title"]
    path = activity.get("path")
    if not path:
        raise InvalidActivity("a process activity must have a path")

    if not os.path.isfile(path):
        raise InvalidActivity(
            "'{path}' cannot be found in activity '{title}'".format(
                path=path, title=title))

    if not os.access(path, os.X_OK):
        raise InvalidActivity(
            "no access permission to '{path}' in activity '{title}'".format(
                path=path, title=title))


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
    url = activity.get("url")
    if not url:
        raise InvalidActivity("a HTTP activity must have a URL")

    headers = activity.get("headers")
    if headers and not type(headers) == dict:
        raise InvalidActivity("a HTTP activities expect headers as a mapping")
