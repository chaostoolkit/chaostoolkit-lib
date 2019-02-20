# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Tuple, Union

__all__ = ["MicroservicesStatus", "Probe", "Action", "Experiment", "Layer",
           "TargetLayers", "Activity", "Journal", "Run", "Secrets", "Step",
           "Configuration", "Discovery", "DiscoveredActivities", "Extension",
           "DiscoveredSystemInfo", "Settings", "EventPayload", "Tolerance",
           "Hypothesis", "Control"]


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
