# -*- coding: utf-8 -*-
import time
import types
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock

from chaoslib.notification import notify, DiscoverFlowEvent, InitFlowEvent, \
    RunFlowEvent, ValidateFlowEvent
from chaoslib.types import Experiment, EventPayload


def test_no_settings_is_okay():
    assert notify(None, DiscoverFlowEvent.DiscoverStarted) is None


def test_no_notifications_in_settings_is_okay():
    assert notify({}, DiscoverFlowEvent.DiscoverStarted) is None


def test_notify_to_http_endpoint():
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', status_code=200, json=event_payload)

        notify({
            "notifications": [
                {
                    "type": "http",
                    "url": "http://example.com"
                }
            ]
        }, RunFlowEvent.RunStarted)

        assert m.called


@patch('chaoslib.notification.logger', autospec=True)
def test_notify_to_http_endpoint_can_timeout(logger):
    url = "http://example.com"
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }

    exc_mock = requests.exceptions.ConnectTimeout()
    with requests_mock.mock() as m:
        m.post(url, exc=exc_mock)

        notify({
            "notifications": [
                {
                    "type": "http",
                    "url": url
                }
            ]
        }, RunFlowEvent.RunStarted)

        m = "failed calling notification endpoint"
        logger.debug.assert_called_with(
            m, exc_info=exc_mock)


@patch('chaoslib.notification.logger', autospec=True)
def test_notify_to_http_endpoint_requires_a_url(logger):
    url = "http://example.com"
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', status_code=200, json=event_payload)

        notify({
            "notifications": [
                {
                    "type": "http"
                }
            ]
        }, RunFlowEvent.RunStarted)

        m = "missing url in notification channel"
        logger.debug.assert_called_with(m)


@patch('chaoslib.notification.logger', autospec=True)
def test_notify_to_http_endpoint_may_fail(logger):
    url = "http://example.com"
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    with requests_mock.mock() as m:
        m.post('http://example.com', status_code=404, text="boom")

        notify({
            "notifications": [
                {
                    "type": "http",
                    "url": url
                }
            ]
        }, RunFlowEvent.RunStarted)

        m = "Notification sent to '{u}' failed with '{t}'".format(
            u=url, t="boom"
        )
        logger.debug.assert_called_with(m)


@patch('fixtures.notifier.logger', autospec=True)
def test_notify_via_plugin(logger):
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    notify({
        "notifications": [
            {
                "type": "plugin",
                "module": "fixtures.notifier"
            }
        ]
    }, RunFlowEvent.RunStarted)
    logger.debug.assert_called_with("boom")


@patch('fixtures.notifier.logger', autospec=True)
def test_notify_via_plugin_with_non_default_func_name(logger):
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    notify({
        "notifications": [
            {
                "type": "plugin",
                "module": "fixtures.notifier",
                "func": "notify_other"
            }
        ]
    }, RunFlowEvent.RunStarted)
    logger.debug.assert_called_with("doh")


@patch('chaoslib.notification.logger', autospec=True)
def test_notify_via_plugin_failed_to_import_plugin(logger):
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    notify({
        "notifications": [
            {
                "type": "plugin",
                "module": "fixtures.notifier___"
            }
        ]
    }, RunFlowEvent.RunStarted)

    logger.debug.assert_called_with(
        "could not find Python plugin '{mod}' for notification".format(
            mod="fixtures.notifier___"))


@patch('chaoslib.notification.logger', autospec=True)
def test_notify_via_plugin_failed_to_import_func(logger):
    payload = {
        "msg": "hello",
        "ts": str(time.time())
    }
    event_payload = {
        "event": str(RunFlowEvent.RunStarted),
        "payload": payload
    }
    notify({
        "notifications": [
            {
                "type": "plugin",
                "module": "fixtures.notifier",
                "func": "blah"
            }
        ]
    }, RunFlowEvent.RunStarted)

    logger.debug.assert_called_with(
        "could not find function '{f}' in plugin '{mod}' "
        "for notification".format(mod="fixtures.notifier", f="blah"))
