from chaoslib.types import Experiment


def before_experiment_control(context: Experiment) -> None:
    context.setdefault("position", []).append(1)
    print(context["position"])
