import json
import os
import tempfile

import yaml

from chaoslib import merge_vars


def test_can_load_config_from_one_single_var():
    config_vars, secret_vars = merge_vars(var={"message": "hello world"})
    assert secret_vars == {}
    assert config_vars == {"message": "hello world"}


def test_can_load_config_from_many_vars():
    config_vars, secret_vars = merge_vars(
        var={
            "message": "hello world",
            "lang": "en"
        }
    )
    assert secret_vars == {}
    assert config_vars == {
        "message": "hello world",
        "lang": "en"
    }


def test_can_load_config_from_json_file():
    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        f.write(json.dumps({
            "configuration": {
                "message": "hello world",
                "lang": "en"
            }
        }).encode('utf-8'))
        f.seek(0)
        config_vars, secret_vars = merge_vars(
            var_files=[f.name]
        )
        assert secret_vars == {}
        assert config_vars == {
            "message": "hello world",
            "lang": "en"
        }


def test_can_load_config_from_yaml_file():
    with tempfile.NamedTemporaryFile(suffix='.yaml') as f:
        f.write(yaml.dump({
            "configuration": {
                "message": "hello world",
                "lang": "en"
            }
        }).encode('utf-8'))
        f.seek(0)
        config_vars, secret_vars = merge_vars(
            var_files=[f.name]
        )
        assert secret_vars == {}
        assert config_vars == {
            "message": "hello world",
            "lang": "en"
        }


def test_can_load_environ_from_dotenv():
    try:
        with tempfile.NamedTemporaryFile(suffix='.env') as f:
            f.write(b"""
TEST_MESSAGE=hello world
TEST_LANG=en
            """)
            f.seek(0)
            config_vars, secret_vars = merge_vars(
                var_files=[f.name]
            )
            assert secret_vars == {}
            assert config_vars == {}
            assert "TEST_MESSAGE" in os.environ
            assert "TEST_LANG" in os.environ
    finally:
        os.environ.pop("TEST_MESSAGE", None)
        os.environ.pop("TEST_LANG", None)


def test_can_load_config_from_many_files_at_once():
    with tempfile.TemporaryDirectory() as d:
        json_file = os.path.join(d, 'env.json')
        with open(json_file, 'w') as f:
            f.write(json.dumps({
                "configuration": {
                    "message": "hello world"
                }
            }))

        yaml_file = os.path.join(d, 'env.yaml')
        with open(yaml_file, 'w') as f:
            f.write(yaml.dump({
                "configuration": {
                    "lang": "en"
                }
            }))

        config_vars, secret_vars = merge_vars(
            var_files=[json_file, yaml_file]
        )
        assert secret_vars == {}
        assert config_vars == {
            "message": "hello world",
            "lang": "en"
        }


def test_can_load_config_from_many_files_at_once_and_override():
    with tempfile.TemporaryDirectory() as d:
        json_file = os.path.join(d, 'env.json')
        with open(json_file, 'w') as f:
            f.write(json.dumps({
                "configuration": {
                    "message": "hello world",
                    "lang": "en"
                }
            }))

        yaml_file = os.path.join(d, 'env.yaml')
        with open(yaml_file, 'w') as f:
            f.write(yaml.dump({
                "configuration": {
                    "lang": "en-us"
                }
            }))

        config_vars, secret_vars = merge_vars(
            var_files=[json_file, yaml_file]
        )
        assert secret_vars == {}
        assert config_vars == {
            "message": "hello world",
            "lang": "en-us"
        }


def test_can_load_config_is_overriden_by_vars():
    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        f.write(json.dumps({
            "configuration": {
                "message": "hello world",
                "lang": "en"
            }
        }).encode('utf-8'))
        f.seek(0)
        config_vars, secret_vars = merge_vars(
            var={
                "message": "bonjour world"
            },
            var_files=[f.name]
        )
        assert secret_vars == {}
        assert config_vars == {
            "message": "bonjour world",
            "lang": "en"
        }


def test_can_load_config_and_secrets():
    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        f.write(json.dumps({
            "configuration": {
                "message": "hello world",
                "lang": "en"
            },
            "secrets": {
                "aws": {
                    "key": "test"
                }
            }
        }).encode('utf-8'))
        f.seek(0)
        config_vars, secret_vars = merge_vars(
            var_files=[f.name]
        )
        assert secret_vars == {
            "aws": {
                "key": "test"
            }
        }
        assert config_vars == {
            "message": "hello world",
            "lang": "en"
        }
