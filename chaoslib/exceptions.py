# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidExperiment", "InvalidActivity",
           "FailedActivity"]


class ChaosException(Exception):
    pass


class InvalidActivity(ChaosException):
    pass


class InvalidExperiment(ChaosException):
    pass


class FailedActivity(ChaosException):
    pass
