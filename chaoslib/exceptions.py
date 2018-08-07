# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidExperiment", "InvalidActivity",
           "ActivityFailed", "DiscoveryFailed", "InvalidSource"]


class ChaosException(Exception):
    pass


class InvalidActivity(ChaosException):
    pass


class InvalidExperiment(ChaosException):
    pass


class ActivityFailed(ChaosException):
    pass


# please use ActivityFailed rather than the old name for this exception
FailedActivity = ActivityFailed


class DiscoveryFailed(ChaosException):
    pass


class InvalidSource(ChaosException):
    pass
