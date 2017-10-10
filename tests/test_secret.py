# -*- coding: utf-8 -*-
import os

import pytest

from chaoslib.secret import load_secrets


def test_should_load_environment():
    os.environ["KUBE_API_URL"] = "http://1.2.3.4"
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": "env.KUBE_API_URL"
        }
    })

    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"
