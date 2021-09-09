from chaoslib.types import Configuration, Experiment, Secrets, Settings


def configure_control(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    settings: Settings,
    joke: str,
):
    experiment["joke"] = joke
