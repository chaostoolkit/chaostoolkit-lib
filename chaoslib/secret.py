import logging
import os
from typing import Any, Dict

from chaoslib.types import Configuration, Secrets
from chaoslib.secretmanagers.vault import load_secrets_from_vault
from chaoslib.secretmanagers.env import load_secret_from_env

__all__ = ["load_secrets"]

logger = logging.getLogger("chaostoolkit")


def load_secrets(
        secrets_info: Dict[str, Dict[str, str]],
        configuration: Configuration = None,
        extra_vars: Dict[str, Any] = None,
) -> Secrets:
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

    extra_vars = extra_vars or {}

    secrets = {}

    for key, value in secrets_info.items():
        if isinstance(value, dict):
            if extra_vars.get(key, None) is not None:
                secrets[key] = extra_vars.get(key)

            elif value.get("type") == "env":
                secrets[key] = load_secret_from_env(value)

            elif value.get("type") == "vault":
                secrets[key] = load_secrets_from_vault(value, configuration)

            else:
                secrets[key] = load_secrets(
                    value, configuration, extra_vars.get(key, None)
                )

        else:
            secrets[key] = value

    logger.debug("Done loading secrets")

    return secrets
