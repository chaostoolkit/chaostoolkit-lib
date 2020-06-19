# -*- coding: utf-8 -*-
import os
import os.path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import contextvars
from logzero import logger
import yaml

from chaoslib.types import Settings

__all__ = ["get_loaded_settings", "load_settings", "save_settings",
           "locate_settings_entry"]
CHAOSTOOLKIT_CONFIG_PATH = os.path.abspath(
    os.path.expanduser("~/.chaostoolkit/settings.yaml"))
loaded_settings = contextvars.ContextVar('loaded_settings', default={})


def load_settings(settings_path: str = CHAOSTOOLKIT_CONFIG_PATH) -> Settings:
    """
    Load chaostoolkit settings as a mapping of key/values or return `None`
    when the file could not be found.
    """
    if not os.path.exists(settings_path):
        logger.debug("The Chaos Toolkit settings file could not be found at "
                     "'{c}'.".format(c=settings_path))
        return

    with open(settings_path) as f:
        try:
            settings = yaml.safe_load(f.read())
            loaded_settings.set(settings)
            return settings
        except yaml.YAMLError as ye:
            logger.error("Failed parsing YAML settings: {}".format(str(ye)))


def save_settings(settings: Settings,
                  settings_path: str = CHAOSTOOLKIT_CONFIG_PATH):
    """
    Save chaostoolkit settings as a mapping of key/values, overwriting any file
    that may already be present.
    """
    loaded_settings.set(settings)
    settings_dir = os.path.dirname(settings_path)
    if not os.path.isdir(settings_dir):
        os.mkdir(settings_dir)

    with open(settings_path, 'w') as outfile:
        yaml.dump(settings, outfile, default_flow_style=False)


def get_loaded_settings() -> Settings:
    """
    Settings that have been loaded in the current context.
    """
    return loaded_settings.get()


def locate_settings_entry(settings: Settings, key: str) \
        -> Optional[
            Tuple[
                Union[Dict[str, Any], List],
                Any,
                Optional[str],
                Optional[int]
            ]
           ]:
    """
    Lookup the entry at the given dotted key in the provided settings and
    return a a tuple as follows:

    * the parent of the found entry (can be a list or a dict)
    * the entry (can eb anything: string, int, list, dict)
    * the key on the parent that has the entry (in case parent is a dict)
    * the index in the parent that has the entry (in case parent is a list)

    Otherwise, returns `None`.

    When the key in the settings has at least one dot, it must be escaped
    with two backslahes.

    Examples of valid keys:

    * auths
    * auths.example\\.com
    * auths.example\\.com:8443
    * auths.example\\.com.type
    * controls[0].name
    """
    array_index = re.compile(r"\[([0-9]*)\]$")
    # borrowed from https://github.com/carlosescri/DottedDict (MIT)
    # this kindly preserves escaped dots
    parts = [x for x in re.split(r"(?<!\\)(\.)", key) if x != "."]

    current = settings
    parent = settings
    last_key = None
    last_index = None
    for part in parts:
        # we don't know to escape now that we have our part
        part = part.replace('\\', '')
        m = array_index.search(part)
        if m:
            # this is part with an index
            part = part[:m.start()]
            if part not in current:
                return
            current = current.get(part)
            parent = current
            index = int(m.groups()[0])
            last_key = None
            last_index = index
            try:
                current = current[index]
            except (KeyError, IndexError):
                return
        else:
            # this is just a regular key
            if part not in current:
                return
            parent = current
            last_key = part
            last_index = None
            current = current.get(part)

    return (parent, current, last_key, last_index)
