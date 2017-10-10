# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict

from logzero import logger

from chaoslib.types import Secrets

__all__ = ["load_secrets"]


def load_secrets(secrets_info: Dict[str, Dict[str, str]]) -> Secrets:
    """
    Takes the the secrets definition from an experiment and tries to load
    the secrets whenever they relate to external sources such as environmental
    variables (or in the future from vault secrets).
    """
    logger.info("Loading secrets...")
    secrets = {}

    for (target, keys) in secrets_info.items():
        logger.info("Loading secrets for {t}".format(t=target))
        secrets[target] = {}

        for (key, value) in keys.items():
            if value.startswith("env."):
                secrets[target][key] = os.environ.get(value[4:])
            else:
                secrets[target][key] = value

    return secrets
