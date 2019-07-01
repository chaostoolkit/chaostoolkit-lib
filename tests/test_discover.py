# -*- coding: utf-8 -*-
import types

import pytest

from chaoslib.exceptions import DiscoveryFailed
from chaoslib.discovery import discover, initialize_discovery_result
from chaoslib.discovery.discover import discover_activities
from chaoslib.types import Discovery, DiscoveredActivities, \
    DiscoveredSystemInfo


def test_fail_discovery_when_module_cannot_be_loaded():
    with pytest.raises(DiscoveryFailed) as exc:
        discover_activities("fixtures.burp", "probe")
    assert "could not import extension module" in str(exc.value)


def test_do_not_fail_when_extension_mod_has_not_all():
    activities = discover_activities("fixtures.keepempty", "probe")
    assert len(activities) == 0


def test_discover_all_activities():
    mod = "fixtures.fakeext"
    activities = discover_activities(mod, "probe")
    assert len(activities) == 8

    activities = iter(activities)

    activity = next(activities)
    assert activity["name"] == "many_args"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "Many arguments."
    assert activity["arguments"] == [
        {
            "name": "message",
            "type": "string"
        },
        {
            "name": "colour",
            "default": "blue",
            "type": "string"
        }
    ]

    activity = next(activities)
    assert activity["name"] == "many_args_with_rich_types"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "Many arguments with rich types."
    assert activity["arguments"] == [
        {
            "name": "message",
            "type": "string"
        },
        {
            "name": "recipients",
            "type": "list"
        },
        {
            "name": "colour",
            "default": "blue",
            "type": "string"
        },
        {
            "name": "count",
            "default": 1,
            "type": "integer"
        },
        {
            "name": "logit",
            "default": False,
            "type": "boolean"
        },
        {
            "name": "other",
            "default": None,
            "type": "object"
        }
    ]

    activity = next(activities)
    assert activity["name"] == "no_args"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "No arguments."
    assert activity["arguments"] == []

    activity = next(activities)
    assert activity["name"] == "no_args_docstring"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == None
    assert activity["arguments"] == []

    activity = next(activities)
    assert activity["name"] == "one_arg"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "One typed argument."
    assert activity["arguments"] == [
        {
            "name": "message",
            "type": "string"
        }
    ]

    activity = next(activities)
    assert activity["name"] == "one_arg_with_default"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "One typed argument with a default value."
    assert activity["arguments"] == [
        {
            "name": "message",
            "default": "hello",
            "type": "string"
        }
    ]

    activity = next(activities)
    assert activity["name"] == "one_untyped_arg"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "One untyped argument."
    assert activity["arguments"] == [
        {
            "name": "message"
        }
    ]

    activity = next(activities)
    assert activity["name"] == "one_untyped_arg_with_default"
    assert activity["type"] == "probe"
    assert activity["mod"] == mod
    assert activity["doc"] == "One untyped argument with a default value."
    assert activity["arguments"] == [
        {
            "name": "message",
            "default": "hello"
        }
    ]
