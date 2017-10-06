# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidActivity", "InvalidProbe",
           "InvalidAction", "FailedAction", "FailedActivity", "FailedProbe"]


class ChaosException(Exception):
    pass


class InvalidActivity(ChaosException):
    pass


class InvalidAction(InvalidActivity):
    pass


class InvalidProbe(InvalidActivity):
    pass


class InvalidExperiment(ChaosException):
    pass


class FailedActivity(ChaosException):
    pass


class FailedAction(FailedActivity):
    pass


class FailedProbe(FailedActivity):
    pass
