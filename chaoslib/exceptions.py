# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidExperiment", "InvalidActivity",
           "ActivityFailed", "DiscoveryFailed", "InvalidSource",
           "InterruptExecution", "ControlPythonFunctionLoadingError",
           "InvalidControl"]


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


class ControlPythonFunctionLoadingError(Exception):
    pass


class InterruptExecution(ChaosException):
    pass


class InvalidControl(ChaosException):
    pass


class ExperimentExitedException(ChaosException):
    """
    Only raised when the process received a SIGUSR2 signal.

    Raised into the blocking background activities of the method only.

    If you catch it, this mean you can clean your activity but you should
    really raise another exception again to let the Chaos Toolkit
    quickly terminate.
    """
    pass
