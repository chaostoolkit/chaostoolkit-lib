from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import callee
import requests
import responses
from freezegun import freeze_time

from chaoslib.exceptions import ChaosException
from chaoslib.notification import (
    DiscoverFlowEvent,
    InitFlowEvent,
    RunFlowEvent,
    ValidateFlowEvent,
    notify,
    notify_with_http,
)


def test_no_settings_is_okay() -> None:
    assert notify(None, DiscoverFlowEvent.DiscoverStarted) is None


def test_no_notifications_in_settings_is_okay() -> None:
    assert notify({"things": "stuff"}, DiscoverFlowEvent.DiscoverStarted) is None


@freeze_time("2020-01-01 00:00")
@patch("chaoslib.notification.notify_with_http")
def test_notify_calls_notify_with_http_when_type_is_http(
    mock_notify_with_http: MagicMock,
) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()
    payload = {"test-key": "test-value", "test-dict": {"test-dict-key": "test"}}
    channel = {"type": "http", "url": "http://example.com"}

    notify(
        settings={"notifications": [channel]},
        event=RunFlowEvent.RunStarted,
        payload=payload,
    )

    mock_notify_with_http.assert_called_once_with(
        channel,
        {
            "name": RunFlowEvent.RunStarted.value,
            "payload": payload,
            "phase": "run",
            "ts": now,
        },
    )


@patch("chaoslib.notification.logger", autospec=True)
def test_notify_with_http_requires_a_url(mock_logger: MagicMock) -> None:
    notify_with_http(channel={"type": "http", "url": ""}, payload={})
    mock_logger.debug.assert_called_with("missing url in notification channel")


@patch("chaoslib.notification.logger")
@patch("chaoslib.notification.requests")
def test_notify_with_http_gracefully_handles_exceptions(
    mock_requests: MagicMock, mock_logger: MagicMock
) -> None:
    exception = requests.exceptions.RequestException("An Exception")
    mock_requests.get.side_effect = exception
    notify_with_http(
        channel={
            "type": "http",
            "url": "http://test-url.com",
            "forward_event_payload": False,
        },
        payload={},
    )
    mock_logger.debug.assert_called_once_with(
        "failed calling notification endpoint", exc_info=exception
    )


@responses.activate
@patch("chaoslib.notification.logger")
def test_notify_with_http_handles_400_500_responses(mock_logger: MagicMock) -> None:
    test_400_url = "http://test-400-url.com"
    test_500_url = "http://test-500-url.com"
    responses.add(method=responses.GET, url=test_400_url, status=400)
    responses.add(method=responses.GET, url=test_500_url, status=500)
    notify_with_http(
        channel={"type": "http", "url": test_400_url, "forward_event_payload": False},
        payload={},
    )
    mock_logger.debug.assert_called_with(
        (
            f"notification sent to {test_400_url} failed with: "
            "400 Client Error: Bad Request for url: http://test-400-url.com/"
        )
    )
    notify_with_http(
        channel={"type": "http", "url": test_500_url, "forward_event_payload": False},
        payload={},
    )
    mock_logger.debug.assert_called_with(
        (
            f"notification sent to {test_500_url} failed with: "
            "500 Server Error: Internal Server Error for url: http://test-500-url.com/"
        )
    )


@responses.activate
@patch("chaoslib.notification.logger")
def test_notify_with_http_will_forward_event_payload(mock_logger: MagicMock) -> None:
    test_url = "http://test-post-url.com"
    test_payload = {"test-key": "test-val", "test-dict": {"test-key-2": "test-val-2"}}
    responses.add(
        method=responses.POST,
        url=test_url,
        match=[responses.matchers.json_params_matcher(test_payload)],
    )
    notify_with_http(channel={"type": "http", "url": test_url}, payload=test_payload)
    mock_logger.debug.assert_not_called()


@responses.activate
@patch("chaoslib.notification.logger")
def test_notify_with_http_wont_forward_event_payload(mock_logger: MagicMock) -> None:
    test_url = "http://test-post-url.com"
    test_payload = {"test-key": "test-val", "test-dict": {"test-key-2": "test-val-2"}}
    responses.add(
        method=responses.GET,
        url=test_url,
    )
    notify_with_http(
        channel={"type": "http", "url": test_url, "forward_event_payload": False},
        payload=test_payload,
    )
    mock_logger.debug.assert_not_called()


@responses.activate
@freeze_time("2021-01-01 00:00")
@patch("chaoslib.notification.logger")
def test_notify_with_http_handles_datetimes_present_in_payload(
    mock_logger: MagicMock,
) -> None:
    test_url = "http://test-datetime-url.com"
    now = datetime.now()
    now_timestamp = now.isoformat()
    test_payload = {"test-key": "test-val", "test-datetime": now}
    test_json_payload = {"test-key": "test-val", "test-datetime": now_timestamp}
    responses.add(
        method=responses.POST,
        url=test_url,
        match=[responses.matchers.json_params_matcher(test_json_payload)],
    )
    notify_with_http(channel={"type": "http", "url": test_url}, payload=test_payload)
    mock_logger.debug.assert_not_called()


@responses.activate
@patch("chaoslib.notification.logger")
def test_notify_with_http_handles_error_present_in_payload(
    mock_logger: MagicMock,
) -> None:
    test_url = "http://test-error-url.com"
    exception = ChaosException("Something went wrong here")
    test_payload = {"test-key": "test-val", "error": exception}
    test_json_payload = {
        "test-key": "test-val",
        "error": "An exception was raised: ChaosException('Something went wrong here')",
    }
    responses.add(
        method=responses.POST,
        url=test_url,
        match=[responses.matchers.json_params_matcher(test_json_payload)],
    )
    notify_with_http(channel={"type": "http", "url": test_url}, payload=test_payload)
    mock_logger.debug.assert_not_called()


@freeze_time("2021-01-01 00:00")
@patch("chaoslib.notification.notify_with_http")
def test_notify_correctly_assigns_phase_from_event_class(
    mock_notify_with_http: MagicMock,
) -> None:
    channel = {"type": "http", "url": "http://example.com"}
    for phase, event_class in [
        ("discovery", DiscoverFlowEvent.DiscoverStarted),
        ("init", InitFlowEvent.InitStarted),
        ("run", RunFlowEvent.RunStarted),
        ("validate", ValidateFlowEvent.ValidateStarted),
    ]:
        mock_notify_with_http.reset_mock()
        notify(settings={"notifications": [channel]}, event=event_class, payload=None)
        mock_notify_with_http.assert_called_once_with(
            channel,
            {
                "name": event_class.value,
                "payload": None,
                "phase": phase,
                "ts": datetime.utcnow().replace(tzinfo=timezone.utc).timestamp(),
            },
        )


@freeze_time("2021-01-01 00:00")
@patch("chaoslib.notification.notify_with_http")
def test_notify_appends_error_to_event_payload_if_provided(
    mock_notify_with_http: MagicMock,
) -> None:
    channel = {"type": "http", "url": "http://example.com"}
    exception = ChaosException("Something went wrong")
    notify(
        settings={"notifications": [channel]},
        event=DiscoverFlowEvent.DiscoverStarted,
        payload=None,
        error=exception,
    )
    mock_notify_with_http.assert_called_once_with(
        channel,
        {
            "name": DiscoverFlowEvent.DiscoverStarted.value,
            "payload": None,
            "phase": "discovery",
            "ts": datetime.utcnow().replace(tzinfo=timezone.utc).timestamp(),
            "error": exception,
        },
    )


@freeze_time("2021-01-01 00:00")
@patch("chaoslib.notification.notify_with_http")
def test_notify_only_notifies_on_events_specified(
    mock_notify_with_http: MagicMock,
) -> None:
    channel = {
        "type": "http",
        "url": "http://example.com",
        "events": ["discover-started"],
    }
    notify(
        settings={"notifications": [channel]},
        event=RunFlowEvent.RunFailed,
        payload=None,
    )
    mock_notify_with_http.assert_not_called()


@freeze_time("2020-01-01 00:00")
@patch("chaoslib.notification.notify_via_plugin")
def test_notify_calls_notify_via_plugin_when_type_is_plugin(
    mock_notify_via_plugin: MagicMock,
) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()
    payload = {"test-key": "test-value", "test-dict": {"test-dict-key": "test"}}
    channel = {"type": "plugin", "module": "fixtures.notifier"}

    notify(
        settings={"notifications": [channel]},
        event=RunFlowEvent.RunStarted,
        payload=payload,
    )

    mock_notify_via_plugin.assert_called_once_with(
        channel,
        {
            "name": RunFlowEvent.RunStarted.value,
            "payload": payload,
            "phase": "run",
            "ts": now,
        },
    )


@patch("fixtures.notifier.logger", autospec=True)
def test_notify_via_plugin_correctly_invokes_notify_func(logger: MagicMock) -> None:
    notify(
        {"notifications": [{"type": "plugin", "module": "fixtures.notifier"}]},
        RunFlowEvent.RunStarted,
    )
    logger.debug.assert_called_with("boom")


@patch("fixtures.notifier.logger", autospec=True)
def test_notify_via_plugin_correctly_invokes_notify_func_with_non_default_func_name(
    logger: MagicMock,
) -> None:
    notify(
        {
            "notifications": [
                {
                    "type": "plugin",
                    "module": "fixtures.notifier",
                    "func": "notify_other",
                }
            ]
        },
        RunFlowEvent.RunStarted,
    )
    logger.debug.assert_called_with("doh")


@patch("chaoslib.notification.logger", autospec=True)
def test_notify_via_plugin_gracefully_handles_failure_to_import_plugin(
    logger: MagicMock,
) -> None:
    notify(
        {"notifications": [{"type": "plugin", "module": "fixtures.notifier___"}]},
        RunFlowEvent.RunStarted,
    )

    logger.debug.assert_called_with(
        "could not find Python plugin '{mod}' for notification".format(
            mod="fixtures.notifier___"
        )
    )


@patch("chaoslib.notification.logger", autospec=True)
def test_notify_via_plugin_gracefully_handles_failure_to_import_func(
    logger: MagicMock,
) -> None:
    notify(
        {
            "notifications": [
                {"type": "plugin", "module": "fixtures.notifier", "func": "blah"}
            ]
        },
        RunFlowEvent.RunStarted,
    )

    logger.debug.assert_called_with(
        "could not find function '{f}' in plugin '{mod}' "
        "for notification".format(mod="fixtures.notifier", f="blah")
    )


@patch("chaoslib.notification.logger", autospec=True)
def test_notify_via_plugin_gracefully_handles_failure_in_invoked_func(
    logger: MagicMock,
) -> None:
    notify(
        {
            "notifications": [
                {
                    "type": "plugin",
                    "module": "fixtures.notifier",
                    "func": "notify_broken",
                }
            ]
        },
        RunFlowEvent.RunStarted,
    )

    logger.debug.assert_called_with(
        "failed calling notification plugin", exc_info=callee.InstanceOf(Exception)
    )
