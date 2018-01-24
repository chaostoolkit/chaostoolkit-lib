# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict

from logzero import logger
try:
    import hvac
    HAS_HVAC = True
except ImportError:
    HAS_HVAC = False

from chaoslib.types import Configuration, Secrets

__all__ = ["load_secrets"]


def load_secrets(secrets_info: Dict[str, Dict[str, str]],
                 configuration: Configuration = None) -> Secrets:
    """
    Takes the the secrets definition from an experiment and tries to load
    the secrets whenever they relate to external sources such as environmental
    variables (or in the future from vault secrets).

    Here is an example of what it looks like:

    ```
    {
        "target_1": {
            "mysecret_1": "some value"
        },
        "target_2": {
            "mysecret_2": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        },
        "target_3": {
            "mysecret_3": {
                "type": "vault",
                "key": "secrets/some/key"
            }
        }
    }
    ```

    Loading this secrets definition will generate the following:

    ```
    {
        "target_1": {
            "mysecret_1": "some value"
        },
        "target_2": {
            "mysecret_2": "some other value"
        },
        "target_3": {
            "mysecret_3": "some alternate value"
        }
    }
    ```

    You can refer to those from your experiments:

    ```
    {
        "type": "probe",
        "provider": {
            "secret": ["target_1", "target_2"]
        }
    }
    ```
    """
    logger.debug("Loading secrets...")

    loaders = (
        load_inline_secrets,
        load_secrets_from_env,
        load_secrets_from_vault,
    )

    secrets = {}
    for loader in loaders:
        for key, value in loader(secrets_info, configuration).items():
            if key not in secrets:
                secrets[key] = {}
            secrets[key].update(value)

    logger.debug("Secrets loaded")

    return secrets


def load_inline_secrets(secrets_info: Dict[str, Dict[str, str]],
                        configuration: Configuration = None) -> Secrets:
    """
    Load secrets that are inlined in the experiments.
    """
    secrets = {}

    for (target, keys) in secrets_info.items():
        secrets[target] = {}

        for (key, value) in keys.items():
            if not isinstance(value, dict):
                secrets[target][key] = value
            elif value.get("type") not in ("env", "vault"):
                secrets[target][key] = value

        if not secrets[target]:
            secrets.pop(target)

    return secrets


def load_secrets_from_env(secrets_info: Dict[str, Dict[str, str]],
                          configuration: Configuration = None) -> Secrets:
    env = os.environ
    secrets = {}

    for (target, keys) in secrets_info.items():
        secrets[target] = {}

        for (key, value) in keys.items():
            if isinstance(value, dict) and value.get("type") == "env":
                secrets[target][key] = env.get(value["key"])

        if not secrets[target]:
            secrets.pop(target)

    return secrets


def load_secrets_from_vault(secrets_info: Dict[str, Dict[str, str]],
                            configuration: Configuration = None) -> Secrets:
    secrets = {}

    url = configuration.get("vault_addr")
    token = configuration.get("vault_token")

    client = None
    if HAS_HVAC:
        client = hvac.Client(url=url, token=token)

    for (target, keys) in secrets_info.items():
        secrets[target] = {}

        for (key, value) in keys.items():
            if isinstance(value, dict) and value.get("type") == "vault":
                if not HAS_HVAC:
                    logger.error(
                        "Install the `hvac` package to fetch secrets "
                        "from Vault: `pip install chaostoolkit-lib[vault]`.")
                    return {}
                secrets[target][key] = client.read(value["key"])

        if not secrets[target]:
            secrets.pop(target)

    return secrets
