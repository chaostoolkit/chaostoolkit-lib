# -*- coding: utf-8 -*-
import os
from typing import Dict

from logzero import logger

from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Configuration

__all__ = ["load_configuration"]


def load_configuration(config_info: Dict[str, str]) -> Configuration:
    """
    Load the configuration. The `config_info` parameter is a mapping from
    key strings to value as strings or dictionaries. In the former case, the
    value is used as-is. In the latter case, if the dictionary has a key named
    `type` alongside a key named `key`.
    An optional default value is accepted for dictionary value with a key named
    `default`. The default value will be used only if the environment variable
    is not defined.


    Here is a sample of what it looks like:

    ```
    {
        "cert": "/some/path/file.crt",
        "token": {
            "type": "env",
            "key": "MY_TOKEN"
        },
        "host": {
            "type": "env",
            "key": "HOSTNAME",
            "default": "localhost"
        }
    }
    ```

    The `cert` configuration key is set to its string value whereas the `token`
    configuration key is dynamically fetched from the `MY_TOKEN` environment
    variable. The `host` configuration key is dynamically fetched from the
    `HOSTNAME` environment variable, but if not defined, the default value
    `localhost` will be used instead.
    """
    logger.debug("Loading configuration...")
    env = os.environ
    conf = {}

    for (key, value) in config_info.items():
        if isinstance(value, dict) and "type" in value:
            if value["type"] == "env":
                env_key = value["key"]
                env_default = value.get("default")
                if env_key not in env and not env_default:
                    raise InvalidExperiment(
                        "Configuration makes reference to an environment key"
                        " that does not exist: {}".format(env_key))
                conf[key] = env.get(env_key, env_default)
        else:
            conf[key] = value

    return conf
