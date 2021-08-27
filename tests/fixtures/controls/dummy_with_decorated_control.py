from functools import wraps
from itertools import count
from typing import Callable

from logzero import logger

from chaoslib.types import Journal

counter = None


def initcounter(f: Callable) -> Callable:
    @wraps(f)
    def wrapped(*args, **kwargs) -> None:
        global counter
        counter = count()
        f(*args, **kwargs)

    return wrapped


def keepcount(f: Callable) -> Callable:
    @wraps(f)
    def wrapped(*args, **kwargs) -> None:
        next(counter)
        f(*args, **kwargs)

    return wrapped


@keepcount
def after_activity_control(**kwargs):
    logger.info("Activity is called")


@initcounter
def configure_control(**kwargs):
    logger.info("configure is called")


def after_experiment_control(state: Journal, **kwargs):
    state["counted_activities"] = next(counter)
