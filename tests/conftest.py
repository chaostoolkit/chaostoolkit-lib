# -*- coding: utf-8 -*-
import json
import os.path
from tempfile import NamedTemporaryFile
from typing import Generator

import pytest

from chaoslib.settings import load_settings
from chaoslib.types import Experiment, Settings

from fixtures import experiments


@pytest.fixture
def settings_file() -> str:
    return os.path.join(
        os.path.dirname(__file__), "fixtures", "settings.yaml")


@pytest.fixture
def settings(settings_file: str) -> Settings:
    return load_settings(settings_file)


@pytest.fixture
def generic_experiment() -> Generator[str, None, None]:
    with NamedTemporaryFile(mode='w', suffix=".json", encoding='utf-8') as f:
        json.dump(experiments.Experiment, f)
        f.seek(0)
        yield f.name
