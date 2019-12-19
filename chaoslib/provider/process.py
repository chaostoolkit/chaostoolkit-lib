# -*- coding: utf-8 -*-
import itertools
import os
import os.path
import shutil
import subprocess
from typing import Any, List

from logzero import logger

from chaoslib import decode_bytes, substitute
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Activity, Configuration, Secrets, ValidationError
from chaoslib.validation import Validation


__all__ = ["run_process_activity", "validate_process_activity"]


def run_process_activity(activity: Activity, configuration: Configuration,
                         secrets: Secrets) -> Any:
    """
    Run the a process activity.

    A process activity is an executable the current user is allowed to apply.
    The raw result of that command is returned as bytes of this activity.

    Raises :exc:`ActivityFailed` when a the process takes longer than the
    timeout defined in the activity. There is no timeout by default so be
    careful when you do not explicitly provide one.

    This should be considered as a private function.
    """
    provider = activity["provider"]
    timeout = provider.get("timeout", None)
    arguments = provider.get("arguments", [])

    if arguments and (configuration or secrets):
        arguments = substitute(arguments, configuration, secrets)

    shell = False
    path = shutil.which(provider["path"])
    if isinstance(arguments, str):
        shell = True
        arguments = "{} {}".format(path, arguments)
    else:
        if isinstance(arguments, dict):
            arguments = itertools.chain.from_iterable(arguments.items())

        arguments = list([str(p) for p in arguments if p not in (None, "")])
        arguments.insert(0, path)

    try:
        logger.debug("Running: {a}".format(a=str(arguments)))
        proc = subprocess.run(
            arguments, timeout=timeout, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=os.environ, shell=shell)
    except subprocess.TimeoutExpired:
        raise ActivityFailed("process activity took too long to complete")

    stdout = decode_bytes(proc.stdout)
    stderr = decode_bytes(proc.stderr)

    return {
        "status": proc.returncode,
        "stdout": stdout,
        "stderr": stderr
    }


def validate_process_activity(activity: Activity) -> List[ValidationError]:
    """
    Validate a process activity.

    A process activity requires:

    * a `"path"` key which is an absolute path to an executable the current
      user can call

    In all failing cases, returns a list of errors.

    This should be considered as a private function.
    """
    v = Validation()

    name = activity.get("name")
    provider = activity.get("provider")

    path = rawpath = provider.get("path")
    if not path:
        v.add_error("path", "a process activity must have a path".
                    format(name=name))
        return v.errors()

    path = shutil.which(path)
    if not path:
        v.add_error(
            "path",
            "path '{path}' cannot be found, in activity '{name}'".format(
                path=rawpath, name=name),
            value=rawpath)
        return v.errors()

    if not os.access(path, os.X_OK):
        v.add_error(
            "path"
            "no access permission to '{path}', in activity '{name}'".format(
                path=rawpath, name=name),
            value=rawpath)

    return v.errors()
