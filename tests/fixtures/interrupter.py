import time

from chaoslib.exit import exit_gracefully, exit_ungracefully


def interrupt_gracefully_in(seconds: int = 1.5) -> None:
    time.sleep(seconds)
    exit_gracefully()


def interrupt_ungracefully_in(seconds: int = 1.5) -> None:
    time.sleep(seconds)
    exit_ungracefully()
