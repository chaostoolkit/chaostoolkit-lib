from collections import namedtuple
from typing import List

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

__all__ = ["list_extensions"]


info_fields = ["name", "version", "summary", "license", "author", "url"]


class ExtensionInfo(namedtuple("ExtensionInfo", info_fields)):
    __slots__ = ()


def list_extensions() -> List[ExtensionInfo]:
    """
    List all installed Chaos Toolkit extensions in the current environment.

    Notice, for now we can only list extensions that start with `chaostoolkit-`
    in their package name.

    This is not as powerful and solid as we want it to be. The trick is that we
    can't rely on any metadata inside extensions to tell us they exist and
    what functionnality they provide either. Python has the concept of trove
    classifiers on packages but we can't extend them yet so they are of no use
    to us.

    In a future version, we will provide a mechanism from packages to support
    a better detection.
    """
    infos = []
    distros = importlib_metadata.distributions()
    seen = []
    for dist in distros:
        info = dist.metadata
        name = info["Name"]
        if name == "chaostoolkit-lib":
            continue
        if name in seen:
            continue
        seen.append(name)
        if name.startswith("chaostoolkit-"):
            ext = ExtensionInfo(
                name=name,
                version=info["Version"],
                summary=info["Summary"],
                license=info["License"],
                author=info["Author"],
                url=info["Home-page"],
            )
            infos.append(ext)
    return infos
