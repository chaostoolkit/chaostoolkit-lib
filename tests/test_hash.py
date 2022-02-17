import hashlib
import json

import pytest

from chaoslib import experiment_hash


def test_with_default():
    assert (
        experiment_hash({})
        == hashlib.blake2b(json.dumps({}).encode("utf-8"), digest_size=12).hexdigest()
    )


def test_specific_algo():
    assert (
        experiment_hash({}, hash_algo="sha256")
        == hashlib.sha256(json.dumps({}).encode("utf-8")).hexdigest()
    )


def test_unavailable_algo():
    with pytest.raises(ValueError):
        experiment_hash({}, hash_algo="md78")
