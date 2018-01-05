# -*- coding: utf-8 -*-
import itertools
import os
import os.path
import shutil
import subprocess
from typing import Any

from logzero import logger

from chaoslib import substitute
from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.types import Activity, Configuration, Secrets


__all__ = ["run_process_activity", "validate_process_activity"]


def run_process_activity(activity: Activity, configuration: Configuration,
                         secrets: Secrets) -> Any:
    """
    Run the a process activity.

    A process activity is an executable the current user is allowed to apply.
    The raw result of that command is returned as bytes of this activity.

    Raises :exc:`FailedActivity` when a the process takes longer than the
    timeout defined in the activity. There is no timeout by default so be
    careful when you do not explicitely provide one.

    This should be considered as a private function.
    """
    provider = activity["provider"]
    timeout = provider.get("timeout", None)
    arguments = provider["arguments"]

    if configuration or secrets:
        arguments = substitute(arguments, configuration, secrets)

    chain = itertools.chain.from_iterable(arguments.items())
    args = list([p for p in chain if p not in (None, "")])
    args.insert(0, shutil.which(provider["path"]))

    try:
        logger.debug("Running: {a}".format(a=" ".join(args)))
        proc = subprocess.run(
            args, timeout=timeout, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=os.environ)
    except subprocess.TimeoutExpired:
        raise FailedActivity("process activity took too long to complete")

    return (
        proc.returncode,
        proc.stdout.decode('utf-8'),
        proc.stderr.decode('utf-8')
    )


def validate_process_activity(activity: Activity):
    """
    Validate a process activity.

    A process activity requires:

    * a `"path"` key which is an absolute path to an executable the current
      user can call

    In all failing cases, raises :exc:`InvalidActivity`.

    This should be considered as a private function.
    """
    name = activity["name"]
    provider = activity["provider"]

    path = provider.get("path")
    if not path:
        raise InvalidActivity("a process activity must have a path")

    path = shutil.which(path)
    if not path:
        raise InvalidActivity(
            "path '{path}' cannot be found, in activity '{name}'".format(
                path=path, name=name))

    if not os.access(path, os.X_OK):
        raise InvalidActivity(
            "no access permission to '{path}', in activity '{name}'".format(
                path=path, name=name))
