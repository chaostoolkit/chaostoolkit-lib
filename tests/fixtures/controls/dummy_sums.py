from typing import Sequence

from chaoslib.types import Experiment, Journal


def before_experiment_control(context: Experiment, values: Sequence[int]) -> None:
    context["result_after"] = 0


def after_experiment_control(
    context: Experiment, state: Journal, values: Sequence[int]
) -> None:
    context["result_after"] += sum(values)
