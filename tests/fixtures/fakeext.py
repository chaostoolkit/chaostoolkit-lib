# -*- coding: utf-8 -*-

__all__ = ["many_args", "no_args_docstring", "no_args", "one_arg",
           "one_untyped_arg", "one_arg_with_default",
           "one_untyped_arg_with_default"]


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


def one_arg_with_default(message: str="hello"):
    """
    One typed argument with a default value.
    """
    pass


def one_untyped_arg(message):
    """
    One untyped argument.
    """
    pass


def one_untyped_arg_with_default(message = "hello"):
    """
    One untyped argument with a default value.
    """
    pass


def many_args(message: str, colour: str="blue"):
    """
    Many arguments.
    """
    pass
