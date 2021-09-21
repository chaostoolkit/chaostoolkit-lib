from typing import Any

from chaoslib.exceptions import InterruptExecution
from chaoslib.types import Activity


def before_activity_control(
    context: Activity, target_activity_name: str, **kwargs: Any
) -> None:
    if context.get("name") == target_activity_name:
        raise InterruptExecution("let's blow this up")
