from typing import Any

from chaoslib.types import Activity, Configuration, Run, Secrets


def after_activity_control(
    context: Activity,
    state: Run,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any
) -> None:
    if context["name"] == "generate-token":
        configuration["my_token"] = state["output"]
