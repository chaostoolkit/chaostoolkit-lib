# -*- coding: utf-8 -*-
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any, Dict, List

from pkg_resources import Distribution, EntryPoint, working_set
import pytest

from chaoslib.activity import execute_activity
from chaoslib.control import initialize_controls, cleanup_controls, \
    validate_controls, controls, get_all_activities, get_context_controls
from chaoslib.exceptions import InterruptExecution
from chaoslib.experiment import run_experiment
from chaoslib.types import Activity, Configuration, Control, \
    Experiment, Hypothesis, Journal, Run, Secrets,  Settings

from fixtures import  experiments
from fixtures.controls import dummy as DummyControl


def test_initialize_controls_will_configure_a_control():
    initialize_controls(
        experiments.ExperimentWithControls, configuration={
            "dummy-key": "dummy-value"
        })
    assert DummyControl.value_from_config == "dummy-value"
    cleanup_controls(experiments.ExperimentWithControls)


def test_initialize_controls_will_cleanup_a_control():
    cleanup_controls(experiments.ExperimentWithControls)
    assert DummyControl.value_from_config == None


def test_controls_are_applied_pre_and_post_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("experiment", exp, context=exp) as c:
        assert "pre_experiment_control" in exp
        assert exp["pre_experiment_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_experiment_control" in exp
    assert exp["post_experiment_control"] is True
    assert journal["post_experiment_control"] is True


def test_controls_are_applied_pre_and_but_not_post_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = ["pre"]
    with controls("experiment", exp, context=exp) as c:
        assert "pre_experiment_control" in exp
        assert exp["pre_experiment_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_experiment_control" not in exp


def test_controls_are_applied_not_pre_and_but_post_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = ["post"]
    with controls("experiment", exp, context=exp) as c:
        assert "pre_experiment_control" not in exp

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_experiment_control" in exp
    assert exp["post_experiment_control"] is True
    assert journal["post_experiment_control"] is True


def test_controls_may_interrupt_experiment():
    exp = deepcopy(experiments.ExperimentCanBeInterruptedByControl)
    with controls("experiment", exp, context=exp) as c:
        exp["dry"] = True
        journal = run_experiment(exp)
        assert journal["status"] == "interrupted"


def test_controls_are_applied_pre_and_post_hypothesis():
    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    with controls("hypothesis", exp, context=hypo) as c:
        assert "pre_hypothesis_control" in hypo
        assert hypo["pre_hypothesis_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_hypothesis_control" in hypo
    assert hypo["post_hypothesis_control"] is True
    assert journal["steady_states"]["before"]["post_hypothesis_control"] is True


def test_controls_are_applied_pre_and_post_method():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("method", exp, context=exp) as c:
        assert "pre_method_control" in exp
        assert exp["pre_method_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_method_control" in exp
    assert exp["post_method_control"] is True
    assert "post_method_control" in journal["run"]


def test_controls_are_applied_pre_and_post_rollbacks():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("rollback", exp, context=exp) as c:
        assert "pre_rollback_control" in exp
        assert exp["pre_rollback_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_rollback_control" in exp
    assert exp["post_rollback_control"] is True
    assert "post_rollback_control" in journal["rollbacks"]


def test_controls_are_applied_pre_and_post_activities():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["dry"] = True

    activities = get_all_activities(exp)
    for activity in activities:
        with controls("activity", exp, context=activity) as c:
            assert activity["pre_activity_control"] is True

            run = execute_activity(exp, activity, None, None, dry=False)

            assert "post_activity_control" in activity
            assert activity["post_activity_control"] is True
            assert run["post_activity_control"] is True


def test_no_controls_get_applied_when_none_defined():
    exp = deepcopy(experiments.ExperimentWithoutControls)
    exp["dry"] = True

    with controls("experiment", exp, context=exp) as c:
        assert "pre_experiment_control" not in exp

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "post_experiment_control" not in exp


def test_automatic_goes_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)

    controls = get_context_controls(exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls(exp, hypo)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls(exp, activity)
        assert len(controls) == 1


def test_not_automatic_does_not_go_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False

    controls = get_context_controls(exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls(exp, hypo)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls(exp, activity)
        assert len(controls) == 0
