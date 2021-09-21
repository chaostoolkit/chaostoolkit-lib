from typing import Any

from chaoslib.exceptions import InterruptExecution


def after_activity_control(**kwargs: Any):
    raise InterruptExecution()
