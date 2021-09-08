import warnings

from logzero import logger

from chaoslib.activity import get_all_activities_in_experiment
from chaoslib.types import Experiment

__all__ = ["warn_about_deprecated_features", "warn_about_moved_function"]
DeprecatedDictArgsMessage = (
    "Process arguments should now be a list to keep the ordering "
    "of the arguments. Dictionary arguments are deprecated for "
    "process activities."
)
DeprecatedVaultMissingPathMessage = (
    "Vault secrets must now specify the `path` property. The `key` property "
    "is now a key of a Vault secret rather than the actual path. For "
    "instance: "
    "{'my-key': {'type': 'vault', 'key': 'foo'}} "
    "now becomes: "
    "{'my-key': {'type': 'vault', 'path': 'foo'}}"
)


def warn_about_deprecated_features(experiment: Experiment):
    """
    Warn about deprecated features.

    We do it globally so that we can warn only once about each feature and
    avoid repeating the same message over and over again.
    """
    warned_deprecations = {
        DeprecatedDictArgsMessage: False,
        DeprecatedVaultMissingPathMessage: False,
    }
    activities = get_all_activities_in_experiment(experiment)

    for activity in activities:
        provider = activity.get("provider")
        if not provider:
            continue

        provider_type = provider.get("type")
        if provider_type == "process":
            arguments = provider.get("arguments")
            if not warned_deprecations[DeprecatedDictArgsMessage] and isinstance(
                arguments, dict
            ):
                warned_deprecations[DeprecatedDictArgsMessage] = True
                warnings.warn(DeprecatedDictArgsMessage, DeprecationWarning)
                logger.warning(DeprecatedDictArgsMessage)

    # vault now expects the path property
    # see https://github.com/chaostoolkit/chaostoolkit-lib/issues/77
    for (target, keys) in experiment.get("secrets", {}).items():
        for (key, value) in keys.items():
            if isinstance(value, dict) and value.get("type") == "vault":
                if "key" in value and "path" not in value:
                    warned_deprecations[DeprecatedVaultMissingPathMessage] = True
                    warnings.warn(DeprecatedVaultMissingPathMessage, DeprecationWarning)
                    logger.warning(DeprecatedVaultMissingPathMessage)


def warn_about_moved_function(message: str):
    warnings.warn(message, DeprecationWarning, stacklevel=2)
