# -*- coding: utf-8 -*-
from contextlib import contextmanager
from copy import deepcopy
from typing import List, Union

from logzero import logger

from chaoslib.control.python import apply_python_control, cleanup_control, \
    initialize_control, validate_python_control
from chaoslib.exceptions import InterruptExecution, InvalidControl
from chaoslib.types import Activity, Configuration, \
    Experiment, Hypothesis, Journal, Run, Secrets

__all__ = ["controls", "initialize_controls", "cleanup_controls",
           "validate_controls", "Control"]


def initialize_controls(experiment: Experiment,
                        configuration: Configuration = None,
                        secrets: Secrets = None):
    """
    Initialize all declared controls in the experiment.

    On Python controls, this means calling the `configure_control` function
    of the exposed module.

    Controls are initialized once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Initializing controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug("Initializing control '{}'".format(name))

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            initialize_control(control, configuration, secrets)


def cleanup_controls(experiment: Experiment):
    """
    Cleanup all declared controls in the experiment.

    On Python controls, this means calling the `cleanup_control` function
    of the exposed module.

    Controls are cleaned up once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Cleaning up controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug("Cleaning up control '{}'".format(name))

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            cleanup_control(control)


def validate_controls(experiment: Experiment):
    """
    Validate that all declared controls respect the specification.

    Raises :exc:`chaoslib.exceptions.InvalidControl` when they are not valid.
    """
    controls = get_controls(experiment)
    references = [
        c["name"] for c in get_controls(experiment)
        if "ref" not in c and "name" in c
    ]
    for c in controls:
        if "ref" in c:
            if c["ref"] not in references:
                raise InvalidControl(
                    "Control reference '{}' declaration cannot be found")

        if "name" not in c:
            raise InvalidControl("A control must have a `name` property")

        name = c["name"]
        if "provider" not in c:
            raise InvalidControl(
                "Control '{}' must have a `provider` property".format(name))

        scope = c.get("scope")
        if scope and scope not in ("before", "after"):
            raise InvalidControl(
                "Control '{}' scope property must be 'before' or "
                "'after' only".format(name))

        provider_type = c.get("provider", {}).get("type")
        if provider_type == "python":
            validate_python_control(c)


class Control:
    def begin(self, level: str, experiment: Experiment,
              context: Union[Activity, Hypothesis, Experiment],
              configuration: Configuration = None, secrets: Secrets = None):
        self.state = None
        apply_controls(
            level=level, experiment=experiment, context=context,
            scope="before", configuration=configuration, secrets=secrets)

    def with_state(self, state):
        self.state = state

    def end(self, level: str, experiment: Experiment,
            context: Union[Activity, Hypothesis, Experiment],
            configuration: Configuration = None, secrets: Secrets = None):
        state = self.state
        self.state = None
        apply_controls(
            level=level, experiment=experiment, context=context,
            scope="after", state=state, configuration=configuration,
            secrets=secrets)


@contextmanager
def controls(level: str, experiment: Experiment,
             context: Union[Activity, Hypothesis, Experiment],
             configuration: Configuration = None, secrets: Secrets = None):
    """
    Context manager for a block that needs to be wrapped by controls.
    """
    try:
        c = Control()
        c.begin(level, experiment, context, configuration, secrets)
        yield c
    finally:
        c.end(level, experiment, context, configuration, secrets)


###############################################################################
# Internals
###############################################################################
def get_all_activities(experiment: Experiment) -> List[Activity]:
    activities = []
    activities.extend(
        experiment.get("steady-state-hypothesis", {}).get("probes", []))
    activities.extend(
        experiment.get("method", []))
    activities.extend(
        experiment.get("rollbacks", []))
    return activities


def get_controls(experiment: Experiment) -> List[Control]:
    controls = []
    controls.extend(experiment.get("controls", []))
    controls.extend(
        experiment.get("steady-state-hypothesis", {}).get("controls", []))

    for activity in get_all_activities(experiment):
        controls.extend(activity.get("controls", []))
    return controls


def get_context_controls(level: str, experiment: Experiment,
                         context: Union[Activity, Experiment]) \
                         -> List[Control]:
    """
    Get the controls at the given level by merging those declared at the
    experiment level with the current's context.

    If a control is declared at the current level, do override it with an
    top-level ine.
    """
    top_level_controls = experiment.get("controls", [])

    controls = context.get("controls", [])
    if not controls:
        if not top_level_controls:
            return []
        else:
            return [
                deepcopy(c)
                for c in top_level_controls
                if c.get("automatic", True)
            ]

    if level in ["method", "rollback"]:
        return [
            deepcopy(c)
            for c in top_level_controls
            if c.get("automatic", True)
        ]

    for c in controls.copy():
        if "ref" in c:
            for top_level_control in top_level_controls:
                if c["ref"] == top_level_control["name"]:
                    controls.append(deepcopy(top_level_control))
                    break
        else:
            for tc in top_level_controls:
                if c.get("name") == tc.get("name"):
                    break
            else:
                if tc.get("automatic", True):
                    controls.append(deepcopy(tc))

    return controls


def apply_controls(level: str, experiment: Experiment,
                   context: Union[Activity, Hypothesis, Experiment],
                   scope: str, state: Union[Journal, Run, List[Run]] = None,
                   configuration: Configuration = None,
                   secrets: Secrets = None):
    """
    Apply the controls at given level

    The ̀ level` parameter is one of `"experiment", "hypothesis", "method",
    "rollback", "activity"`. The `context` is usually an experiment except at
    the `"activity"` when it must be an activity. The `scope` is one of
    `"before", "after"` and the `state` is only set on `"after"` scope.
    """
    controls = get_context_controls(level, experiment, context)
    if not controls:
        return

    for control in controls:
        control_name = control.get("name")
        target_scope = control.get("scope")

        if target_scope and target_scope != scope:
            continue

        logger.debug(
            "Applying {}-control '{}' on '{}'".format(
                scope, control_name, level))
        provider = control.get("provider", {})
        provider_type = provider.get("type")

        try:
            if provider_type == "python":
                apply_python_control(
                    level="{}-{}".format(level, scope), control=control,
                    context=context, state=state, experiment=experiment,
                    configuration=configuration, secrets=secrets)
        except InterruptExecution:
            logger.debug(
                "{}-control '{}' interrupted the execution".format(
                    scope.title(), control_name), exc_info=True)
            raise
        except Exception:
            logger.debug(
                "{}-control '{}' failed".format(
                    scope.title(), control_name), exc_info=True)
