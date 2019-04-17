import os
from typing import Any, Callable, Dict, List, Union

from chaoslib.types import Activity, Configuration, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings

value_from_config = None


def configure_control(config: Configuration, secrets: Secrets,
                      settings: Settings):
    global value_from_config
    if config:
        value_from_config = config.get("dummy-key", "default")
    elif settings:
        value_from_config = settings.get("dummy-key", "default")


def cleanup_control():
    global value_from_config
    value_from_config = None


def before_experiment_control(context: Experiment, **kwargs):
    context["before_experiment_control"] = True


def after_experiment_control(context: Experiment, state: Journal, **kwargs):
    context["after_experiment_control"] = True
    state["after_experiment_control"] = True


def before_hypothesis_control(context: Hypothesis, **kwargs):
    context["before_hypothesis_control"] = True


def after_hypothesis_control(context: Hypothesis,
                             state: Dict[str, Any], **kwargs):
    context["after_hypothesis_control"] = True
    state["after_hypothesis_control"] = True


def before_method_control(context: Experiment, **kwargs):
    context["before_method_control"] = True


def after_method_control(context: Experiment, state: List[Run], **kwargs):
    context["after_method_control"] = True
    state.append("after_method_control")


def before_rollback_control(context: Experiment, **kwargs):
    context["before_rollback_control"] = True


def after_rollback_control(context: Experiment, state: List[Run], **kwargs):
    context["after_rollback_control"] = True
    state.append("after_rollback_control")


def before_activity_control(context: Activity, **kwargs):
    context["before_activity_control"] = True


def after_activity_control(context: Activity, state: Run, **kwargs):
    context["after_activity_control"] = True
    state["after_activity_control"] = True
