# -*- coding: utf-8 -*-
from collections import ChainMap
from string import Template
from typing import Any, Dict, List, Mapping, Union

from chaoslib.types import Configuration, Secrets

__all__ = ["__version__", "substitute"]
__version__ = '0.14.0'


def substitute(data: Union[str, Dict[str, Any]], configuration: Configuration,
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
