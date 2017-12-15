# -*- coding: utf-8 -*-
from chaoslib import substitute

from fixtures import config


def test_substitute_strings_from_configuration():
    new_args = substitute("hello ${name}", config.SomeConfig, None)
    
    assert new_args == "hello Jane"


def test_substitute_from_configuration():
    args = {
        "message": "hello ${name}"
    }

    new_args = substitute(args, config.SomeConfig, None)
    
    assert new_args["message"] == "hello Jane"


def test_substitute_from_secrets():
    args = {
        "message": "hello ${name}"
    }

    new_args = substitute(args, None, {"ident": {"name": "Joe"}})
    
    assert new_args["message"] == "hello Joe"


def test_substitute_from_config_and_secrets_with_priority_to_config():
    args = {
        "message": "hello ${name}"
    }

    new_args = substitute(args, config.SomeConfig, {"ident": {"name": "Joe"}})
    
    assert new_args["message"] == "hello Jane"


def test_do_not_fail_when_key_is_missing():
    args = {
        "message": "hello ${firstname}"
    }

    new_args = substitute(args, config.SomeConfig, None)
    
    assert new_args["message"] == "hello ${firstname}"
