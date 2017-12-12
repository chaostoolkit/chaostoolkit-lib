# -*- coding: utf-8 -*-
import os

import pytest

from chaoslib.secret import load_secrets

from fixtures import config


def test_should_load_environment():
    os.environ["KUBE_API_URL"] = "http://1.2.3.4"
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig)

    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"
