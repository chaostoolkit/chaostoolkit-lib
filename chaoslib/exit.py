"""
This module is advanced usage and mostly interesting to users who need to
be able to terminate an experiment's execution as fast as possible and,
potentially, without much care for cleaning up afterwards.

If you want to interrup an execution but can affort to wait for graceful
completion (current activty, rollbacks...) it's probably best to rely on
the control interface.

If you need this utility here, you can simply do as follows:


```python
from chaoslib.exit import exit_ungracefully

def my_probe():
    # whatever condition comes up that shows you need to terminate asap
    exit_ungracefully()
```

Then in your experiment

```json
"method": [
    {
        "type": "probe",
        "name": "interrupt-when-system-is-unhappy",
        "background": True,
        "provider": {
            "type": "python",
            "module": "mymod",
            "func": "my_probe"
        }
    }
    ...
]
```

This will start your probe in the background.

WARNING: Only available on Unix/Linux systems.
"""
from chaoslib.exceptions import InterruptExecution
from contextlib import contextmanager
import inspect
import os
import platform
import signal
from types import FrameType

from logzero import logger

__all__ = ["exit_gracefully", "exit_ungracefully", "exit_signals"]


@contextmanager
def exit_signals():
    """
    Register the handlers for SIGTERM, SIGUSR1 and SIGUSR2 signals.
    Puts back the original handlers when the call ends.

    SIGTERM will trigger an InterruptExecution exception
    SIGUSR1 is used to terminate the experiment now while keeping the
    rollbacks if they were declared.
    SIGUSR2 is used to terminate the experiment without ever running the
    rollbacks.

    Generally speaking using signals this way is a bit of an overkill but
    the Python VM has no other mechanism to interrupt blocking calls.

    WARNING: SIGUSR1 and SIGUSR2 are only available on Unix/Linux systems.
    """
    sigterm_handler = signal.signal(signal.SIGTERM, _terminate_now)

    if hasattr(signal, "SIGUSR1") and hasattr(signal, "SIGUSR2"):
        # keep a reference to the original handlers
        sigusr1_handler = signal.signal(signal.SIGUSR1, _leave_now)
        sigusr2_handler = signal.signal(signal.SIGUSR2, _leave_now)
        try:
            yield
        finally:
            signal.signal(signal.SIGTERM, sigterm_handler)
            signal.signal(signal.SIGUSR1, sigusr1_handler)
            signal.signal(signal.SIGUSR2, sigusr2_handler)
    else:

        # On a system that doesn't support SIGUSR signals
        # not much we can do...
        logger.debug(
            "System '{}' does not expose SIGUSR signals".format(
                platform.platform()))
        try:
            yield
        finally:
            signal.signal(signal.SIGTERM, sigterm_handler)


def exit_gracefully():
    """
    Sends a user signal to the chaostoolkit process which should terminate
    the current execution immediatly, but gracefully.

    WARNING: Only available on Unix/Linux systems.
    """
    if not hasattr(signal, "SIGUSR1"):
        frames = inspect.getouterframes(inspect.currentframe())
        info = frames[1]
        logger.error(
            "Cannot call 'chaoslib.exit.exit_ungracefully() [{} - line {}] "
            "as it relies on the SIGUSR1 signal which is not available on "
            "your platform".format(info.filename, info.lineno))
        return

    os.kill(os.getpid(), signal.SIGUSR1)


def exit_ungracefully():
    """
    Sends a user signal to the chaostoolkit process which should terminate
    the current execution immediatly, but not gracefully.

    This means the rollbacks will not be executed, although controls
    will be correctly terminated.

    WARNING: Only available on Unix/Linux systems.
    """
    if not hasattr(signal, "SIGUSR2"):
        frames = inspect.getouterframes(inspect.currentframe())
        info = frames[1]
        logger.error(
            "Cannot call 'chaoslib.exit.exit_ungracefully() [{} - line {}] "
            "as it relies on the SIGUSR2 signal which is not available on "
            "your platform".format(info.filename, info.lineno))
        return

    os.kill(os.getpid(), signal.SIGUSR2)


###############################################################################
# Internals
###############################################################################
def _leave_now(signum: int, frame: FrameType = None) -> None:
    """
    Signal handler only interested in SIGUSR1 and SIGUSR2 to indicate
    requested termination of the experiment.
    """
    if signum == signal.SIGUSR1:
        raise SystemExit(20)

    elif signum == signal.SIGUSR2:
        raise SystemExit(30)


def _terminate_now(signum: int, frame: FrameType = None) -> None:
    """
    Signal handler for the SIGTERM event. Raises an `InterruptExecution`.
    """
    if signum == signal.SIGTERM:
        logger.warning("Caught SIGTERM signal, interrupting experiment now")
        raise InterruptExecution("SIGTERM signal received")
