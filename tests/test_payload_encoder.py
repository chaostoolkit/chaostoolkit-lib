import decimal
import json
import uuid
from datetime import date, datetime

import pytest

from chaoslib import PayloadEncoder
from chaoslib.exceptions import ChaosException


def test_that_payload_encoder_handles_datetime_objects():
    now = datetime.now()
    payload = {"test-datetime": now}
    payload_encoded = json.dumps(payload, cls=PayloadEncoder)
    assert now.isoformat() in payload_encoded


def test_that_payload_encoder_handles_date_objects():
    now = date.today()
    payload = {"test-datetime": now}
    payload_encoded = json.dumps(payload, cls=PayloadEncoder)
    assert now.isoformat() in payload_encoded


def test_that_payload_encoder_handles_uuid_objects():
    payload_uuid = uuid.uuid4()
    payload = {"test-uuid": payload_uuid}
    payload_encoded = json.dumps(payload, cls=PayloadEncoder)
    assert str(payload_uuid) in payload_encoded


def test_that_payload_encoder_handles_decimal_objects():
    number = decimal.Decimal(6.12)
    payload = {"test-decimal": number}
    payload_encoded = json.dumps(payload, cls=PayloadEncoder)
    assert str(number) in payload_encoded


def test_that_payload_encoder_handles_exception_objects():
    exception = ChaosException("An Exception Happened")
    payload = {"test-exception": exception}
    payload_encoded = json.dumps(payload, cls=PayloadEncoder)
    assert (
        "An exception was raised: ChaosException('An Exception Happened')"
    ) in payload_encoded


def test_that_payload_encoder_handles_unserialisable_object_in_base_class():
    class AThing:
        def __init__(self, name: str) -> None:
            self.name = name

    a_thing = AThing(name="test-name")
    payload = {"test-thing": a_thing}
    with pytest.raises(TypeError):
        json.dumps(payload, cls=PayloadEncoder)
