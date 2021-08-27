from chaoslib.types import Configuration, Experiment, Secrets, Settings


def configure_control(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    settings: Settings,
):
    raise RuntimeError("init control")


def before_experiment_control(context: Experiment, **kwargs):
    context["should_never_been_called"] = True
