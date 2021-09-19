import enum
from typing import Any, Dict, List, Optional, Tuple, Union

__all__ = [
    "MicroservicesStatus",
    "Probe",
    "Action",
    "Experiment",
    "Layer",
    "TargetLayers",
    "Activity",
    "Journal",
    "Run",
    "Secrets",
    "Step",
    "Configuration",
    "Discovery",
    "DiscoveredActivities",
    "Extension",
    "DiscoveredSystemInfo",
    "Settings",
    "EventPayload",
    "Tolerance",
    "Hypothesis",
    "Control",
    "Strategy",
    "Schedule",
    "ConfigVars",
    "SecretVars",
]


Action = Dict[str, Any]
Experiment = Dict[str, Any]
Probe = Dict[str, Any]

Activity = Union[Probe, Action]

Layer = Any
TargetLayers = Dict[str, List[Dict[str, Any]]]

MicroservicesStatus = Tuple[Dict[str, Any], Dict[str, Any]]
Journal = Dict[str, Any]
Run = Dict[str, Any]
Step = Dict[str, Any]

Secrets = Dict[str, Dict[str, str]]
Configuration = Dict[str, Dict[str, str]]

Discovery = Dict[str, Any]
DiscoveredActivities = Dict[str, Any]
DiscoveredSystemInfo = Dict[str, Any]

Settings = Dict[str, Any]
EventPayload = Dict[str, Any]

Tolerance = Union[int, str, bool, list, Dict[str, Any]]

Extension = Dict[str, Any]
Hypothesis = Dict[str, Any]
Control = Dict[str, Any]

ConfigVars = Dict[str, Any]
SecretVars = Dict[str, Any]


class Strategy(enum.Enum):
    BEFORE_METHOD = "before-method-only"
    AFTER_METHOD = "after-method-only"
    DURING_METHOD = "during-method-only"
    DEFAULT = "default"
    CONTINUOUS = "continuous"

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
