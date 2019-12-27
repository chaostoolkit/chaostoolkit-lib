# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any, Union

from chaoslib.types import ValidationError

__all__ = ["Validation"]


class Validation(object):
    """
    This class keeps a list of validation errors to be appended
    to report all errors at once
    """
    def __init__(self):
        self._errors = []  # type: List[ValidationError]

    def add_error(self, field: str, message: str,
                  value: Any = None, location: tuple = None):
        """
        Append a new error to the validation errors list

        :param field: name of the key/field that raised the validation error
        :param message: information about the error
        :param value: value being validated - that failed -
        :param location: optional location of the key in the full document
            as a json-path-like; e.g. ("rollbacks", 0, "type")
            NB: For list/tuples, the index of the failed sub-element is used
        """
        if location is None:
            location = ()

        self._errors.append(
            {
                "field": field,
                "msg": message,
                "value": value,
                "loc": location,
            }
        )

    def has_errors(self) -> bool:
        return len(self.errors())

    def extend_errors(self, errors: List[ValidationError]):
        self._errors.extend(errors)

    def merge(self, val: 'Validation'):
        self.extend_errors(val.errors())

    def errors(self) -> List[ValidationError]:
        return self._errors

    def json(self, indent: Union[None, int, str] = 2) -> str:
        return json.dumps(self.errors(), indent=indent)

    def display_errors(self):
        return _display_errors(self.errors())

    def __str__(self) -> str:
        errors = self.errors()
        nb_errors = len(errors)
        return (
            "{count} validation error{plural}\n"
            "{errors}".format(
                count=nb_errors, plural="" if nb_errors == 1 else "s",
                errors=_display_errors(errors)
            )
        )


def _display_errors(errors: List[ValidationError]) -> str:
    error_format = "{field}\n\t{msg} -> {loc} ({val})"
    return '\n'.join(error_format.format(
        field=e["field"], msg=e["msg"], val=e["value"],
        loc=_display_error_loc(e)) for e in errors)


def _display_error_loc(error: ValidationError) -> str:
    return '.'.join(str(l) for l in error['loc'])
