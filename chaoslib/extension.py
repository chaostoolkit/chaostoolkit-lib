# -*- coding: utf-8 -*-
from typing import Optional

from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Experiment, Extension

__all__ = ["get_extension", "has_extension", "set_extension",
           "merge_extension", "remove_extension", "validate_extensions"]


def validate_extensions(experiment: Experiment):
    """
    Validate that extensions respect the specification.
    """
    extensions = experiment.get("extensions")
    if not extensions:
        return

    for ext in extensions:
        ext_name = ext.get('name')
        if not ext_name or not ext_name.strip():
            raise InvalidExperiment("All extensions require a non-empty name")


def get_extension(experiment: Experiment, name: str) -> Optional[Extension]:
    """
    Get an extension by its name.

    If no extensions were defined, or the extension doesn't exist in this
    experiment, return `None`.
    """
    extensions = experiment.get("extensions")
    if not extensions:
        return None

    for ext in extensions:
        ext_name = ext.get("name")
        if ext_name == name:
            return ext

    return None


def has_extension(experiment: Experiment, name: str) -> bool:
    """
    Check if an extension is declared in this experiment.
    """
    return get_extension(experiment, name) is not None


def set_extension(experiment: Experiment, extension: Extension):
    """
    Set an extension in this experiment.

    If the extension already exists, it is overriden by the new one.
    """
    if "extensions" not in experiment:
        experiment["extensions"] = []

    name = extension.get("name")
    for ext in experiment["extensions"]:
        ext_name = ext.get("name")
        if ext_name == name:
            experiment["extensions"].remove(ext)
            break
    experiment["extensions"].append(extension)


def remove_extension(experiment: Experiment, name: str):
    """
    Remove an extension from this experiment.
    """
    if "extensions" not in experiment:
        return None

    for ext in experiment["extensions"]:
        ext_name = ext.get("name")
        if ext_name == name:
            experiment["extensions"].remove(ext)
            break


def merge_extension(experiment: Experiment, extension: Extension):
    """
    Merge an extension in this experiment.

    If the extension does not exist yet, it is added. The merge is at the
    first level only.
    """
    if "extensions" not in experiment:
        experiment["extensions"] = []

    name = extension.get("name")
    for ext in experiment["extensions"]:
        ext_name = ext.get("name")
        if ext_name == name:
            ext.update(extension)
            break
    else:
        experiment["extensions"].append(extension)
