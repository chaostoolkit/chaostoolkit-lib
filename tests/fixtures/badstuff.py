from itertools import count

from chaoslib.exceptions import InterruptExecution

__all__ = ["interrupt_me", "raise_exception", "check_under_treshold", "count_generator"]


def interrupt_me() -> None:
    raise InterruptExecution()


def raise_exception() -> None:
    raise Exception("oops")


g = None


def count_generator() -> int:
    global g
    if g is None:
        g = count()

    return next(g)


def cleanup_counter() -> None:
    global g
    g = None


def check_under_treshold(value: int = 0, target: int = 5) -> bool:
    global g
    if value >= target:
        return False
    return True
