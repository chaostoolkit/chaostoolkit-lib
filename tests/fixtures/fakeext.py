from typing import Any, List

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


def no_args_docstring() -> None:
    pass


def no_args() -> None:
    """
    No arguments.
    """
    pass


def one_arg(message: str) -> None:
    """
    One typed argument.
    """
    pass


def one_arg_with_default(message: str = "hello") -> None:
    """
    One typed argument with a default value.
    """
    pass


def one_untyped_arg(message) -> None:  # type: ignore[no-untyped-def]
    """
    One untyped argument.
    """
    pass


def one_untyped_arg_with_default(message="hello") -> None:  # type: ignore[no-untyped-def]  # Noqa
    """
    One untyped argument with a default value.
    """
    pass


def many_args(message: str, colour: str = "blue") -> None:
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
    **kwargs: Any
) -> str:
    """
    Many arguments with rich types.
    """
    pass


def do_nothing() -> None:
    pass


def echo_message(message: str) -> str:
    print(message)
    return message


def force_failed_activity() -> None:
    raise ActivityFailed()


def force_interrupting_experiment() -> None:
    raise InterruptExecution()
