from typing import Any

from chaoslib.run import RunEventHandler
from chaoslib.types import (
    Activity,
    Configuration,
    Experiment,
    Journal,
    Run,
    Schedule,
    Secrets,
    Settings,
)


class FullRunEventHandler(RunEventHandler):
    def __init__(self):
        self.calls = []

    def started(self, experiment: Experiment, journal: Journal) -> None:
        self.calls.append("started")

    def running(
        self,
        experiment: Experiment,
        journal: Journal,
        configuration: Configuration,
        secrets: Secrets,
        schedule: Schedule,
        settings: Settings,
    ) -> None:
        self.calls.append("running")

    def finish(self, journal: Journal) -> None:
        self.calls.append("finish")

    def interrupted(self, experiment: Experiment, journal: Journal) -> None:
        self.calls.append("interrupted")

    def signal_exit(self) -> None:
        self.calls.append("signal_exit")

    def start_continuous_hypothesis(self, frequency: int) -> None:
        self.calls.append("start_continuous_hypothesis")

    def continuous_hypothesis_iteration(
        self, iteration_index: int, state: Any
    ) -> None:
        self.calls.append("continuous_hypothesis_iteration")

    def continuous_hypothesis_completed(
        self,
        experiment: Experiment,
        journal: Journal,
        exception: Exception | None = None,
    ) -> None:
        self.calls.append("continuous_hypothesis_completed")

    def start_method(self, experiment: Experiment) -> None:
        self.calls.append("start_method")

    def method_completed(self, experiment: Experiment, state: Any) -> None:
        self.calls.append("method_completed")

    def start_rollbacks(self, experiment: Experiment) -> None:
        self.calls.append("start_rollbacks")

    def rollbacks_completed(self, experiment: Experiment, state: Any) -> None:
        self.calls.append("rollbacks_completed")

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        self.calls.append("start_hypothesis_before")

    def hypothesis_before_completed(
        self, experiment: Experiment, state: dict[str, Any], journal: Journal
    ) -> None:
        self.calls.append("hypothesis_before_completed")

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        self.calls.append("start_hypothesis_after")

    def hypothesis_after_completed(
        self, experiment: Experiment, state: dict[str, Any], journal: Journal
    ) -> None:
        self.calls.append("hypothesis_after_completed")

    def start_cooldown(self, duration: int) -> None:
        self.calls.append("start_cooldown")

    def cooldown_completed(self) -> None:
        self.calls.append("cooldown_completed")

    def start_activity(self, activity: Activity) -> None:
        self.calls.append("start_activity")

    def activity_completed(self, activity: Activity, run: Run) -> None:
        self.calls.append("activity_completed")


class RunEventHandlerError(Exception):
    pass


class FullExceptionRunEventHandler(RunEventHandler):
    def __init__(self):
        self.calls = []

    def started(self, experiment: Experiment, journal: Journal) -> None:
        raise RunEventHandlerError()

    def finish(self, journal: Journal) -> None:
        raise RunEventHandlerError()

    def interrupted(self, experiment: Experiment, journal: Journal) -> None:
        raise RunEventHandlerError()

    def signal_exit(self) -> None:
        raise RunEventHandlerError()

    def start_continuous_hypothesis(self, frequency: int) -> None:
        raise RunEventHandlerError()

    def continuous_hypothesis_iteration(
        self, iteration_index: int, state: Any
    ) -> None:
        raise RunEventHandlerError()

    def continuous_hypothesis_completed(self) -> None:
        raise RunEventHandlerError()

    def start_rollbacks(self, experiment: Experiment) -> None:
        raise RunEventHandlerError()

    def rollbacks_completed(self, experiment: Experiment, state: Any) -> None:
        raise RunEventHandlerError()

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        raise RunEventHandlerError()

    def hypothesis_before_completed(
        self, experiment: Experiment, state: dict[str, Any], journal: Journal
    ) -> None:
        raise RunEventHandlerError()

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        raise RunEventHandlerError()

    def hypothesis_after_completed(
        self, experiment: Experiment, state: dict[str, Any], journal: Journal
    ) -> None:
        raise RunEventHandlerError()

    def start_method(self, iteration_index: int = 0) -> None:
        raise RunEventHandlerError()

    def method_completed(self, state: Any, iteration_index: int = 0) -> None:
        raise RunEventHandlerError()

    def start_cooldown(self, duration: int) -> None:
        raise RunEventHandlerError()

    def cooldown_completed(self) -> None:
        raise RunEventHandlerError()

    def start_activity(self, activity: Activity) -> None:
        raise RunEventHandlerError()

    def activity_completed(self, activity: Activity, run: Run) -> None:
        raise RunEventHandlerError()
