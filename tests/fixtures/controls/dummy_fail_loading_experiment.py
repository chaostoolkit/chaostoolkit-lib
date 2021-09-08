from chaoslib.exceptions import InterruptExecution


def before_loading_experiment_control(context: str):
    raise InterruptExecution(f"failed to load: {context}")
