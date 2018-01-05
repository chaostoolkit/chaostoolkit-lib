# -*- coding: utf-8 -*-
import json
import sys

import pytest
import requests_mock

from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.activity import ensure_activity_is_valid, run_activity
from chaoslib.types import Probe

from fixtures import config, experiments, probes


def test_empty_probe_is_invalid():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.EmptyProbe)
    assert "empty activity is no activity" in str(exc)


def test_probe_must_have_a_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingTypeProbe)
    assert "an activity must have a type" in str(exc)


def test_probe_must_have_a_known_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.UnknownTypeProbe)
    assert "'whatever' is not a supported activity type" in str(exc)


def test_probe_provider_must_have_a_known_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.UnknownProviderTypeProbe)
    assert "unknown provider type 'pizza'" in str(exc)


def test_python_probe_must_have_a_module_path():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingModuleProbe)
    assert "a Python activity must have a module path" in str(exc)


def test_python_probe_must_have_a_function_name():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingFunctionProbe)
    assert "a Python activity must have a function name" in str(exc)


def test_python_probe_must_be_importable():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.NotImportableModuleProbe)
    assert "could not find Python module 'fake.module'" in str(exc)


def test_python_probe_func_must_have_enough_args():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingFuncArgProbe)
    assert "required argument 'path' is missing" in str(exc)


def test_python_probe_func_cannot_have_too_many_args():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.TooManyFuncArgsProbe)
    assert "argument 'should_not_be_here' is not part of the " \
           "function signature" in str(exc)


def test_process_probe_have_a_path():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingProcessPathProbe)
    assert "a process activity must have a path" in str(exc)


def test_process_probe_path_must_exist():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.ProcessPathDoesNotExistProbe)
    assert "path 'None' cannot be found, in activity" in str(exc)


def test_http_probe_must_have_a_url():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingHTTPUrlProbe)
    assert "a HTTP activity must have a URL" in str(exc)


def test_run_python_probe_should_return_raw_value():
    # our probe checks a file exists
    assert run_activity(
        probes.PythonModuleProbe, config.EmptyConfig,
        experiments.Secrets) is True


def test_run_process_probe_should_return_raw_value():
    v = "Python {v}\n".format(v=sys.version.split(" ")[0])

    result = run_activity(
        probes.ProcProbe, config.EmptyConfig, experiments.Secrets)
    assert type(result) is tuple
    assert result == (0, v, '')


def test_run_process_probe_can_timeout():
    probe = probes.ProcProbe
    probe["provider"]["timeout"] = 0.0001

    with pytest.raises(FailedActivity) as exc:
        run_activity(
            probes.ProcProbe, config.EmptyConfig, 
            experiments.Secrets).decode("utf-8")
    assert "activity took too long to complete" in str(exc)


def test_run_http_probe_should_return_parsed_json_value():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post(
            'http://example.com', json=['well done'], headers=headers)
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == ['well done']


def test_run_http_probe_must_be_serializable_to_json():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post(
            'http://example.com', json=['well done'], headers=headers)
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert json.dumps(result) is not None


def test_run_http_probe_should_return_raw_text_value():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', text="['well done']")
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == "['well done']"


def test_run_http_probe_can_expect_failure():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', status_code=404, text="Not found!")

        probe = probes.HTTPProbe.copy()
        probe['provider']["expected_status"] = 404

        try:
            run_activity(probe, config.EmptyConfig, experiments.Secrets)
        except FailedActivity:
            pytest.fail("activity should not have failed")
