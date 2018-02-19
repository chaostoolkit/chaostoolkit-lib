# -*- coding: utf-8 -*-
import sys
import warnings

import pytest

from chaoslib import deprecation
from chaoslib.deprecation import DeprecatedDictArgsMessage, \
    warn_about_deprecated_features

from fixtures import experiments


def test_run_dict_arguments_has_been_deprecated_in_favor_of_list():
    warn_counts = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        warn_about_deprecated_features(
            experiments.ExperimentWithDeprecatedProcArgsProbe)
        for warning in w:
            if issubclass(warning.category, DeprecationWarning) and \
                warning.filename == deprecation.__file__:
                assert DeprecatedDictArgsMessage in str(warning.message)
                warn_counts = warn_counts + 1

    assert warn_counts == 1
