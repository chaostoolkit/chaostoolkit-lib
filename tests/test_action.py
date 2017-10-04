# -*- coding: utf-8 -*-
import sys

import pytest
import requests_mock

from chaoslib.exceptions import FailedAction, InvalidAction
from chaoslib.action import ensure_action_is_valid, run_action
from chaoslib.types import Action

from fixtures import actions


def test_empty_action_is_invalid():
    with pytest.raises(InvalidAction) as exc:
        ensure_action_is_valid(actions.EmptyAction)
    assert "empty action is no action" in str(exc)
