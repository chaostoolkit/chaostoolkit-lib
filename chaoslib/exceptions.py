# -*- coding: utf-8 -*-

__all__ = ["ChaosException", "InvalidExperiment", "InvalidActivity",
           "ActivityFailed", "DiscoveryFailed", "InvalidSource",
           "InterruptExecution", "ControlPythonFunctionLoadingError",
           "InvalidControl", "ValidationError"]


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


class ValidationError(ChaosException):
    def __init__(self, msg, errors, *args, **kwargs):
        """
        :param msg: exception message
        :param errors: single error as string or list of errors/exceptions
        """
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors
        super().__init__(msg, *args, **kwargs)

    def __str__(self) -> str:
        errors = self.errors
        nb_errors = len(errors)
        err_msg = super().__str__()
        return (
            "{msg}{dot} {nb} validation error{plural}:\n"
            " - {errors}".format(
                msg=err_msg,
                dot="" if err_msg.endswith(".") else ".",
                nb=nb_errors,
                plural="" if nb_errors == 1 else "s",
                errors="\n - ".join([str(err) for err in errors])
            )
        )
