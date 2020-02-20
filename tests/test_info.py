from unittest.mock import patch
from typing import List
try:
    from importlib.metadata import Distribution
except ImportError:
    from importlib_metadata import Distribution

from chaoslib.info import list_extensions

PGK_META = """Metadata-Version: 2.1
Name: chaostoolkit-some-stuff
Version: 0.1.0
Summary: Chaos Toolkit some package
Home-page: http://chaostoolkit.org
Author: chaostoolkit Team
Author-email: contact@chaostoolkit.org
License: Apache License 2.0
"""


class InMemoryDistribution(Distribution):
    def __init__(self, metadata, *args, **kwargs):
        Distribution.__init__(self, *args, **kwargs)
        self._data = metadata

    def read_text(self, filename):
        return self._data

    def locate_file(self, path):
        pass


@patch("chaoslib.info.importlib_metadata.distributions")
def test_list_none_when_none_installed(distros: List[Distribution]):
    distros.return_value = []
    extensions = list_extensions()
    assert extensions == []


@patch("chaoslib.info.importlib_metadata.distributions")
def test_list_one_installed(distros: List[Distribution]):
    distros.return_value = [
        InMemoryDistribution(PGK_META)
    ]

    extensions = list_extensions()
    assert len(extensions) == 1

    ext = extensions[0]
    assert ext.name == "chaostoolkit-some-stuff"
    assert ext.version == "0.1.0"


@patch("chaoslib.info.importlib_metadata.distributions")
def test_list_excludes_ctklib(distros: List[Distribution]):
    metadata = """Name: chaostoolkit-lib"""
    distros.return_value = [
        InMemoryDistribution(metadata)
    ]

    extensions = list_extensions()
    assert len(extensions) == 0


@patch("chaoslib.info.importlib_metadata.distributions")
def test_list_skip_duplicates(distros: List[Distribution]):
    distros.return_value = [
        InMemoryDistribution(PGK_META),
        InMemoryDistribution(PGK_META),
    ]

    extensions = list_extensions()
    assert len(extensions) == 1
