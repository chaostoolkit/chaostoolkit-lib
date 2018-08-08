# -*- coding: utf-8 -*-
import pytest

from chaoslib.exceptions import InvalidExperiment
from chaoslib.extension import get_extension, has_extension, merge_extension, \
    remove_extension, set_extension, validate_extensions

from fixtures import experiments


def test_extensions_must_have_name():
    with pytest.raises(InvalidExperiment):
        exp = experiments.Experiment.copy()
        set_extension(exp, {"somekey": "blah"})
        validate_extensions(exp)


def test_get_extension_returns_nothing_when_not_extensions_block():
    assert get_extension(experiments.Experiment, "myext") is None


def test_get_extension_returns_nothing_when_missing():
    ext = experiments.Experiment.copy()
    set_extension(ext, {
        "name": "myotherext",
        "somekey": "blah"
    })
    assert get_extension(ext, "myext") is None


def test_get_extension():
    exp = experiments.Experiment.copy()
    set_extension(exp, {
        "name": "myext",
        "somekey": "blah"
    })

    ext = get_extension(exp, "myext")
    assert ext is not None
    assert ext["somekey"] == "blah"


def test_remove_extension():
    exp = experiments.Experiment.copy()
    set_extension(exp, {
        "name": "myext",
        "somekey": "blah"
    })

    assert get_extension(exp, "myext") is not None
    remove_extension(exp, "myext")
    assert get_extension(exp, "myext") is None


def test_merge_extension():
    exp = experiments.Experiment.copy()
    set_extension(exp, {
        "name": "myext",
        "somekey": "blah"
    })

    ext = get_extension(exp, "myext")
    assert ext is not None
    assert ext["somekey"] == "blah"

    merge_extension(exp, {
        "name": "myext",
        "somekey": "burp",
        "otherkey": "oneday"
    })

    ext = get_extension(exp, "myext")
    assert ext is not None
    assert ext["somekey"] == "burp"
    assert ext["otherkey"] == "oneday"
