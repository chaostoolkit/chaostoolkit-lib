# -*- coding: utf-8 -*-
from copy import deepcopy
import importlib
import inspect
from typing import Callable, List, Union

from logzero import logger

from chaoslib import substitute
from chaoslib.exceptions import InvalidActivity
from chaoslib.types import Activity, Configuration, Control, Experiment, \
    Journal, Run, Secrets, Settings


__all__ = ["apply_python_control", "cleanup_control", "initialize_control",
           "validate_python_control"]
_level_mapping = {
    "experiment-before": "before_experiment_control",
    "experiment-after": "after_experiment_control",
    "hypothesis-before": "before_hypothesis_control",
    "hypothesis-after": "after_hypothesis_control",
    "method-before": "before_method_control",
    "method-after": "after_method_control",
    "rollback-before": "before_rollback_control",
    "rollback-after": "after_rollback_control",
    "activity-before": "before_activity_control",
    "activity-after": "after_activity_control",
}


def initialize_control(control: Control, experiment: Experiment,
                       configuration: Configuration,
                       secrets: Secrets, settings: Settings = None):
    """
    Initialize a control by calling its `configure_control` function.
    """
    func = load_func(control, "configure_control")
    if not func:
        return

    arguments = {}
    sig = inspect.signature(func)

    if "experiment" in sig.parameters:
        arguments["experiment"] = experiment

    if "secrets" in sig.parameters:
        arguments["secrets"] = secrets

    if "configuration" in sig.parameters:
        arguments["configuration"] = configuration

    if "settings" in sig.parameters:
        arguments["settings"] = settings

    func(**arguments)


def cleanup_control(control: Control):
    """
    Cleanup a control by calling its `cleanup_control` function.
    """
    func = load_func(control, "cleanup_control")
    if not func:
        return
    func()


def validate_python_control(control: Control):
    """
    Verify that a control block matches the specification
    """
    name = control["name"]
    provider = control["provider"]
    mod_name = provider.get("module")
    if not mod_name:
        raise InvalidActivity(
            "Control '{}' must have a module path".format(name))

    try:
        importlib.import_module(mod_name)
    except ImportError:
        logger.warning("Could not find Python module '{mod}' "
                       "in control '{name}'. Did you install the Python "
                       "module? The experiment will carry on running "
                       "nonetheless.".format(mod=mod_name, name=name))


def apply_python_control(level: str, control: Control, experiment: Experiment,
                         context: Union[Activity, Experiment],
                         state: Union[Journal, Run, List[Run]] = None,
                         configuration: Configuration = None,
                         secrets: Secrets = None, settings: Settings = None):
    """
    Apply a control by calling a function matching the given level.
    """
    provider = control["provider"]
    func_name = _level_mapping.get(level)
    func = load_func(control, func_name)
    if not func:
        return

    arguments = deepcopy(provider.get("arguments", {}))

    if configuration or secrets:
        arguments = substitute(arguments, configuration, secrets)

    sig = inspect.signature(func)
    if "secrets" in provider and "secrets" in sig.parameters:
        arguments["secrets"] = {}
        for s in provider["secrets"]:
            arguments["secrets"].update(secrets.get(s, {}).copy())

    if "configuration" in sig.parameters:
        arguments["configuration"] = configuration.copy()

    if "state" in sig.parameters:
        arguments["state"] = state

    if "experiment" in sig.parameters:
        arguments["experiment"] = experiment

    if "extensions" in sig.parameters:
        arguments["extensions"] = experiment.get("extensions")

    if "settings" in sig.parameters:
        arguments["settings"] = settings

    func(context=context, **arguments)


###############################################################################
# Internals
###############################################################################
def load_func(control: Control, func_name: str) -> Callable:
    provider = control["provider"]
    mod_path = provider["module"]
    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        logger.debug(
            "Control module '{}' could not be loaded. "
            "Have you installed it?".format(mod_path))
        return
    func = getattr(mod, func_name, None)
    if not func:
        logger.debug(
            "Control module '{}' does not declare '{}'".format(
                mod_path, func_name
            ))
        return

    try:
        logger.debug(
            "Control '{}' loaded from '{}'".format(
                func_name, inspect.getfile(func)))
    except TypeError:
        pass

    return func
