# -*- coding: utf-8 -*-
import warnings

from logzero import logger

from chaoslib.activity import get_all_activities_in_experiment
from chaoslib.types import Experiment

__all__ = ["warn_about_deprecated_features"]
DeprecatedDictArgsMessage = \
    "Process arguments should now be a list to keep the ordering "\
    "of the arguments. Dictionary arguments are deprecated for "\
    "process activities."


def warn_about_deprecated_features(experiment: Experiment):
    """
    Warn about deprecated features.

    We do it globally so that we can warn only once about each feature and
    avoid repeating the same message over and over again.
    """
    warned_deprecations = {
        DeprecatedDictArgsMessage: False
    }
    activities = get_all_activities_in_experiment(experiment)

    for activity in activities:
        provider = activity.get("provider")
        if not provider:
            continue

        provider_type = provider.get("type")
        if provider_type == "process":
            arguments = provider.get("arguments")
            if not warned_deprecations[DeprecatedDictArgsMessage] and \
                    isinstance(arguments, dict):
                warned_deprecations[DeprecatedDictArgsMessage] = True
                warnings.warn(DeprecatedDictArgsMessage, DeprecationWarning)
                logger.warning(DeprecatedDictArgsMessage)
