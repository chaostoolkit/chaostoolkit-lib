# -*- coding: utf-8 -*-
import sys

from chaoslib.activity import ensure_activity_is_valid, run_activity
from chaoslib.exceptions import FailedProbe, FailedActivity, InvalidActivity, \
    InvalidProbe
from chaoslib.types import Probe, Secrets

__all__ = ["ensure_probe_is_valid", "run_probe"]


def ensure_probe_is_valid(probe: Probe):
    try:
        return ensure_activity_is_valid(probe)
    except InvalidActivity as x:
        m = str(x)
        m = m.replace("activity", "probe")
        raise InvalidProbe(m).with_traceback(sys.exc_info()[2])


def run_probe(probe: Probe, secrets: Secrets):
    try:
        return run_activity(probe, secrets)
    except FailedActivity as x:
        if probe.get("negate") is True:
            return
        m = str(x)
        m = m.replace("activity", "probe")
        raise FailedProbe(m).with_traceback(sys.exc_info()[2])
