import pytest
from fixtures import actions

from chaoslib.activity import ensure_activity_is_valid
from chaoslib.exceptions import InvalidActivity


def test_empty_action_is_invalid():
    with pytest.raises(InvalidActivity) as exc:
        ensure_activity_is_valid(actions.EmptyAction)
    assert "empty activity is no activity" in str(exc.value)
