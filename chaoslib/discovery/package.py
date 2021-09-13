import importlib
import inspect
import subprocess

from logzero import logger

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

from chaoslib.exceptions import DiscoveryFailed

__all__ = ["get_discover_function", "install", "load_package"]


def install(package_name: str):
    """
    Use pip to download and install the `package_name` to the current Python
    environment. Pip can detect it is already installed.
    """
    logger.info(f"Attempting to download and install package '{package_name}'")

    process = subprocess.run(
        ["pip", "install", "-U", package_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout = process.stdout.decode("utf-8")
    stderr = process.stderr.decode("utf-8")
    logger.debug(stdout)

    if process.returncode != 0:
        msg = f"failed to install `{package_name}`"
        logger.debug(
            msg
            + "\n=================\n{o}\n=================\n{e}\n".format(
                o=stdout, e=stderr
            )
        )
        raise DiscoveryFailed(msg)

    logger.info("Package downloaded and installed in current environment")


def load_package(package_name: str) -> object:
    """
    Import the module into the current process state.
    """
    name = get_importname_from_package(package_name)
    try:
        package = importlib.import_module(name)
    except ImportError:
        raise DiscoveryFailed(f"could not load Python module '{name}'")

    return package


def get_discover_function(package: object):
    """
    Lookup the `discover` function from the given imported package.
    """
    funcs = inspect.getmembers(package, inspect.isfunction)
    for (name, value) in funcs:
        if name == "discover":
            return value

    raise DiscoveryFailed(
        "package '{name}' does not export a `discover` function".format(
            name=package.__name__
        )
    )


###############################################################################
# Private functions
###############################################################################
class PathDistribution(importlib_metadata.PathDistribution):
    """
    Extends the class for easier retrieval of top-level package names
    for a distribution installed package
    """

    @property
    def top_level(self):
        text = self.read_text("top_level.txt")
        return text and text.splitlines()


# Replace the original class with the extended one
# until this is officially supported in the API
importlib_metadata.PathDistribution = PathDistribution


def get_importname_from_package(package_name: str) -> str:
    """
    Try to fetch the name of the top-level import name for the given
    package. For some reason, this isn't straightforward.

    For now, we do not support distribution packages that contains
    multiple top-level packages.
    """
    try:
        dist = importlib_metadata.distribution(package_name)
    except importlib_metadata.PackageNotFoundError:
        raise DiscoveryFailed(f"Package {package_name} not found ")

    try:
        packages = dist.top_level
    except FileNotFoundError:
        raise DiscoveryFailed(
            "failed to load package {p} metadata. "
            "Was the package installed properly?".format(p=package_name)
        )

    if len(packages) > 1:
        raise DiscoveryFailed(
            "Package {p} contains multiple top-level packages. "
            "Unable to discover from multiple packages.".format(p=package_name)
        )
    return packages[0]
