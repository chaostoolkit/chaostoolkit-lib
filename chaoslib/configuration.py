# -*- coding: utf-8 -*-
import os
from typing import Dict

from logzero import logger

from chaoslib.exceptions import InvalidExperiment, ChaosException
from chaoslib.types import Configuration
from chaoslib.activity import run_activity

__all__ = ["load_configuration"]


def load_configuration(config_info: Dict[str, str]) -> Configuration:
    """
    Load the configuration. The `config_info` parameter is a mapping from
    key strings to value as strings or dictionaries. In the cert case, the
    value is used as-is. In the other cases, if the dictionary has a key named
    `type` with `env` value, it will take the `key` value from the env
    variables. If `type` is `probe`, it will take the value from a probe
    In the probe is of type `process`, the value will be taken from `stdout`
    In the probe is of type `python`, the value will be taken from the
    result as is
    In the probe is of type `http`, the value will be taken from `body`

    Here is a sample of what it looks like:

    ```
    {
        "cert": "/some/path/file.crt",
        "token": {
            "type": "env",
            "key": "MY_TOKEN"
        },
        "date": {
          "type": "probe",
          "name": "Current date",
          "provider": {
            "type": "process",
            "path": "date"
          }
        },
        "words": {
          "type": "probe",
          "name": "Some capped words",
          "provider": {
              "type": "python",
              "module": "string",
              "func": "capwords",
              "arguments": {
                "s": "some words"
              }
          }
        },
        "valueFromServer": {
          "type": "probe",
          "name": "Some value taken from the network",
          "provider": {
            "type": "http",
            "url": "http://my.config.server.com/value"
         }
        }
    }
    ```

    The `cert` configuration key is set to its string value whereas the `token`
    configuration key is dynamically fetched from the `MY_TOKEN` environment
    variable.
    """
    logger.debug("Loading configuration...")
    env = os.environ
    conf = {}

    for (key, value) in config_info.items():
        if isinstance(value, dict) and "type" in value:
            if value["type"] == "env":
                env_key = value["key"]
                if env_key not in env:
                    raise InvalidExperiment(
                        "Configuration makes reference to an environment key"
                        " that does not exist: {}".format(env_key))
                conf[key] = env.get(env_key)
            elif value["type"] == "probe":
                result = run_activity(value, config_info, {})
                if value["provider"]["type"] == "process":
                    conf[key] = result.get("stdout")
                elif value["provider"]["type"] == "python":
                    conf[key] = result
                elif value["provider"]["type"] == "body":
                    conf[key] = result
                else:
                    raise ChaosException(
                        "Different provider than process not supported yet")
        else:
            conf[key] = value

    return conf
