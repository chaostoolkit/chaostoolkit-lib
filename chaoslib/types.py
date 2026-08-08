import enum
from typing import Any, Optional

__all__ = [
    "Action",
    "Activity",
    "ConfigVars",
    "Configuration",
    "Control",
    "DiscoveredActivities",
    "DiscoveredSystemInfo",
    "Discovery",
    "EventPayload",
    "Experiment",
    "Extension",
    "Hypothesis",
    "Journal",
    "Layer",
    "MicroservicesStatus",
    "Probe",
    "Run",
    "Schedule",
    "SecretVars",
    "Secrets",
    "Settings",
    "Step",
    "Strategy",
    "TargetLayers",
    "Tolerance",
]


Action = dict[str, Any]
Experiment = dict[str, Any]
Probe = dict[str, Any]

Activity = Probe | Action

Layer = Any
TargetLayers = dict[str, list[dict[str, Any]]]

MicroservicesStatus = tuple[dict[str, Any], dict[str, Any]]
Journal = dict[str, Any]
Run = dict[str, Any]
Step = dict[str, Any]

Secrets = dict[str, dict[str, str]]
Configuration = dict[str, dict[str, str]]

Discovery = dict[str, Any]
DiscoveredActivities = dict[str, Any]
DiscoveredSystemInfo = dict[str, Any]

Settings = dict[str, Any]
EventPayload = dict[str, Any]

Tolerance = int | str | bool | list | dict[str, Any]

Extension = dict[str, Any]
Hypothesis = dict[str, Any]
Control = dict[str, Any]

ConfigVars = dict[str, Any]
SecretVars = dict[str, Any]


class Strategy(enum.Enum):
    BEFORE_METHOD = "before-method-only"
    AFTER_METHOD = "after-method-only"
    DURING_METHOD = "during-method-only"
    DEFAULT = "default"
    CONTINUOUS = "continuous"
    SKIP = "skip"

    @staticmethod
    def from_string(value: str) -> "Strategy":
        if value == "default":
            return Strategy.DEFAULT
        elif value == "before-method-only":
            return Strategy.BEFORE_METHOD
        elif value == "after-method-only":
            return Strategy.AFTER_METHOD
        elif value == "during-method-only":
            return Strategy.DURING_METHOD
        elif value == "continuously":
            return Strategy.CONTINUOUS
        elif value == "skip":
            return Strategy.SKIP

        raise ValueError("Unknown strategy")


class Dry(enum.Enum):
    PROBES = "probes"
    ACTIONS = "actions"
    ACTIVITIES = "activities"
    PAUSE = "pause"

    @staticmethod
    def from_string(value: str) -> Optional["Dry"]:
        if value == "probes":
            return Dry.PROBES
        elif value == "actions":
            return Dry.ACTIONS
        elif value == "activities":
            return Dry.ACTIVITIES
        elif value == "pause":
            return Dry.PAUSE
        elif not value:
            return None

        raise ValueError("Unknown dry")


class Schedule:
    def __init__(
        self,
        continuous_hypothesis_frequency: float = 1.0,
        fail_fast: bool = False,
        fail_fast_ratio: float = 0,
    ):
        self.continuous_hypothesis_frequency = continuous_hypothesis_frequency
        self.fail_fast = fail_fast
        self.fail_fast_ratio = fail_fast_ratio
