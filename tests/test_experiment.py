# -*- coding: utf-8 -*-
import sys

import pytest
import requests_mock

from chaoslib.exceptions import InvalidExperiment
from chaoslib.experiment import ensure_experiment_is_valid
from chaoslib.types import Experiment

from fixtures import experiments


def test_empty_experiment_is_invalid():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.EmptyExperiment)
    assert "an empty experiment is not an experiment" in str(exc)


def test_experiment_must_have_a_method():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingMethodExperiment)
    assert "an experiment requires a method with "\
           "at least one activity" in str(exc)


def test_experiment_must_have_at_least_one_step():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.NoStepsMethodExperiment)
    assert "an experiment requires a method with "\
           "at least one activity" in str(exc)


def test_experiment_must_have_a_title():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingTitleExperiment)
    assert "experiment requires a title" in str(exc)


def test_experiment_must_have_a_description():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingDescriptionExperiment)
    assert "experiment requires a description" in str(exc)


def test_valid_experiment():
    assert ensure_experiment_is_valid(experiments.Experiment) is None
