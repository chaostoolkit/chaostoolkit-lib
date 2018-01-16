# -*- coding: utf-8 -*-
from datetime import datetime
import importlib
import inspect
import platform
import uuid

from logzero import logger

from chaoslib import __version__
from chaoslib.discovery.package import get_discover_function, install,\
    load_package
from chaoslib.types import Discovery, DiscoveredActivities


__all__ = ["discover", "discover_activities", "discover_actions",
           "discover_probes", "initialize_discovery_result"]


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
        "type": discovery_type,
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
    logger.info("Searching for actions")
    return discover_activities(extension_mod_name, "action")


def discover_probes(extension_mod_name: str) -> DiscoveredActivities:
    """
    Discover probes from the given extension named `extension_mod_name`.
    """
    logger.info("Searching for probes")
    return discover_activities(extension_mod_name, "probe")


def discover_activities(extension_mod_name: str,
                        activity_type: str) -> DiscoveredActivities:
    """
    Discover exported activities from the given extension module name.
    """
    try:
        mod = importlib.import_module(extension_mod_name)
    except ImportError:
        raise DiscoveryFailed(
            "could not import Python module '{m}'".format(
                m=extension_mod_name))

    activities = []
    exported = getattr(mod, "__all__")
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

        # if sig.return_annotation is not inspect.Signature.empty:
        #     activity["return_type"] = sig.return_annotation

        for param in sig.parameters.values():
            arg = {
                "name": param.name,
            }

            if param.default is not inspect.Parameter.empty:
                arg["default"] = param.default
        #    if param.annotation is not inspect.Parameter.empty:
        #         arg["type"] = param.annotation
            activity["arguments"].append(arg)

        activities.append(activity)

    return activities
