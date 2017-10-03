# -*- coding: utf-8 -*-
import pytest

from chaoslib.exceptions import InvalidProbe
from chaoslib.layer import load_layers
from chaoslib.probe import ensure_layer_probe_is_valid
from chaoslib.types import Layer, Probe

from fixtures import probes


def test_empty_probe_is_invalid():
    with pytest.raises(InvalidProbe) as exc:
        ensure_layer_probe_is_valid(probes.EmptyProbe, None)
