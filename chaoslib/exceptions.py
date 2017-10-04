# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidActivity", "InvalidProbe",
           "InvalidAction", "FailedAction", "FailedActivity", "FailedProbe"]


class ChaosException(Exception):
    pass


class InvalidAction(ChaosException):
    pass


class InvalidProbe(ChaosException):
    pass


class InvalidActivity(ChaosException):
    pass


class FailedProbe(ChaosException):
    pass


class InvalidExperiment(ChaosException):
    pass


class FailedActivity(ChaosException):
    pass


class FailedAction(ChaosException):
    pass
