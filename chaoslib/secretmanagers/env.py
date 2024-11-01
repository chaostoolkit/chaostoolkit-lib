import os
from typing import Dict

from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Secrets


def load_secret_from_env(secrets_info: Dict[str, Dict[str, str]]) -> Secrets:
    env = os.environ

    if isinstance(secrets_info, dict) and secrets_info.get("type") == "env":
        env_key = secrets_info["key"]
        if env_key not in env:
            raise InvalidExperiment(
                "Secrets make reference to an environment key "
                "that does not exist: {}".format(env_key)
            )
        else:
            secret = env[env_key]

    return secret
