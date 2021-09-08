import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest
import requests_mock
from fixtures import config, experiments, probes

from chaoslib.activity import ensure_activity_is_valid, run_activity
from chaoslib.exceptions import ActivityFailed, InvalidActivity


def test_empty_probe_is_invalid():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.EmptyProbe)
    assert "empty activity is no activity" in str(exc.value)


def test_probe_must_have_a_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingTypeProbe)
    assert "an activity must have a type" in str(exc.value)


def test_probe_must_have_a_known_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.UnknownTypeProbe)
    assert "'whatever' is not a supported activity type" in str(exc.value)


def test_probe_provider_must_have_a_known_type():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.UnknownProviderTypeProbe)
    assert "unknown provider type 'pizza'" in str(exc.value)


def test_python_probe_must_have_a_module_path():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingModuleProbe)
    assert "a Python activity must have a module path" in str(exc.value)


def test_python_probe_must_have_a_function_name():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingFunctionProbe)
    assert "a Python activity must have a function name" in str(exc.value)


def test_python_probe_must_be_importable():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.NotImportableModuleProbe)
    assert "could not find Python module 'fake.module'" in str(exc.value)


def test_python_probe_func_must_have_enough_args():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingFuncArgProbe)
    assert "required argument 'path' is missing" in str(exc.value)


def test_python_probe_func_cannot_have_too_many_args():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.TooManyFuncArgsProbe)
    assert (
        "argument 'should_not_be_here' is not part of the "
        "function signature" in str(exc.value)
    )


def test_process_probe_have_a_path():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingProcessPathProbe)
    assert "a process activity must have a path" in str(exc.value)


def test_process_probe_path_must_exist():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.ProcessPathDoesNotExistProbe)
    assert "path 'somewhere/not/here' cannot be found, in activity" in str(exc.value)


def test_http_probe_must_have_a_url():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(probes.MissingHTTPUrlProbe)
    assert "a HTTP activity must have a URL" in str(exc.value)


def test_run_python_probe_should_return_raw_value():
    # our probe checks a file exists
    assert (
        run_activity(probes.PythonModuleProbe, config.EmptyConfig, experiments.Secrets)
        is True
    )


def test_run_process_probe_should_return_raw_value():
    v = "Python {v}\n".format(v=sys.version.split(" ")[0])

    result = run_activity(probes.ProcProbe, config.EmptyConfig, experiments.Secrets)
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == v
    assert result["stderr"] == ""


def test_run_process_probe_should_pass_arguments_in_array():
    args = (
        "['-c', '--empty', '--number', '1', '--string', 'with spaces', '--string',"
        " 'a second string with the same option']\n"
    )

    result = run_activity(
        probes.ProcEchoArrayProbe, config.EmptyConfig, experiments.Secrets
    )
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == args
    assert result["stderr"] == ""


def test_run_process_probe_can_pass_arguments_as_string():
    args = (
        "['-c', '--empty', '--number', '1', '--string', 'with spaces', "
        "'--string', 'a second string with the same option']\n"
    )

    result = run_activity(
        probes.ProcEchoStrProbe, config.EmptyConfig, experiments.Secrets
    )
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == args
    assert result["stderr"] == ""


def test_run_process_probe_can_timeout():
    probe = probes.ProcProbe
    probe["provider"]["timeout"] = 0.0001

    with pytest.raises(ActivityFailed) as exc:
        run_activity(probes.ProcProbe, config.EmptyConfig, experiments.Secrets).decode(
            "utf-8"
        )
    assert "activity took too long to complete" in str(exc.value)


def test_run_http_probe_should_return_parsed_json_value():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post("http://example.com", json=["well done"], headers=headers)
        result = run_activity(probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == ["well done"]


def test_run_http_probe_must_be_serializable_to_json():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post("http://example.com", json=["well done"], headers=headers)
        result = run_activity(probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert json.dumps(result) is not None


def test_run_http_probe_should_return_raw_text_value():
    with requests_mock.mock() as m:
        m.post("http://example.com", text="['well done']")
        result = run_activity(probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == "['well done']"


def test_run_http_probe_can_expect_failure():
    with requests_mock.mock() as m:
        m.post("http://example.com", status_code=404, text="Not found!")

        probe = probes.HTTPProbe.copy()
        probe["provider"]["expected_status"] = 404

        try:
            run_activity(probe, config.EmptyConfig, experiments.Secrets)
        except ActivityFailed:
            pytest.fail("activity should not have failed")


def test_run_http_probe_can_retry():
    """
    this test embeds a fake HTTP server to test the retry part
    it can't be easily tested with libraries like requests_mock or responses
    we could mock urllib3 retry mechanism as it is used in the requests library but it
    implies to understand how requests works which is not the idea of this test

    in this test, the first call will lead to a ConnectionAbortedError and the second
    will work
    """

    class MockServerRequestHandler(BaseHTTPRequestHandler):
        """
        mock of a real HTTP server to simulate the behavior of
        a connection aborted error on first call
        """

        call_count = 0

        def do_GET(self):
            MockServerRequestHandler.call_count += 1
            if MockServerRequestHandler.call_count == 1:
                raise ConnectionAbortedError
            self.send_response(200)
            self.end_headers()
            return

    # get a free port to listen on
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()

    # start the fake HTTP server in a dedicated thread on the selected port
    server = HTTPServer(("localhost", port), MockServerRequestHandler)
    t = Thread(target=server.serve_forever)
    t.setDaemon(True)
    t.start()

    # change probe URL to call the selected port
    probe = probes.PythonModuleProbeWithHTTPMaxRetries.copy()
    probe["provider"]["url"] = f"http://localhost:{port}"
    try:
        run_activity(probe, config.EmptyConfig, experiments.Secrets)
    except ActivityFailed:
        pytest.fail("activity should not have failed")
