# -*- coding: utf-8 -*-
import sys

from chaoslib.activity import ensure_activity_is_valid, run_activity
from chaoslib.exceptions import FailedActivity, FailedAction, InvalidActivity,\
    InvalidAction
from chaoslib.types import Action, Secrets

__all__ = ["ensure_action_is_valid", "run_action"]


def ensure_action_is_valid(action: Action):
    try:
        return ensure_activity_is_valid(action)
    except InvalidActivity as x:
        m = str(x)
        m = m.replace("activity", "action")
        raise InvalidAction(m).with_traceback(sys.exc_info()[2])


def run_action(action: Action, secrets: Secrets):
    try:
        return run_activity(action, secrets)
    except FailedActivity as x:
        m = str(x)
        m = m.replace("activity", "action")
        raise FailedAction(m).with_traceback(sys.exc_info()[2])
