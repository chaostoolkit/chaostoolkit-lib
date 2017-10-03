# -*- coding: utf-8 -*-
from chaoslib.exceptions import InvalidProbe
from chaoslib.types import Layer, Probe

__all__ = ["ensure_layer_probe_is_valid"]


def ensure_layer_probe_is_valid(probe: Probe, layer: Layer):
    if not probe:
        raise InvalidProbe()
