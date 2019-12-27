# -*- coding: utf-8 -*-
import sys

import pytest
import requests_mock

from chaoslib.exceptions import InvalidActivity
from chaoslib.activity import ensure_activity_is_valid
from chaoslib.types import Action

from fixtures import actions


def test_empty_action_is_invalid():
    errors = ensure_activity_is_valid(actions.EmptyAction)
    assert "empty activity is no activity" in str(errors[0])

