# -*- coding: utf-8 -*-
from collections import ChainMap
from string import Template
from typing import Any, Dict, List, Mapping, Union

HAS_CHARDET = True
try:
    import cchardet as chardet
except ImportError:
    try:
        import chardet
    except ImportError:
        HAS_CHARDET = False
from logzero import logger

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets

__all__ = ["__version__", "decode_bytes", "substitute"]
__version__ = '1.4.0'


def substitute(data: Union[None, str, Dict[str, Any], List],
               configuration: Configuration,
               secrets: Secrets) -> Dict[str, Any]:
    """
    Replace forms such as `${name}` with the first value found in either the
    `configuration` or `secrets` mappings within the given `data`.
    The original payload is not altered.

    The substitition is done recursively and inside sequences as well.

    The goal is to inject values into the experiment by reading them from
    dynamic values.
    """
    if not data:
        return data

    # secrets is a mapping of mapping, only the second level is useful here
    secrets = secrets.values() if secrets else []

    # let's pretend we have a single mapping of everything with the config
    # by the leader
    mapping = ChainMap(configuration or {}, *secrets)

    if isinstance(data, dict):
        return substitute_dict(data, mapping)

    if isinstance(data, str):
        return substitute_string(data, mapping)

    if isinstance(data, list):
        return substitute_in_sequence(data, mapping)

    return data


def substitute_string(data: str, mapping: Mapping[str, Any]) -> str:
    return Template(data).safe_substitute(mapping)


def substitute_dict(data: Dict[str, Any],
                    mapping: Mapping[str, Any]) -> Dict[str, Any]:
    if not data:
        return data

    args = {}
    for key, value in data.items():
        if isinstance(value, str):
            args[key] = substitute_string(value, mapping)
        elif isinstance(value, (list, tuple)):
            args[key] = substitute_in_sequence(value, mapping)
        elif isinstance(value, dict):
            args[key] = substitute_dict(value, mapping)
        else:
            args[key] = value
    return args


def substitute_in_sequence(data: List[Any],
                           mapping: Mapping[str, Any]) -> List[Any]:
    if not data:
        return data

    new_value = []
    for v in data:
        if isinstance(v, str):
            new_value.append(substitute_string(v, mapping))
        elif isinstance(v, (list, tuple)):
            new_value.extend(substitute_in_sequence(v, mapping))
        elif isinstance(v, dict):
            new_value.append(substitute_dict(v, mapping))
        else:
            new_value.append(v)
    return new_value


def decode_bytes(data: bytes, default_encoding: str = 'utf-8') -> str:
    """
    Decode the given bytes and return the decoded unicode string or raises
    `ActivityFailed`.

    When the chardet, or cchardet, packages are installed, we try to detect
    the encoding and use that instead of the default one (when the confidence
    is greater or equal than 50%).
    """
    encoding = default_encoding
    if HAS_CHARDET:
        detected = chardet.detect(data) or {}
        confidence = detected.get('confidence') or 0
        if confidence >= 0.5:
            encoding = detected['encoding']
            logger.debug(
                "Data encoding detected as '{}' "
                "with a confidence of {}".format(encoding, confidence))

    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        raise ActivityFailed(
            "Failed to decode bytes using encoding '{}'".format(encoding))
