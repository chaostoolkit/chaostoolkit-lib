from fixtures import config

from chaoslib import substitute
from chaoslib.configuration import load_configuration
from chaoslib.hypothesis import within_tolerance
from chaoslib.provider.http import run_http_activity


def test_substitute_strings_from_configuration():
    new_args = substitute("hello ${name}", config.SomeConfig, None)

    assert new_args == "hello Jane"


def test_substitute_from_configuration():
    args = {"message": "hello ${name}"}

    new_args = substitute(args, config.SomeConfig, None)

    assert new_args["message"] == "hello Jane"


def test_substitute_from_secrets():
    args = {"message": "hello ${name}"}

    new_args = substitute(args, None, {"ident": {"name": "Joe"}})

    assert new_args["message"] == "hello Joe"


def test_substitute_from_config_and_secrets_with_priority_to_config():
    args = {"message": "hello ${name}"}

    new_args = substitute(args, config.SomeConfig, {"ident": {"name": "Joe"}})

    assert new_args["message"] == "hello Jane"


def test_do_not_fail_when_key_is_missing():
    args = {"message": "hello ${firstname}"}

    new_args = substitute(args, config.SomeConfig, None)

    assert new_args["message"] == "hello ${firstname}"


# see https://github.com/chaostoolkit/chaostoolkit-lib/issues/195
def test_use_nested_object_as_substitution():
    config = load_configuration(
        {"nested": {"onea": "fdsfdsf", "lol": {"haha": [1, 2, 3]}}}
    )

    result = substitute("${nested}", configuration=config, secrets=None)
    assert isinstance(result, dict)
    assert result == {"onea": "fdsfdsf", "lol": {"haha": [1, 2, 3]}}


# see https://github.com/chaostoolkit/chaostoolkit-lib/issues/180
def test_use_integer_as_substitution():
    config = load_configuration({"value": 8})

    result = substitute("${value}", configuration=config, secrets=None)
    assert isinstance(result, int)
    assert result == 8


def test_always_return_to_string_when_pattern_is_not_alone():
    config = load_configuration({"value": 8})

    result = substitute("hello ${value}", configuration=config, secrets=None)
    assert isinstance(result, str)
    assert result == "hello 8"


def test_http_activity_can_substitute_timeout() -> None:
    c = {"my_timeout": 1}
    run_http_activity(
        {"provider": {"url": "https://www.google.com", "timeout": "${my_timeout}"}},
        c,
        {},
    )


def test_jsonpath_can_substitute_expect() -> None:
    r = within_tolerance(
        {
            "type": "jsonpath",
            "path": "$.RecordData[0]",
            "expect": ["my-other-cname.${env}.mysite.com"],
        },
        {"RecordData": ["my-other-cname.dev.mysite.com"]},
        {"env": "dev"},
        {},
    )

    assert r is True
