# -*- coding: utf-8 -*-
import pytest
import sys

from chaoslib.exceptions import InvalidActivity
from chaoslib.hypothesis import ensure_hypothesis_tolerance_is_valid, \
    within_tolerance


def test_tolerance_int():
    assert within_tolerance(6, value=6) is True


def test_tolerance_int_returns_false_when_different():
    assert within_tolerance(6, value=7) is False


def test_tolerance_int_from_process_status():
    assert within_tolerance(6, value={"status": 6}) is True


def test_tolerance_int_from_process_status_returns_false_when_different():
    assert within_tolerance(6, value={"status": 7}) is False


def test_tolerance_int_from_http_status():
    assert within_tolerance(6, value={"status": 6}) is True


def test_tolerance_int_from_http_status_returns_false_when_different():
    assert within_tolerance(6, value={"status": 7}) is False


def test_tolerance_list_int_from_process_status():
    assert within_tolerance([5, 6], value={"status": 6}) is True


def test_tolerance_list_int_from_process_status_returns_false_when_different():
    assert within_tolerance([5, 7], value={"status": 6}) is False


def test_tolerance_list_int_from_http_status():
    assert within_tolerance([5, 6], value={"status": 6}) is True


def test_tolerance_list_int_from_http_status_returns_false_when_different():
    assert within_tolerance([5, 7], value={"status": 6}) is False


def test_tolerance_bool():
    assert within_tolerance(True, value=True) is True


def test_tolerance_bool_returns_false_when_different():
    assert within_tolerance(True, value=False) is False


def test_tolerance_string():
    assert within_tolerance("hello", value="hello") is True


def test_tolerance_string_returns_false_when_different():
    assert within_tolerance("hello", value="not hello") is False


def test_tolerance_string():
    assert within_tolerance("hello", value="hello") is True


def test_tolerance_string_returns_false_when_different():
    assert within_tolerance("hello", value="not hello") is False


def test_tolerance_regex():
    assert within_tolerance(
        {
            "type": "regex",
            "pattern": "[0-9]{2}"
        },
        value="you are number 87"
    ) is True


def test_tolerance_regex():
    t = {
        "type": "regex",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value="you are number 8") is False


def test_tolerance_jsonpath_from_dict():
    t = {
        "type": "jsonpath",
        "path": "foo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is True


def test_tolerance_jsonpath_must_find_items_to_succeed():
    t = {
        "type": "jsonpath",
        "path": "notsofoo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is False


def test_tolerance_jsonpath_must_match_expected_value():
    t = {
        "type": "jsonpath",
        "path": "foo.baz",
        "expect": "hello"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }, 
    ) is True

    t = {
        "type": "jsonpath",
        "path": "foo.baz",
        "expect": ["hello", "bonjour"]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": ["hello", "bonjour"]}
        }, 
    ) is True


def test_tolerance_jsonpath_must_match_expected_values():
    t = {
        "type": "jsonpath",
        "path": "foo[*].baz",
        "expect": ["hello", "bonjour"]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{"baz": "hello"}, {"baz": "bonjour"}]
        }, 
    ) is True


def test_tolerance_jsonpath_must_find_items_with_a_given_value_to_succeed():
    t = {
        "type": "jsonpath",
        "path": "foo[?baz=2]",
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is True

    t = {
        "type": "jsonpath",
        "path": "foo[0].baz",
        "count": 2
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is False

    t = {
        "type": "jsonpath",
        "path": "foo[?baz=4]",
        "count": 2
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 4}, {'baz': 4}]
        }) is True


def test_tolerance_jsonpath_from_jsonstring():
    t = {
        "type": "jsonpath",
        "path": "foo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value='{"foo": [{"baz": 1}, {"baz": 2}]}') is True


def test_tolerance_jsonpath_from_bytes():
    t = {
        "type": "jsonpath",
        "path": "foo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value=b'{"foo": [{"baz": 1}, {"baz": 2}]}') is True


def test_tolerance_regex_stdout_process():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 87",
            "stderr": ""
        }
    ) is True


def test_tolerance_regex_stdout_process_needs_to_match():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 8",
            "stderr": ""
        }
    ) is False


def test_tolerance_regex_stderr_process():
    t = {
        "type": "regex",
        "target": "stderr",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "",
            "stderr": "you are number 87"
        }
    ) is True


def test_tolerance_regex_stdout_process_needs_to_match():
    t = {
        "type": "regex",
        "target": "stderr",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "",
            "stderr": "you are number 8"
        }
    ) is False


def test_tolerance_regex_process_only_match_stdout_or_stderr():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 87",
            "stderr": "you are number 8"
        }
    ) is True


def test_tolerance_regex_body_http():
    t = {
        "type": "regex",
        "target": "body",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "you are number 87"
        }
    ) is True


def test_tolerance_regex_must_have_a_pattern():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout"
        })
    assert "tolerance must have a `pattern` key" in str(e)


def test_tolerance_regex_must_have_a_valid_pattern_type():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout",
            "pattern": None
        })
    assert "tolerance pattern None has an invalid type" in str(e)


def test_tolerance_regex_must_have_a_valid_pattern():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout",
            "pattern": "[0-9"
        })
    assert "pattern [0-9 seems invalid" in str(e)


def test_tolerance_unsupported_type():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "boom"
        })
    assert "tolerance type 'boom' is unsupported" in str(e)


def test_tolerance_unsupported_type():
    from chaoslib import hypothesis
    hypothesis.HAS_JSONPATH = False
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "jsonpath",
            "path": "whatever"
        })
    hypothesis.HAS_JSONPATH = True
    assert "Install the `jsonpath_ng` package to use a JSON path" in str(e)
