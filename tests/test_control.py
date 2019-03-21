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
from chaoslib.control.python import validate_python_control
from chaoslib.exceptions import InterruptExecution, InvalidActivity
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


def test_controls_are_applied_before_and_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("experiment", exp, context=exp) as c:
        assert "before_experiment_control" in exp
        assert exp["before_experiment_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" in exp
    assert exp["after_experiment_control"] is True
    assert journal["after_experiment_control"] is True


def test_controls_are_applied_before_and_but_not_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = "before"
    with controls("experiment", exp, context=exp) as c:
        assert "before_experiment_control" in exp
        assert exp["before_experiment_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" not in exp


def test_controls_are_applied_not_before_and_but_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = "after"
    with controls("experiment", exp, context=exp) as c:
        assert "before_experiment_control" not in exp

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" in exp
    assert exp["after_experiment_control"] is True
    assert journal["after_experiment_control"] is True


def test_controls_may_interrupt_experiment():
    exp = deepcopy(experiments.ExperimentCanBeInterruptedByControl)
    with controls("experiment", exp, context=exp) as c:
        exp["dry"] = True
        journal = run_experiment(exp)
        assert journal["status"] == "interrupted"


def test_controls_are_applied_before_and_after_hypothesis():
    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    with controls("hypothesis", exp, context=hypo) as c:
        assert "before_hypothesis_control" in hypo
        assert hypo["before_hypothesis_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_hypothesis_control" in hypo
    assert hypo["after_hypothesis_control"] is True
    assert journal["steady_states"]["before"]["after_hypothesis_control"] is True


def test_controls_are_applied_before_and_after_method():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("method", exp, context=exp) as c:
        assert "before_method_control" in exp
        assert exp["before_method_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_method_control" in exp
    assert exp["after_method_control"] is True
    assert "after_method_control" in journal["run"]


def test_controls_are_applied_before_and_after_rollbacks():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("rollback", exp, context=exp) as c:
        assert "before_rollback_control" in exp
        assert exp["before_rollback_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_rollback_control" in exp
    assert exp["after_rollback_control"] is True
    assert "after_rollback_control" in journal["rollbacks"]


def test_controls_are_applied_before_and_after_activities():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["dry"] = True

    activities = get_all_activities(exp)
    for activity in activities:
        with controls("activity", exp, context=activity) as c:
            assert activity["before_activity_control"] is True

            run = execute_activity(exp, activity, None, None, dry=False)

            assert "after_activity_control" in activity
            assert activity["after_activity_control"] is True
            assert run["after_activity_control"] is True


def test_no_controls_get_applied_when_none_defined():
    exp = deepcopy(experiments.ExperimentWithoutControls)
    exp["dry"] = True

    with controls("experiment", exp, context=exp) as c:
        assert "before_experiment_control" not in exp

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" not in exp


def test_automatic_goes_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)

    controls = get_context_controls("experiment", exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls("hypothesis", exp, hypo)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls("activity", exp, activity)
        assert len(controls) == 1


def test_not_automatic_does_not_go_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False

    controls = get_context_controls("experiment", exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls("hypothesis", exp, hypo)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    controls = get_context_controls("method", exp, exp)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    controls = get_context_controls("rollback", exp, exp)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls("activity", exp, activity)
        assert len(controls) == 0


def test_validate_python_control_must_be_loadable():
    with pytest.raises(InvalidActivity):
        validate_python_control({
            "name": "a-python-control",
            "provider": {
                "type": "python",
                "module": "blah.blah"
            }
        })


def test_validate_python_control_needs_a_module():
    with pytest.raises(InvalidActivity):
        validate_python_control({
            "name": "a-python-control",
            "provider": {
                "type": "python"
            }
        })


def test_controls_can_access_experiment():
    exp = deepcopy(experiments.ExperimentWithControlAccessingExperiment)
    exp["dry"] = True

    hypo = exp.get("steady-state-hypothesis")
    run_experiment(exp)
    assert hypo["has_experiment_before"] is True
    assert hypo["has_experiment_after"] is True

    activities = get_all_activities(exp)
    for activity in activities:
        assert activity["has_experiment_before"] is True
        assert activity["has_experiment_after"] is True


def test_controls_are_applied_at_various_levels():
    exp = deepcopy(experiments.ExperimentWithControlsAtVariousLevels)
    exp["dry"] = True

    run_experiment(exp)
    activities = get_all_activities(exp)
    for activity in activities:
        print(activity)
        if "controls" in activity:
            assert activity["before_activity_control"] is True
            assert activity["after_activity_control"] is True


def test_controls_are_applied_when_they_are_not_top_level():
    exp = deepcopy(experiments.ExperimentWithControlNotAtTopLevel)
    exp["dry"] = True

    run_experiment(exp)
    activities = get_all_activities(exp)
    for activity in activities:
        if "controls" in activity:
            assert activity["before_activity_control"] is True
            assert activity["after_activity_control"] is True
