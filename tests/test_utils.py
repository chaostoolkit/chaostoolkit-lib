import pytest

from chaoslib import convert_to_type


def test_can_convert_to_bool():
    assert convert_to_type("bool", "false") is False
    assert convert_to_type("bool", "0") is False
    assert convert_to_type("bool", "no") is False
    assert convert_to_type("bool", "true") is True
    assert convert_to_type("bool", "1") is True
    assert convert_to_type("bool", "yes") is True


def test_can_convert_to_int():
    assert convert_to_type("int", "17") == 17
    assert convert_to_type("integer", "95") == 95


def test_can_convert_to_float():
    assert convert_to_type("float", "17.76") == 17.76
    assert convert_to_type("number", "95.89") == 95.89
    assert convert_to_type("float", "17") == 17.0


def test_can_convert_to_str():
    assert convert_to_type("str", "hello") == "hello"
    assert convert_to_type("string", "hello") == "hello"


def test_can_convert_to_bytes():
    assert convert_to_type("bytes", "hello") == b"hello"


def test_can_convert_to_json():
    assert convert_to_type("json", '{"a": 67}') == {"a": 67}


def test_no_type_is_bypass():
    assert convert_to_type(None, "true") == "true"


def test_cannot_convert_unknown_type():
    with pytest.raises(ValueError):
        convert_to_type("yaml", "true") == "true"


def test_can_convert_to_json_is_silent_when_no_value_given():
    assert convert_to_type("json", "") == ""
