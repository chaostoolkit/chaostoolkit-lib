from typing import Any

from chaoslib.types import Configuration, Experiment, Secrets, Settings


def configure_control(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    settings: Settings,
) -> None:
    raise RuntimeError("init control")


def before_experiment_control(context: Experiment, **kwargs: Any) -> None:
    context["should_never_been_called"] = True
