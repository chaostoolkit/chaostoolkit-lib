# -*- coding: utf-8 -*-
import sys

import pytest
import requests_mock

from chaoslib.exceptions import FailedProbe, InvalidProbe
from chaoslib.probe import ensure_probe_is_valid, run_probe
from chaoslib.types import Probe

from fixtures import experiments, probes


def test_empty_probe_is_invalid():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.EmptyProbe)
    assert "empty probe is no probe" in str(exc)


def test_probe_must_have_a_type():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingTypeProbe)
    assert "a probe must have a type" in str(exc)


def test_probe_must_have_a_known_type():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.UnknownTypeProbe)
    assert "unknown probe type 'whatever'" in str(exc)


def test_python_probe_must_have_a_module_path():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingModuleProbe)
    assert "a Python probe must have a module path" in str(exc)


def test_python_probe_must_have_a_function_name():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingFunctionProbe)
    assert "a Python probe must have a function name" in str(exc)


def test_python_probe_must_be_importable():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.NotImportableModuleProbe)
    assert "could not find Python module 'fake.module'" in str(exc)


def test_python_probe_func_must_have_enough_args():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingFuncArgProbe)
    assert "required argument 'path' is missing" in str(exc)


def test_python_probe_func_cannot_have_too_many_args():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.TooManyFuncArgsProbe)
    assert "argument 'should_not_be_here' is not part of the " \
           "function signature" in str(exc)


def test_process_probe_have_a_path():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingProcessPathProbe)
    assert "a process probe must have a path" in str(exc)


def test_process_probe_path_must_exist():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.ProcessPathDoesNotExistProbe)
    assert "'somewhere/not/here' cannot be found" in str(exc)


def test_http_probe_must_have_a_url():
    with pytest.raises(InvalidProbe) as exc:
        ensure_probe_is_valid(probes.MissingHTTPUrlProbe)
    assert "a HTTP probe must have a URL" in str(exc)


def test_run_python_probe_should_return_raw_value():
    # our probe checks a file exists
    assert run_probe(probes.PythonModuleProbe, experiments.Secrets) is True


def test_run_process_probe_should_return_raw_value():
    v = "Python {v}\n".format(v=sys.version.split(" ")[0])

    result = run_probe(probes.ProcProbe, experiments.Secrets)
    assert type(result) is bytes
    assert result.decode("utf-8") == v


def test_run_process_probe_can_timeout():
    probe = probes.ProcProbe
    probe["timeout"] = 0.0001

    with pytest.raises(FailedProbe) as exc:
        run_probe(probes.ProcProbe, experiments.Secrets).decode("utf-8")
    assert "probe took too long to complete" in str(exc)


def test_run_http_probe_should_return_raw_value():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', json=['well done'], 
            headers={"Content-Type": "application/json"})
        result = run_probe(probes.HTTPProbe, experiments.Secrets)
        assert result == ['well done']

        m.post(
            'http://example.com', text="['well done']")
        result = run_probe(probes.HTTPProbe, experiments.Secrets)
        assert result == "['well done']"


def test_run_http_probe_should_fail_when_return_code_is_above_400():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', status_code=404, text="Not found!")

        with pytest.raises(FailedProbe) as exc:
            run_probe(probes.HTTPProbe, experiments.Secrets)
        assert "Not found!" in str(exc)
