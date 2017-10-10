# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Tuple, Union

__all__ = ["MicroservicesStatus", "Probe", "Action", "Experiment", "Layer",
           "TargetLayers", "Activity", "Journal", "Run", "Secrets"]


Action = Dict[str, Any]
Experiment = Dict[str, Any]
Probe = Dict[str, Any]

Activity = Union[Probe, Action]

Layer = Any
TargetLayers = Dict[str, List[Dict[str, Any]]]

MicroservicesStatus = Tuple[Dict[str, Any], Dict[str, Any]]
Journal = Dict[str, Any]
Run = Dict[str, Any]

Secrets = Dict[str, Dict[str, str]]
