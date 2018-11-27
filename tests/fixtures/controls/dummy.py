import os
from typing import Any, Callable, Dict, List, NoReturn, Union

from chaoslib.types import Activity, Configuration, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings

value_from_config = None


def configure_control(config: Configuration, secrets = Secrets) -> NoReturn:
    global value_from_config
    print(config)
    value_from_config = config.get("dummy-key", "default")


def cleanup_control() -> NoReturn:
    global value_from_config
    value_from_config = None


def pre_experiment_control(context: Experiment, **kwargs):
    context["pre_experiment_control"] = True


def post_experiment_control(context: Experiment, state: Journal, **kwargs):
    context["post_experiment_control"] = True
    state["post_experiment_control"] = True


def pre_hypothesis_control(context: Hypothesis, **kwargs):
    context["pre_hypothesis_control"] = True


def post_hypothesis_control(context: Hypothesis,
                            state: Dict[str, Any], **kwargs):
    context["post_hypothesis_control"] = True
    state["post_hypothesis_control"] = True


def pre_method_control(context: Experiment, **kwargs):
    context["pre_method_control"] = True


def post_method_control(context: Experiment, state: List[Run], **kwargs):
    context["post_method_control"] = True
    state.append("post_method_control")


def pre_rollback_control(context: Experiment, **kwargs):
    context["pre_rollback_control"] = True


def post_rollback_control(context: Experiment, state: List[Run], **kwargs):
    context["post_rollback_control"] = True
    state.append("post_rollback_control")


def pre_activity_control(context: Activity, **kwargs):
    context["pre_activity_control"] = True


def post_activity_control(context: Activity, state: Run, **kwargs):
    context["post_activity_control"] = True
    state["post_activity_control"] = True
