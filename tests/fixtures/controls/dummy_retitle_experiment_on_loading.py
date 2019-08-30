from chaoslib.types import Experiment


def after_loading_experiment_control(context: str, state: Experiment):
    state["title"] = "BOOM I changed it"
