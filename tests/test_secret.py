# -*- coding: utf-8 -*-
import os

import pytest
from chaoslib.secret import load_secrets, create_vault_client
from fixtures import config
from unittest.mock import ANY, MagicMock, patch

def test_should_load_environment():
    os.environ["KUBE_API_URL"] = "http://1.2.3.4"
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


def test_should_load_inline():
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": "http://1.2.3.4"
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


def test_should_merge_properly():
    secrets = load_secrets({
        "kubernetes": {
            "username": "jane",
            "address": {"host": "whatever", "port": 8090},
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["username"] == "jane"
    assert secrets["kubernetes"]["address"]["host"] == "whatever"
    assert secrets["kubernetes"]["address"]["port"] == 8090
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


@patch('chaoslib.secret.hvac')
def test_should_auth_with_approle(hvac):
    config = {
        'vault_addr' : 'http://someaddr.com',
        'vault_role_id' : 'mighty_id',
        'vault_role_secret' : 'secret_secret'
    }

    fake_auth_object = {
        'auth' : {
            'client_token' : 'awesome_token'
        }
    }

    fake_client = MagicMock()
    fake_client.auth_approle.return_value = fake_auth_object
    hvac.Client.return_value = fake_client

    vault_client = create_vault_client(config)

    assert vault_client.token == fake_auth_object['auth']['client_token']
    fake_client.auth_approle.assert_called_with(config['vault_role_id'], config['vault_role_secret'])


@patch('chaoslib.secret.hvac')
def test_should_auth_with_token(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client

    vault_client = create_vault_client(config)

    assert vault_client.token == config['vault_token']
    fake_client.auth_approle.assert_not_called()