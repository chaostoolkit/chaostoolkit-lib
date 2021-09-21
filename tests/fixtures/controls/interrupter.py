from typing import Any

from chaoslib.exceptions import InterruptExecution
from chaoslib.types import Activity


def before_activity_control(context: Activity, **kwargs: Any) -> None:
    raise InterruptExecution("let's blow this up")
