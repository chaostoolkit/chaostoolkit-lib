from typing import Any, Dict
from chaoslib.run import RunEventHandler
from chaoslib.types import Experiment, Journal


class FullRunEventHandler(RunEventHandler):
    def __init__(self):
        self.calls = []

    def started(self, experiment: Experiment, journal: Journal) -> None:
        self.calls.append("started")

    def finish(self, journal: Journal) -> None:
        self.calls.append("finish")

    def interrupted(self, experiment: Experiment,
                    journal: Journal) -> None:
        self.calls.append("interrupted")

    def signal_exit(self) -> None:
        self.calls.append("signal_exit")

    def start_continuous_hypothesis(self, frequency: int) -> None:
        self.calls.append("start_continuous_hypothesis")

    def continuous_hypothesis_iteration(self, iteration_index: int,
                                       state: Any) -> None:
        self.calls.append("continuous_hypothesis_iteration")

    def continuous_hypothesis_completed(self, experiment: Experiment,
                                       journal: Journal,
                                       exception: Exception = None) -> None:
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

    def hypothesis_before_completed(self, experiment: Experiment,
                                    state: Dict[str, Any],
                                    journal: Journal) -> None:
        self.calls.append("hypothesis_before_completed")

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        self.calls.append("start_hypothesis_after")

    def hypothesis_after_completed(self, experiment: Experiment,
                                   state: Dict[str, Any],
                                   journal: Journal) -> None:
        self.calls.append("hypothesis_after_completed")

    def start_cooldown(self, duration: int) -> None:
        self.calls.append("start_cooldown")

    def cooldown_completed(self) -> None:
        self.calls.append("cooldown_completed")


class FullExceptionRunEventHandler(RunEventHandler):
    def __init__(self):
        self.calls = []

    def started(self, experiment: Experiment, journal: Journal) -> None:
        raise Exception()

    def finish(self, journal: Journal) -> None:
        raise Exception()

    def interrupted(self, experiment: Experiment,
                    journal: Journal) -> None:
        raise Exception()

    def signal_exit(self) -> None:
        raise Exception()

    def start_continuous_hypothesis(self, frequency: int) -> None:
        raise Exception()

    def continuous_hypothesis_iteration(self, iteration_index: int,
                                       state: Any) -> None:
        raise Exception()

    def continuous_hypothesis_completed(self) -> None:
        raise Exception()

    def start_rollbacks(self, experiment: Experiment) -> None:
        raise Exception()

    def rollbacks_completed(self, experiment: Experiment, state: Any) -> None:
        raise Exception()

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        raise Exception()

    def hypothesis_before_completed(self, experiment: Experiment,
                                    state: Dict[str, Any],
                                    journal: Journal) -> None:
        raise Exception()

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        self.calls.append("start_hypothesis_after")

    def hypothesis_after_completed(self, experiment: Experiment,
                                   state: Dict[str, Any],
                                   journal: Journal) -> None:
        raise Exception()

    def start_method(self, iteration_index: int = 0) -> None:
        raise Exception()

    def method_completed(self, state: Any,
                            iteration_index: int = 0) -> None:
        raise Exception()

    def start_cooldown(self, duration: int) -> None:
        raise Exception()

    def cooldown_completed(self) -> None:
        raise Exception()
