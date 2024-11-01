import os
from unittest.mock import patch

from tests.fixtures import config
from chaoslib.secret import load_secrets


@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_should_load_environment():
    secrets = load_secrets(
        {
            "kubernetes": {
                "api_server_url": {"type": "env", "key": "KUBE_API_URL"}
            }
        },
        config.EmptyConfig,
    )
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_should_load_nested_environment():
    secrets = load_secrets(
        {
            "kubernetes": {
                "env1": {
                    "username": "jane",
                    "address": {"host": "whatever", "port": 8090},
                    "api_server_url": {"type": "env", "key": "KUBE_API_URL"},
                }
            }
        },
        config.EmptyConfig,
    )
    assert secrets["kubernetes"]["env1"]["username"] == "jane"
    assert secrets["kubernetes"]["env1"]["address"]["host"] == "whatever"
    assert secrets["kubernetes"]["env1"]["address"]["port"] == 8090
    assert secrets["kubernetes"]["env1"]["api_server_url"] == "http://1.2.3.4"


def test_should_load_inline():
    secrets = load_secrets(
        {"kubernetes": {"api_server_url": "http://1.2.3.4"}}, config.EmptyConfig
    )
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_should_merge_properly():
    secrets = load_secrets(
        {
            "kubernetes": {
                "username": "jane",
                "address": {"host": "whatever", "port": 8090},
                "api_server_url": {"type": "env", "key": "KUBE_API_URL"},
            }
        },
        config.EmptyConfig,
    )
    assert secrets["kubernetes"]["username"] == "jane"
    assert secrets["kubernetes"]["address"]["host"] == "whatever"
    assert secrets["kubernetes"]["address"]["port"] == 8090
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"
