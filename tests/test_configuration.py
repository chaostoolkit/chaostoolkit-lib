# -*- coding: utf-8 -*-
import os

import pytest

from chaoslib.exceptions import InvalidExperiment
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
            "type": "env",
            "key": "UNDEFINED",
            "default": "value3"
        }
    })

    assert config["token1"] == "value1"
    assert config["token2"] == "value2"
    assert config["token3"] == "value3"

def test_should_load_configuration_with_empty_string_as_default():
    os.environ.clear()
    os.environ["KUBE_TOKEN"] = "value2"
    config = load_configuration({
        "token1": "value1",
        "token2": {
            "type": "env",
            "key": "KUBE_TOKEN"
        },
        "token3": {
            "type": "env",
            "key": "UNDEFINED",
            "default": ""
        }
    })

    assert config["token1"] == "value1"
    assert config["token2"] == "value2"
    assert config["token3"] == ""

def test_should_load_configuration_with_empty_string_as_input():
    os.environ.clear()
    os.environ["KUBE_TOKEN"] = ""
    config = load_configuration({
        "token1": "value1",
        "token2": {
            "type": "env",
            "key": "KUBE_TOKEN"
        },
        "token3": {
            "type": "env",
            "key": "UNDEFINED",
            "default": "value3"
        }
    })

    assert config["token1"] == "value1"
    assert config["token2"] == ""
    assert config["token3"] == "value3"

def test_should_load_configuration_with_empty_string_as_input_while_default_is_define():
    os.environ.clear()
    os.environ["KUBE_TOKEN"] = ""
    config = load_configuration({
        "token1": "value1",
        "token2": {
            "type": "env",
            "key": "KUBE_TOKEN",
            "default": "value2"
        },
        "token3": {
            "type": "env",
            "key": "UNDEFINED",
            "default": "value3"
        }
    })

    assert config["token1"] == "value1"
    assert config["token2"] == ""
    assert config["token3"] == "value3"

def test_load_configuration_should_raise_exception():
    os.environ.clear()
    try:
        load_configuration({
            "token1": "value1",
            "token2": {
                "type": "env",
                "key": "KUBE_TOKEN"
            },
            "token3": {
                "type": "env",
                "key": "UNDEFINED",
                "default": ""
            }
        })
    except InvalidExperiment as err:
        assert format(err) == "Configuration makes reference to an environment key that does not exist: KUBE_TOKEN"
    else:
        raise AssertionError("should raise InvalidExperiment")