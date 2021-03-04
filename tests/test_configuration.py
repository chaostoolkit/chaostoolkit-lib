# -*- coding: utf-8 -*-
import json
import os
import tempfile

import pytest
import yaml

from chaoslib import convert_vars, merge_vars
from chaoslib.configuration import load_configuration
from chaoslib.exceptions import InvalidExperiment


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
    with pytest.raises(InvalidExperiment) as x:
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
  
    assert str(x.value) == "Configuration makes reference to an environment key that does not exist: KUBE_TOKEN"


def test_can_override_experiment_inline_config_keys():
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
    }, extra_vars={
        "token1": "extravalue"
    })

    assert config["token1"] == "extravalue"
    assert config["token2"] == "value2"
    assert config["token3"] == "value3"


def test_default_value_is_overriden_in_inline_config_keys():
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
    }, extra_vars={
        "token3": "extravalue"
    })

    assert config["token1"] == "value1"
    assert config["token2"] == "value2"
    assert config["token3"] == "extravalue"


def test_merge_vars_from_keys_only_for_configs():
    assert merge_vars({"stuff": "todo"}) == ({"stuff": "todo"}, {})


def test_merge_config_vars_from_json_file():
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        f.write(json.dumps(
            {"configuration": {"otherstuff": "tobedone"}}).encode('utf-8'))
        f.seek(0)
        assert merge_vars({"stuff": "todo"}, [f.name]) == (
            {"stuff": "todo", "otherstuff": "tobedone"}, {})


def test_merge_config_vars_from_cli_override_from_file():
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        f.write(json.dumps(
            {"configuration": {"stuff": "tobedone"}}).encode('utf-8'))
        f.seek(0)
        assert merge_vars({"stuff": "todo"}, [f.name]) == (
            {"stuff": "todo"}, {})


def test_merge_secret_vars_from_json_file():
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        f.write(json.dumps(
            {"secrets": {"otherstuff": "tobedone"}}).encode('utf-8'))
        f.seek(0)
        assert merge_vars({"stuff": "todo"}, [f.name]) == (
            {"stuff": "todo"}, {"otherstuff": "tobedone"})


def test_merge_config_vars_from_yaml_file():
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(yaml.dump(
            {"configuration": {"otherstuff": "tobedone"}}).encode('utf-8'))
        f.seek(0)
        assert merge_vars({"stuff": "todo"}, [f.name]) == (
            {"stuff": "todo", "otherstuff": "tobedone"}, {})


def test_merge_secret_vars_from_yaml_file():
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(yaml.dump(
            {"secrets": {"otherstuff": "tobedone"}}).encode('utf-8'))
        f.seek(0)
        assert merge_vars({"stuff": "todo"}, [f.name]) == (
            {"stuff": "todo"}, {"otherstuff": "tobedone"})


def test_read_env_from_env_file():
    assert "STUFF" not in os.environ
    with tempfile.NamedTemporaryFile(suffix=".env") as f:
        f.write(b"STUFF=todo")
        f.seek(0)
        merge_vars(var_files=[f.name])
        assert os.environ["STUFF"] == "todo"
        os.environ.clear()


def test_convert_int_var():
    assert convert_vars(["age:int=45"]) == {"age": 45}


def test_convert_float_var():
    assert convert_vars(["age:float=45"]) == {"age": 45.0}


def test_convert_bytes_var():
    assert convert_vars(["todo:bytes=stuff"]) == {"todo": b"stuff"}


def test_convert_str_var():
    assert convert_vars(["todo:str=stuff"]) == {"todo": "stuff"}


def test_convert_default_to_str_var():
    assert convert_vars(["todo=stuff"]) == {"todo": "stuff"}


def test_convert_invalid_format():
    with pytest.raises(ValueError):
        convert_vars(["todo/stuff"])


def test_convert_invalid_type():
    with pytest.raises(ValueError):
        convert_vars(["todo:object=stuff"])


def test_should_override_load_configuration_with_var():
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
    },
    {
        "token1": "othervalue1",
        "token2": "othervalue2"
    })

    assert config["token1"] == "othervalue1"
    assert config["token2"] == "othervalue2"
    assert config["token3"] == "value3"


# see https://github.com/chaostoolkit/chaostoolkit-lib/issues/195
def test_load_nested_object_configuration():
    os.environ.clear()
    config = load_configuration({
        "nested": {
            "onea": "fdsfdsf",
            "lol": {
                "haha": [1, 2, 3]
            }
        }
    })

    assert isinstance(config["nested"], dict)
    assert config["nested"]["onea"] == "fdsfdsf"
    assert config["nested"]["lol"] == {"haha": [1, 2, 3]}
