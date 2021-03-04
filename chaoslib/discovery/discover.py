# -*- coding: utf-8 -*-
from datetime import datetime
import importlib
import inspect
import platform
from typing import Any
import uuid

from logzero import logger

from chaoslib import __version__
from chaoslib.discovery.package import get_discover_function, install,\
    load_package
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Discovery, DiscoveredActivities


__all__ = ["discover", "discover_activities", "discover_actions",
           "discover_probes", "initialize_discovery_result",
           "portable_type_name", "portable_type_name_to_python_type"]


def discover(package_name: str, discover_system: bool = True,
             download_and_install: bool = True) -> Discovery:
    """
    Discover the capabilities of an extension as well as the system it targets.

    Then apply any post discovery hook that are declared in the chaostoolkit
    settings under the `discovery/post-hook` section.
    """
    if download_and_install:
        install(package_name)
    package = load_package(package_name)
    discover_func = get_discover_function(package)

    return discover_func(discover_system=discover_system)


def initialize_discovery_result(extension_name: str, extension_version: str,
                                discovery_type: str) -> Discovery:
    """
    Intialize the discovery result payload to fill with activities and system
    discovery.
    """
    plt = platform.uname()
    return {
        "chaoslib_version": __version__,
        "id": str(uuid.uuid4()),
        "target": discovery_type,
        "date": "{d}Z".format(d=datetime.utcnow().isoformat()),
        "platform": {
            "system": plt.system,
            "node": plt.node,
            "release": plt.release,
            "version": plt.version,
            "machine": plt.machine,
            "proc": plt.processor,
            "python": platform.python_version()
        },
        "extension": {
            "name": extension_name,
            "version": extension_version,
        },
        "activities": [],
        "system": None
    }


def discover_actions(extension_mod_name: str) -> DiscoveredActivities:
    """
    Discover actions from the given extension named `extension_mod_name`.
    """
    logger.info("Searching for actions in {n}".format(n=extension_mod_name))
    return discover_activities(extension_mod_name, "action")


def discover_probes(extension_mod_name: str) -> DiscoveredActivities:
    """
    Discover probes from the given extension named `extension_mod_name`.
    """
    logger.info("Searching for probes in {n}".format(n=extension_mod_name))
    return discover_activities(extension_mod_name, "probe")


def discover_activities(extension_mod_name: str,  #noqa: C901
                        activity_type: str) -> DiscoveredActivities:
    """
    Discover exported activities from the given extension module name.
    """
    try:
        mod = importlib.import_module(extension_mod_name)
    except ImportError:
        raise DiscoveryFailed(
            "could not import extension module '{m}'".format(
                m=extension_mod_name))

    activities = []
    try:
        exported = getattr(mod, "__all__")
    except AttributeError:
        logger.warning(
            "'{m}' does not expose the __all__ attribute. "
            "It is required to determine what functions are actually "
            "exported as activities.".format(m=extension_mod_name))
        return activities

    funcs = inspect.getmembers(mod, inspect.isfunction)
    for (name, func) in funcs:
        if exported and name not in exported:
            # do not return "private" functions
            continue

        sig = inspect.signature(func)
        activity = {
            "type": activity_type,
            "name": name,
            "mod": mod.__name__,
            "doc": inspect.getdoc(func),
            "arguments": []
        }

        if sig.return_annotation is not inspect.Signature.empty:
            activity["return_type"] = portable_type_name(sig.return_annotation)

        for param in sig.parameters.values():
            if param.kind in (param.KEYWORD_ONLY, param.VAR_KEYWORD):
                continue

            arg = {
                "name": param.name,
            }

            if param.default is not inspect.Parameter.empty:
                arg["default"] = param.default
            if param.annotation is not inspect.Parameter.empty:
                arg["type"] = portable_type_name(param.annotation)
            activity["arguments"].append(arg)

        activities.append(activity)

    return activities


def portable_type_name(python_type: Any) -> str:  # noqa: C901
    """
    Return a fairly portable name for a Python type. The idea is to make it
    easy for consumer to read without caring for actual Python types
    themselves.

    These are not JSON types so don't eval them directly. This function does
    not try to be clever with rich types and will return `"object"` whenever
    it cannot make sense of the provide type.
    """
    if python_type is None:
        return "null"
    elif python_type is bool:
        return "boolean"
    elif python_type is int:
        return "integer"
    elif python_type is float:
        return "number"
    elif python_type is str:
        return "string"
    elif python_type is bytes:
        return "byte"
    elif python_type is set:
        return "set"
    elif python_type is tuple:
        return "tuple"
    elif python_type is list:
        return "list"
    elif python_type is dict:
        return "mapping"
    elif str(python_type).startswith('typing.Dict'):
        return "mapping"
    elif str(python_type).startswith('typing.List'):
        return "list"
    elif str(python_type).startswith('typing.Set'):
        return "set"

    logger.debug(
        "'{}' could not be ported to something meaningful".format(
            str(python_type)))

    return "object"


def portable_type_name_to_python_type(name: str) -> Any:  # noqa: C901
    """
    Return the Python type associated to the given portable name.
    """
    if name == "null":
        return None
    elif name == "boolean":
        return bool
    elif name == "integer":
        return int
    elif name == "number":
        return float
    elif name == "string":
        return str
    elif name == "byte":
        return bytes
    elif name == "set":
        return set
    elif name == "list":
        return list
    elif name == "tuple":
        return tuple
    elif name == "mapping":
        return dict

    return object
