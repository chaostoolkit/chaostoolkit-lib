from typing import List

from chaoslib.exceptions import ActivityFailed, InterruptExecution

__all__ = [
    "many_args",
    "many_args_with_rich_types",
    "no_args_docstring",
    "no_args",
    "one_arg",
    "one_untyped_arg",
    "one_arg_with_default",
    "one_untyped_arg_with_default",
]


def no_args_docstring():
    pass


def no_args():
    """
    No arguments.
    """
    pass


def one_arg(message: str):
    """
    One typed argument.
    """
    pass


def one_arg_with_default(message: str = "hello"):
    """
    One typed argument with a default value.
    """
    pass


def one_untyped_arg(message):
    """
    One untyped argument.
    """
    pass


def one_untyped_arg_with_default(message="hello"):
    """
    One untyped argument with a default value.
    """
    pass


def many_args(message: str, colour: str = "blue"):
    """
    Many arguments.
    """
    pass


class Whatever:
    pass


def many_args_with_rich_types(
    message: str,
    recipients: List[str],
    colour: str = "blue",
    count: int = 1,
    logit: bool = False,
    other: Whatever = None,
    **kwargs
) -> str:
    """
    Many arguments with rich types.
    """
    pass


def do_nothing():
    pass


def echo_message(message: str) -> str:
    print(message)
    return message


def force_failed_activity():
    raise ActivityFailed()


def force_interrupting_experiment():
    raise InterruptExecution()
