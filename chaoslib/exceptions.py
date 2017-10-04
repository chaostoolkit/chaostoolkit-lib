# -*- coding: utf-8 -*-

__all__ = ["InvalidActivity", "InvalidProbe", "InvalidAction",
           "FailedAction", "FailedActivity", "FailedProbe"]


class InvalidAction(BaseException):
    pass


class InvalidProbe(BaseException):
    pass


class InvalidActivity(BaseException):
    pass


class FailedProbe(BaseException):
    pass


class InvalidExperiment(BaseException):
    pass


class FailedActivity(BaseException):
    pass


class FailedAction(BaseException):
    pass
