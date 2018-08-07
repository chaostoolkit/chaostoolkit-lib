# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidExperiment", "InvalidActivity",
           "FailedActivity", "DiscoveryFailed", "InvalidSource"]


class ChaosException(Exception):
    pass


class InvalidActivity(ChaosException):
    pass


class InvalidExperiment(ChaosException):
    pass


class FailedActivity(ChaosException):
    pass


class DiscoveryFailed(ChaosException):
    pass


class InvalidSource(ChaosException):
    pass
