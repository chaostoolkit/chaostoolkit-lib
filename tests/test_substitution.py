from fixtures import config

from chaoslib import substitute
from chaoslib.configuration import load_configuration


def test_substitute_strings_from_configuration() -> None:
    new_args = substitute("hello ${name}", config.SomeConfig, {})

    assert new_args == "hello Jane"


def test_substitute_from_configuration() -> None:
    args = {"message": "hello ${name}"}

    new_args = substitute(args, config.SomeConfig, {})

    assert isinstance(new_args, dict)
    assert new_args["message"] == "hello Jane"


def test_substitute_from_secrets() -> None:
    args = {"message": "hello ${name}"}

    new_args = substitute(args, {"": ""}, {"ident": {"name": "Joe"}})

    assert isinstance(new_args, dict)
    assert new_args["message"] == "hello Joe"


def test_substitute_from_config_and_secrets_with_priority_to_config() -> None:
    args = {"message": "hello ${name}"}

    new_args = substitute(args, config.SomeConfig, {"ident": {"name": "Joe"}})

    assert isinstance(new_args, dict)
    assert new_args["message"] == "hello Jane"


def test_do_not_fail_when_key_is_missing() -> None:
    args = {"message": "hello ${firstname}"}

    new_args = substitute(args, config.SomeConfig, {})

    assert isinstance(new_args, dict)
    assert new_args["message"] == "hello ${firstname}"


# see https://github.com/chaostoolkit/chaostoolkit-lib/issues/195
def test_use_nested_object_as_substitution() -> None:
    config = load_configuration(
        {"nested": {"onea": "fdsfdsf", "lol": {"haha": [1, 2, 3]}}}
    )

    result = substitute("${nested}", configuration=config, secrets={})
    assert isinstance(result, dict)
    assert result == {"onea": "fdsfdsf", "lol": {"haha": [1, 2, 3]}}


# see https://github.com/chaostoolkit/chaostoolkit-lib/issues/180
def test_use_integer_as_substitution() -> None:
    config = load_configuration({"value": 8})

    result = substitute("${value}", configuration=config, secrets={})
    assert isinstance(result, int)
    assert result == 8


def test_always_return_to_string_when_pattern_is_not_alone() -> None:
    config = load_configuration({"value": 8})

    result = substitute("hello ${value}", configuration=config, secrets={})
    assert isinstance(result, str)
    assert result == "hello 8"
