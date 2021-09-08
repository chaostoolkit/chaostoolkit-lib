from itertools import count

from chaoslib.exceptions import InterruptExecution

__all__ = ["interrupt_me", "raise_exception", "check_under_treshold", "count_generator"]


def interrupt_me():
    raise InterruptExecution()


def raise_exception():
    raise Exception("oops")


g = None


def count_generator():
    global g
    if g is None:
        g = count()

    return next(g)


def cleanup_counter():
    global g
    g = None


def check_under_treshold(value: int = 0, target: int = 5) -> bool:
    global g
    if value >= target:
        return False
    return True
