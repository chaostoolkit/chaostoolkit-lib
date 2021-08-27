from chaoslib.types import Activity, Configuration, Run, Secrets


def after_activity_control(
    context: Activity,
    state: Run,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs
):
    if context["name"] == "generate-token":
        secrets["mytokens"]["my_token"] = state["output"]
