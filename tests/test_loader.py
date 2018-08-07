# -*- coding: utf-8 -*-
import json
import pytest
import requests_mock

from chaoslib.exceptions import InvalidSource
from chaoslib.loader import load_experiment
from chaoslib.types import Settings


def test_load_from_file(generic_experiment: str):
    try:
        load_experiment(generic_experiment)
    except InvalidSource as x:
        pytest.fail(str(x))


def test_load_invalid_filepath(generic_experiment: str):
    with pytest.raises(InvalidSource) as x:
        load_experiment("/tmp/xyuzye.txt")
    assert 'Path "/tmp/xyuzye.txt" does not exist.' in str(x)


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
        with pytest.raises(InvalidSource) as x:
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
            request_headers={"Authorization": "bearer XYZ"},
            headers={"Content-Type": "application/json"},
            json=json.dumps(generic_experiment))
        try:
            load_experiment('http://example.com/experiment.json', settings)
        except InvalidSource as x:
            pytest.fail(str(x))
