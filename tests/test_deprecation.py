import warnings
from unittest.mock import patch

from fixtures import experiments

from chaoslib import deprecation, experiment
from chaoslib.deprecation import (
    DeprecatedDictArgsMessage,
    DeprecatedVaultMissingPathMessage,
    warn_about_deprecated_features,
)
from chaoslib.experiment import (
    apply_activities,
    apply_rollbacks,
    initialize_run_journal,
)


def test_run_dict_arguments_has_been_deprecated_in_favor_of_list():
    warn_counts = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        warn_about_deprecated_features(
            experiments.ExperimentWithDeprecatedProcArgsProbe
        )
        for warning in w:
            if (
                issubclass(warning.category, DeprecationWarning)
                and warning.filename == deprecation.__file__
            ):
                assert DeprecatedDictArgsMessage in str(warning.message)
                warn_counts = warn_counts + 1

    assert warn_counts == 1


def test_vault_secrets_require_path():
    warn_counts = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        warn_about_deprecated_features(experiments.ExperimentWithDeprecatedVaultPayload)
        for warning in w:
            if (
                issubclass(warning.category, DeprecationWarning)
                and warning.filename == deprecation.__file__
            ):
                assert DeprecatedVaultMissingPathMessage in str(warning.message)
                warn_counts = warn_counts + 1

    assert warn_counts == 1


def test_initialize_run_journal_has_moved():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        with patch("chaoslib.experiment.init_journal"):
            initialize_run_journal(None)
            assert len(w) == 1
            assert w[0].filename == experiment.__file__
            assert "'initialize_run_journal'" in str(w[0].message)


def test_apply_activities_has_moved():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        with patch("chaoslib.experiment.apply_act"):
            apply_activities(None, None, None, None, None, None)
            assert len(w) == 1
            assert w[0].filename == experiment.__file__
            assert "'apply_activities'" in str(w[0].message)


def test_apply_rollbacks_has_moved():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("module")
        with patch("chaoslib.experiment.apply_roll"):
            apply_rollbacks(None, None, None, None, None)
            assert len(w) == 1
            assert w[0].filename == experiment.__file__
            assert "'apply_rollbacks'" in str(w[0].message)
