# -*- coding: utf-8 -*-
import os

import pytest

from chaoslib.configuration import load_configuration


def test_should_load_configuration():
    os.environ["KUBE_TOKEN"] = "value2"
    config = load_configuration({
        "token1": "value1",
        "token2": {
            "type": "env",
            "key": "KUBE_TOKEN"
        },
        "token3": {
            "type": "probe",
            "name": "Get some value from a process",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": ["-n", "value3"]
            }
        },
        "token4": {
            "type": "probe",
            "name": "Get some value from Python",
            "provider": {
                "type": "python",
                "module": "string",
                "func": "capwords",
                "arguments": {
                    "s": "value4"
                }
            }
        }
    })

    assert config["token1"] == "value1"
    assert config["token2"] == "value2"
    assert config["token3"] == "value3"
    assert config["token4"] == "Value4"
