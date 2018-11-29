from email import message_from_string
from unittest.mock import MagicMock, patch

from pkg_resources import Distribution, EmptyProvider, Environment

from chaoslib.info import list_extensions


class InMemoryMetadata(EmptyProvider):
    def __init__(self, metadata, *args, **kwargs):
        EmptyProvider.__init__(self, *args, **kwargs)
        self._data = metadata

    def has_metadata(self, name):
        return name in self._data

    def get_metadata(self, name):
        return self._data.get(name)


@patch("chaoslib.info.Environment", autospec=True)
def test_list_none_when_none_installed(environment: Environment):
    extensions = list_extensions()
    assert extensions == []


@patch("chaoslib.info.Environment", autospec=True)
def test_list_one_installed(environment: Environment):
    env = Environment(search_path=[])
    environment.return_value = env
    metadata = """Metadata-Version: 2.1
Name: chaostoolkit-some-stuff
Version: 0.1.0
Summary: Chaos Toolkit some package
Home-page: http://chaostoolkit.org
Author: chaostoolkit Team
Author-email: contact@chaostoolkit.org
License: Apache License 2.0
"""

    env.add(
        Distribution(
            project_name="chaostoolkit-some-stuff",
            version="0.1.0",
            metadata=InMemoryMetadata({
                "PKG-INFO": metadata
            })
        )
    )
    extensions = list_extensions()
    assert len(extensions) == 1

    ext = extensions[0]
    assert ext.name == "chaostoolkit-some-stuff"
    assert ext.version == "0.1.0"
