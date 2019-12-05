# -*- coding: utf-8 -*-
import importlib
import inspect
import subprocess
from typing import List

from logzero import logger
import pkg_resources

from chaoslib.exceptions import DiscoveryFailed

__all__ = ["get_discover_function", "install", "load_package",
           "get_top_level_packages"]


def install(package_name: str):
    """
    Use pip to download and install the `package_name` to the current Python
    environment. Pip can detect it is already installed.
    """
    logger.info("Attempting to download and install package '{p}'".format(
        p=package_name))

    process = subprocess.run(
        ["pip", "install", "-U", package_name], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout = process.stdout.decode('utf-8')
    stderr = process.stderr.decode('utf-8')
    logger.debug(stdout)

    if process.returncode != 0:
        msg = "failed to install `{p}`".format(p=package_name)
        logger.debug(
            msg + "\n=================\n{o}\n=================\n{e}\n".format(
                o=stdout, e=stderr))
        raise DiscoveryFailed(msg)

    logger.info("Package downloaded and installed in current environment")


def load_package(package_name: str) -> object:
    """
    Import the module into the current process state.
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        raise DiscoveryFailed(
            "could not load Python module '{name}'".format(name=package_name))

    return package


def get_top_level_packages(package_name: str) -> List[str]:
    """
    Returns the list of top_level importable packages available
    for an installed `package_name` distribution
    """
    return get_importnames_from_package(package_name)


def get_discover_function(package: object):
    """
    Lookup the `discover` function from the given imported package.
    """
    funcs = inspect.getmembers(package, inspect.isfunction)
    for (name, value) in funcs:
        if name == 'discover':
            return value

    raise DiscoveryFailed(
        "package '{name}' does not export a `discover` function".format(
            name=package.__name__))


###############################################################################
# Private functions
###############################################################################
def get_importnames_from_package(package_name: str) -> List[str]:
    """
    Try to fetch the name of the top-level import name for the given
    package. For some reason, this isn't straightforward.

    We support the case for a setup package (distribution) that contains
    multiple top level packages embedded.
    """
    reqs = list(pkg_resources.parse_requirements(package_name))
    if not reqs:
        raise DiscoveryFailed(
            "no requirements met for package '{p}'".format(p=package_name))

    req = reqs[0]
    dist = pkg_resources.get_distribution(req)
    try:
        names = [
            name.strip() for name in
            dist.get_metadata('top_level.txt').split("\n")
            if name != ''
        ]
    except FileNotFoundError:
        raise DiscoveryFailed(
            "failed to load package '{p}' metadata. "
            "Was the package installed properly?".format(p=package_name))

    return names
