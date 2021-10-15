import threading
import time
from copy import deepcopy

import pytest
from fixtures import experiments

from chaoslib.exit import exit_gracefully, exit_ungracefully
from chaoslib.run import Runner
from chaoslib.types import Strategy


@pytest.mark.usefixtures("slow_service")
def test_play_rollbacks_on_graceful_exit_with_http_action():
    x = deepcopy(experiments.ExperimentGracefulExitLongHTTPCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 1


@pytest.mark.usefixtures("slow_service")
def test_do_not_play_rollbacks_on_graceful_exit_with_http_action():
    x = deepcopy(experiments.ExperimentUngracefulExitLongHTTPCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 0


def test_play_rollbacks_on_graceful_exit_with_process_action():
    x = deepcopy(experiments.ExperimentGracefulExitLongProcessCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 1


def test_do_not_play_rollbacks_on_graceful_exit_with_process_action():
    x = deepcopy(experiments.ExperimentUngracefulExitLongProcessCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 0


def test_play_rollbacks_on_graceful_exit_with_python_action():
    x = deepcopy(experiments.ExperimentGracefulExitLongPythonCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 1


@pytest.mark.usefixtures("slow_service")
def test_do_not_play_rollbacks_on_graceful_exit_with_python_action():
    x = deepcopy(experiments.ExperimentUngracefulExitLongHTTPCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(
            x, settings={"runtime": {"rollbacks": {"strategy": "always"}}}
        )

        assert journal["status"] == "interrupted"
        assert len(journal["rollbacks"]) == 0


@pytest.mark.usefixtures("slow_service")
def test_wait_for_background_activity_on_graceful_exit():
    x = deepcopy(experiments.ExperimentGracefulExitLongHTTPCall)
    with Runner(Strategy.DEFAULT) as runner:
        journal = runner.run(x)

        assert journal["status"] == "interrupted"
        assert 3.0 < journal["run"][0]["duration"] < 3.2


def test_do_not_wait_for_background_activity_on_ungraceful_exit():
    def _exit_soon():
        time.sleep(1.5)
        exit_ungracefully()

    t = threading.Thread(target=_exit_soon)

    x = deepcopy(experiments.SimpleExperimentWithBackgroundActivity)
    with Runner(Strategy.DEFAULT) as runner:
        t.start()
        journal = runner.run(x)
        assert journal["status"] == "interrupted"
        assert journal["run"][0]["status"] == "failed"
        assert "ExperimentExitedException" in journal["run"][0]["exception"][-1]


def test_wait_for_background_activity_to_finish_on_graceful_exit():
    def _exit_soon():
        time.sleep(1.5)
        exit_gracefully()

    t = threading.Thread(target=_exit_soon)

    x = deepcopy(experiments.SimpleExperimentWithBackgroundActivity)
    with Runner(Strategy.DEFAULT) as runner:
        t.start()
        journal = runner.run(x)
        assert journal["status"] == "interrupted"
        assert journal["run"][0]["status"] == "succeeded"
