from chaoslib.exceptions import InterruptExecution

def before_loading_experiment_control(context: str):
    raise InterruptExecution("failed to load: {}".format(context))
