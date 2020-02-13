# -*- coding: utf-8 -*-
import json
import pytest
import requests_mock
import tempfile

from chaoslib.exceptions import InvalidSource, InvalidExperiment
from chaoslib.loader import load_experiment, parse_experiment_from_file
from chaoslib.types import Settings
import requests

from fixtures import experiments


def test_load_from_file(generic_experiment: str):
    try:
        load_experiment(generic_experiment)
    except InvalidSource as x:
        pytest.fail(str(x))


def test_load_invalid_filepath(generic_experiment: str):
    with pytest.raises(InvalidSource) as x:
        load_experiment("/tmp/xyuzye.txt")
    assert 'Path "/tmp/xyuzye.txt" does not exist.' in str(x.value)


def test_load_from_http_without_auth(generic_experiment: str):
    with requests_mock.mock() as m:
        m.get(
            'http://example.com/experiment.json', status_code=200,
            headers={"Content-Type": "application/json"},
            json=json.dumps(generic_experiment)
        )
        try:
            load_experiment('http://example.com/experiment.json')
        except InvalidSource as x:
            pytest.fail(str(x))


def test_load_from_http_with_missing_auth(generic_experiment: str):
    with requests_mock.mock() as m:
        m.get('http://example.com/experiment.json', status_code=401)
        with pytest.raises(InvalidSource):
            load_experiment('http://example.com/experiment.json')


def test_load_from_http_with_auth(settings: Settings, generic_experiment: str):
    with requests_mock.mock() as m:
        settings['auths'] = {
            'example.com': {
                'type': 'bearer',
                'value': 'XYZ'
            }
        }
        m.get(
            'http://example.com/experiment.json', status_code=200,
            request_headers={
                "Authorization": "bearer XYZ",
                "Accept": "application/json, application/x-yaml"
            },
            headers={"Content-Type": "application/json"},
            json=json.dumps(generic_experiment))
        try:
            load_experiment('http://example.com/experiment.json', settings)
        except InvalidSource as x:
            pytest.fail(str(x))


def test_yaml_safe_load_from_file():
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(experiments.UnsafeYamlExperiment.encode('utf-8'))
        f.seek(0)

        with pytest.raises(InvalidSource):
            parse_experiment_from_file(f.name)


def test_yaml_safe_load_from_http():
    with requests_mock.mock() as m:
        m.get(
            'http://example.com/experiment.yaml', status_code=200,
            headers={"Content-Type": "application/x-yaml"},
            text=experiments.UnsafeYamlExperiment
        )
        with pytest.raises(InvalidSource):
            load_experiment('http://example.com/experiment.yaml')


def test_can_load_json_from_plain_text_http():
    with requests_mock.mock() as m:
        m.get(
            'http://example.com/experiment.yaml', status_code=200,
            headers={"Content-Type": "text/plain; charset=utf-8"},
            text=experiments.YamlExperiment
        )
        try:
            load_experiment('http://example.com/experiment.yaml')
        except InvalidExperiment as x:
            pytest.fail(str(x))


def test_can_load_yaml_from_plain_text_http(generic_experiment: str):
    with requests_mock.mock() as m:
        m.get(
            'http://example.com/experiment.json', status_code=200,
            headers={"Content-Type": "text/plain; charset=utf-8"},
            text=json.dumps(generic_experiment)
        )
        try:
            load_experiment('http://example.com/experiment.json')
        except InvalidExperiment as x:
            pytest.fail(str(x))


def test_http_loads_fails_when_known_type():
    with requests_mock.mock() as m:
        m.get(
            'http://example.com/experiment.yaml', status_code=200,
            headers={"Content-Type": "text/css"},
            text="body {}"
        )
        with pytest.raises(InvalidExperiment):
            load_experiment('http://example.com/experiment.yaml')


def test_https_no_verification():
    with requests_mock.mock() as m:
        m.get(
            'https://example.com/experiment.yaml', status_code=200,
            headers={"Content-Type": "text/css"},
            text="body {}"
        )
        with pytest.raises(InvalidExperiment):
            load_experiment(
                'https://example.com/experiment.yaml', verify_tls=False)


def test_https_with_verification():
    with requests_mock.mock() as m:
        m.get(
            'https://example.com/experiment.yaml',
            exc=requests.exceptions.SSLError
        )
        with pytest.raises(requests.exceptions.SSLError):
            load_experiment(
                'https://example.com/experiment.yaml', verify_tls=True)
