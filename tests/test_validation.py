# -*- coding: utf-8 -*-
import pytest

from chaoslib.validation import Validation


def assert_in_errors(msg, errors):
    """
    Check whether msg can be found in any of the list of errors

    :param msg: exception string to be found in any of the instances
    :param errors: list of ChaosException instances
    """
    print(errors)
    for error in errors:
        if msg in error["msg"]:
            # expected exception message is found
            return

    raise AssertionError("{} not in {}".format(msg, errors))


#
# v = Validation()
# v.add_error("key", "invalid value", value=5, location=("test", 0, "key"))
# v.add_error("other", "missing required value", value=None, location=("name",))
# v.add_error("dummy", "this is an error")
# from logzero import logger
# logger.debug('Experiment is invalid. \n{errors}'.format(errors=str(v)))
# # print(v)

def test_add_error():
    v = Validation()
    v.add_error("test", "this is an error message")
    assert v.has_errors()


def test_extend_errors():
    v = Validation()
    v.add_error("test", "this is an error message")
    v.extend_errors([{'dummy': 'error'}, {'another': 'error'}])
    assert len(v.errors()) == 3


def test_display_errors():
    v = Validation()
    v.add_error("test", "this is an error message", value=False,
                location=("a", "b", "c"))
    str = v.display_errors()
    assert len(str)


def test_errors_as_json():
    v = Validation()
    v.add_error("test", "this is an error message", value=False,
                location=("a", "b", "c"))
    json = v.json()
    assert len(json)


def test_merge_validation():
    v1 = Validation()
    v1.add_error("test", "this is an error message")

    v2 = Validation()
    v2.add_error("test", "this is another error message")

    v1.merge(v2)
    assert len(v1.errors()) == 2


def test_str_output():
    v = Validation()
    v.add_error("test", "this is an error message", value=False,
                location=("a", "b", "c"))
    assert str(v)
