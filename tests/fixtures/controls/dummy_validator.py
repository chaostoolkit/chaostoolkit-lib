from chaoslib.exceptions import InvalidActivity
from chaoslib.types import Control


def validate_control(control: Control) -> None:
    if "should-not-be-here" in control:
        raise InvalidActivity("invalid key on control")
