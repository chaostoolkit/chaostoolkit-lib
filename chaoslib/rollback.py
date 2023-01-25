from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Iterator

from logzero import logger

from chaoslib.activity import execute_activity
from chaoslib.types import Configuration, Dry, Experiment, Run, Secrets

if TYPE_CHECKING:
    from chaoslib.run import EventHandlerRegistry

__all__ = ["run_rollbacks"]


def run_rollbacks(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    pool: ThreadPoolExecutor,
    dry: Dry,
    event_registry: "EventHandlerRegistry" = None,
) -> Iterator[Run]:
    """
    Run all rollbacks declared in the experiment in their order. Wait for
    each rollback activity to complete before to the next unless the activity
    is declared with the `background` flag.
    """
    rollbacks = experiment.get("rollbacks", [])

    if not rollbacks:
        logger.info("No declared rollbacks, let's move on.")

    for activity in rollbacks:
        logger.info("Rollback: {t}".format(t=activity.get("name")))

        if activity.get("background"):
            logger.debug("rollback activity will run in the background")
            yield pool.submit(
                execute_activity,
                experiment=experiment,
                activity=activity,
                configuration=configuration,
                secrets=secrets,
                dry=dry,
                event_registry=event_registry,
            )
        else:
            yield execute_activity(
                experiment,
                activity,
                configuration=configuration,
                secrets=secrets,
                dry=dry,
                event_registry=event_registry,
            )
