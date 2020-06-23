from chaoslib.exceptions import InterruptExecution


def after_activity_control(**kwargs):
    raise InterruptExecution()
