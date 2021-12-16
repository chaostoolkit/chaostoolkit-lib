import os
from copy import deepcopy
from typing import Any, Dict

from logzero import logger

from chaoslib import convert_to_type
from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Configuration, Secrets

__all__ = ["load_configuration", "load_dynamic_configuration"]


def load_configuration(
    config_info: Dict[str, str], extra_vars: Dict[str, Any] = None
) -> Configuration:
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
        },
        "port": {
            "type": "env",
            "key": "SERVICE_PORT",
            "env_var_type": "int"
        }
    }
    ```

    The `cert` configuration key is set to its string value whereas the `token`
    configuration key is dynamically fetched from the `MY_TOKEN` environment
    variable. The `host` configuration key is dynamically fetched from the
    `HOSTNAME` environment variable, but if not defined, the default value
    `localhost` will be used instead. The `port` configuration key is
    dynamically fetched from the `SERVICE_PORT` environment variable. It is
    coerced into an `int` with the addition of the `env_var_type` key.

    When `extra_vars` is provided, it must be a dictionnary where keys map
    to configuration key. The values from `extra_vars` always override the
    values from the experiment itself. This is useful to the Chaos Toolkit
    CLI mostly to allow overriding values directly from cli arguments. It's
    seldom required otherwise.
    """
    logger.debug("Loading configuration...")
    env = os.environ
    extra_vars = extra_vars or {}
    conf = {}

    for (key, value) in config_info.items():
        if isinstance(value, dict) and "type" in value:
            if value["type"] == "env":
                env_key = value["key"]
                env_default = value.get("default")
                if (
                    (env_key not in env)
                    and (env_default is None)
                    and (key not in extra_vars)
                ):
                    raise InvalidExperiment(
                        "Configuration makes reference to an environment key"
                        " that does not exist: {}".format(env_key)
                    )
                env_var_type = value.get("env_var_type")
                env_var_value = convert_to_type(
                    env_var_type, env.get(env_key, env_default)
                )
                conf[key] = extra_vars.get(key, env_var_value)
            else:
                conf[key] = extra_vars.get(key, value)

        else:
            conf[key] = extra_vars.get(key, value)

    return conf


def load_dynamic_configuration(
    config: Configuration, secrets: Secrets = None
) -> Configuration:
    """
    This is for loading a dynamic configuration if exists.
    The dynamic config is a regular activity (probe) in the configuration
    section. If there's a use-case for setting a configuration dynamically
    right before the experiment is starting. It executes the probe,
    and then the return value of this probe will be the config you wish to set.
    The dictionary needs to have a key named `type` and as a value `probe`,
    alongside the rest of the probe props.
    (No need for the `tolerance` key).

    For example:

    ```json
    "some_dynamic_config": {
      "name": "some config probe",
      "type": "probe",
      "provider": {
        "type": "python",
        "module": "src.probes",
        "func": "config_probe",
        "arguments": {
            "arg1":"arg1"
        }
      }
    }
    ```

    `some_dynamic_config` will be set with the return value
    of the function config_probe.

    Side Note: the probe type can be the same as a regular probe can be,
    python, process or http. The config argument contains all the
    configurations of the experiment including the raw config_probe
    configuration that can be dynamically injected.

    The configurations contain as well all the env vars after they are set in
    `load_configuration`.

    The `secrets` argument contains all the secrets of the experiment.

    For `process` probes, the stdout value (stripped of endlines)
    is stored into the configuration.
    For `http` probes, the `body` value is stored.
    For `python` probes, the output of the function will be stored.

    We do not stop on errors but log a debug message and do not include the
    key into the result dictionary.
    """
    # we delay this so that the configuration module can be imported leanly
    # from elsewhere
    from chaoslib.activity import run_activity

    conf = {}
    secrets = secrets or {}

    had_errors = False
    logger.debug("Loading dynamic configuration...")
    for (key, value) in config.items():
        if not (isinstance(value, dict) and value.get("type") == "probe"):
            conf[key] = config.get(key, value)
            continue

        # we have a dynamic config
        name = value.get("name")
        provider_type = value["provider"]["type"]
        value["provider"]["secrets"] = deepcopy(secrets)
        try:
            output = run_activity(value, config, secrets)
        except Exception:
            had_errors = True
            logger.debug(f"Failed to load configuration '{name}'", exc_info=True)
            continue

        if provider_type == "python":
            conf[key] = output
        elif provider_type == "process":
            if output["status"] != 0:
                had_errors = True
                logger.debug(
                    f"Failed to load configuration dynamically "
                    f"from probe '{name}': {output['stderr']}"
                )
            else:
                conf[key] = output.get("stdout", "").strip()
        elif provider_type == "http":
            conf[key] = output.get("body")

    if had_errors:
        logger.warning(
            "Some of the dynamic configuration failed to be loaded."
            "Please review the log file for understanding what happened."
        )

    return conf
