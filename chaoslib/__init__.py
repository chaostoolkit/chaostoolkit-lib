import decimal
import hashlib
import json
import logging
import os.path
import uuid
from collections import ChainMap
from collections.abc import Mapping
from datetime import date, datetime
from importlib.metadata import PackageNotFoundError, version
from json.decoder import JSONDecodeError
from json.encoder import JSONEncoder
from string import Template
from typing import Any, Dict, List, Tuple, Union

import yaml
from charset_normalizer import detect

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import (
    Configuration,
    ConfigVars,
    Experiment,
    Secrets,
    SecretVars,
)

__all__ = [
    "PayloadEncoder",
    "__version__",
    "canonical_json",
    "convert_vars",
    "decode_bytes",
    "experiment_hash",
    "merge_vars",
    "substitute",
]
logger = logging.getLogger("chaostoolkit-lib")

try:
    __version__ = version("chaostoolkit-lib")
except PackageNotFoundError:
    __version__ = "unknown"


def substitute(
    data: None | str | dict[str, Any] | list,
    configuration: Configuration,
    secrets: Secrets,
) -> dict[str, Any]:
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


class TypedTemplate(Template):
    def safe_substitute(self, mapping: dict[str, Any]) -> Any:
        """
        We trick the substitution so that, if the template is made
        of a single pattern, we returns its value in the type found
        in the configuration/secrets. Otherwise, we cast to a string.

        "${value}" => returns whatever type is value
        "hello ${value}" => return a string no matter the type of value
        """
        match = self.pattern.fullmatch(self.template)
        if match is not None:
            try:
                _, _, key, _ = match.groups()
                return mapping[key]
            except KeyError:
                logger.debug(
                    f"The pattern {self.template} does not have a matching "
                    "value in either the configuration or secrets. We don't "
                    "know if that's because the pattern should be passed as-is "
                    "down to the activity. We assume that's the case."
                )
            except ValueError:
                pass
        return Template.safe_substitute(self, mapping)


def substitute_string(data: str, mapping: Mapping[str, Any]) -> Any:
    return TypedTemplate(data).safe_substitute(mapping)


def substitute_dict(
    data: dict[str, Any], mapping: Mapping[str, Any]
) -> dict[str, Any]:
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


def substitute_in_sequence(
    data: list[Any], mapping: Mapping[str, Any]
) -> list[Any]:
    if not data:
        return data

    new_value = []
    for v in data:
        if isinstance(v, str):
            new_value.append(substitute_string(v, mapping))
        elif isinstance(v, (list, tuple)):
            new_value.append(substitute_in_sequence(v, mapping))
        elif isinstance(v, dict):
            new_value.append(substitute_dict(v, mapping))
        else:
            new_value.append(v)
    return new_value


def decode_bytes(data: bytes, default_encoding: str = "utf-8") -> str:
    """
    Decode the given bytes and return the decoded unicode string or raises
    `ActivityFailed`.

    We try to detect the encoding and use that instead of the default one
    (when the confidence is greater or equal than 50%).
    """
    encoding = default_encoding
    detected = detect(data) or {}
    confidence = detected.get("confidence") or 0
    if confidence >= 0.5:
        encoding = detected["encoding"]
        logger.debug(
            f"Data encoding detected as '{encoding}' " f"with a confidence of {confidence}"
        )

    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        raise ActivityFailed(
            f"Failed to decode bytes using encoding '{encoding}'"
        )


def merge_vars(
    var: dict[str, str | float | int | bytes] = None,
    var_files: list[str] = None,
) -> tuple[ConfigVars, SecretVars]:
    """
    Load configuration and secret values from the given set of variables.
    These values are applicable for substitution when the experiment runs.
    If `var` is set, it must be a dictionary which will be used as
    configuration values only.
    If `var_files` is set, it can be a list of any of these two items:
    * a Json or Yaml payload which must be also mappings with two top-level
      keys: `"configuration"` and `"secrets"`. If any is present, it must
      respect the format of the confiuration and secrets of the experiment
      format.
    * a .env file which is used to load environment variable on the fly.
      In that case, the values are injected in the process environment so that
      they get picked up during experiment's execution as if they had been
      from the terminal itself.
    Note that, when multiple var files are provided, they can override each
    other.
    The output of this function is a tuple made of configuration and secrets
    that will be used during the experiment's execution for lookup.
    """
    config_vars = {}
    secret_vars = {}

    if var_files:
        for var_file in var_files:
            logger.debug(f"Loading var from file '{var_file}'")

            if not os.path.isfile(var_file):
                logger.error(f"Cannot read var file '{var_file}'")
                continue

            content = None
            with open(var_file) as f:
                content = f.read()

            if not content:
                logger.debug(f"Var file '{var_file}' is empty")
                continue

            data = None
            _, ext = os.path.splitext(var_file)
            if ext in (".yaml", ".yml"):
                try:
                    data = yaml.safe_load(content)
                except yaml.YAMLError as y:
                    logger.error(
                        f"Failed to parse variable file '{var_file}': {y!s}"
                    )
                    continue
            elif ext in (".json",):
                try:
                    data = json.loads(content)
                except JSONDecodeError as x:
                    logger.error(
                        f"Failed to parse variable file '{var_file}': {x!s}"
                    )
                    continue

            # process .env files
            if not data:
                for line in content.split(os.linesep):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    k, v = line.split("=", 1)
                    os.environ[k] = v
                    logger.debug(
                        f"Inject environment variable '{k}' from "
                        f"file '{var_file}'"
                    )
            else:
                logger.debug(f"Reading configuration/secrets from {f.name}")
                config_vars.update(data.get("configuration", {}))
                secret_vars.update(data.get("secrets", {}))

    if var:
        for k in var:
            logger.debug(f"Using configuration variable '{k}'")
            config_vars[k] = var[k]

    return (config_vars, secret_vars)


def convert_vars(value: list[str]) -> dict[str, Any]:
    """
    Process all variables and return a dictionnary of them with the
    value converted to the appropriate type.

    The list of values is as follows: `key[:type]=value` with `type` being one
    of: str, int, float and bytes. `str` is the default and can be omitted.
    """
    var = {}
    for v in value:
        try:
            k, v = v.split("=", 1)
            if ":" in k:
                k, typ = k.rsplit(":", 1)
                try:
                    v = convert_to_type(typ, v)
                except (TypeError, UnicodeEncodeError):
                    raise ValueError(
                        "var cannot convert value to required type"
                    )
            var[k] = v
        except ValueError:
            raise
        except Exception:
            raise ValueError("var needs to be in the format name[:type]=value")

    return var


def convert_to_type(
    type: str, val: str
) -> str | int | float | bytes | bool | Any:
    """
    Converts a value to a provided type. If `type` is None, then the original string is
    returned, else the val is coerced into the provided type. An exception is thrown
    if the type is not supported.

    :param type: str representing what type to convert `val` to
    :param val: str representing the variable loaded in to configuration
    :returns: Union[str, int, float, bytes] representing the converted value
    """
    if type is None or type in ("str", "string"):
        return val
    elif type in ("int", "integer"):
        return int(val)
    elif type in ("float", "number"):
        return float(val)
    elif type == "bytes":
        return val.encode("utf-8")
    elif type == "bool":
        if isinstance(val, bool):
            return val
        return False if val.lower() in ("false", "0", "no") else True
    elif type == "json":
        if val in ("", None):
            return val
        if isinstance(val, str):
            return json.loads(val)
        return val
    else:
        raise ValueError(
            "variable type can only be: bool, str, int, float, bytes or json"
        )


class PayloadEncoder(JSONEncoder):
    """
    Extension of the base JSONEncoder to support serialising objects commonly passed
    around in Chaos Toolkit function payloads

    Currently supports:
    - datetime/date objects
    - UUID objects
    - Decimal objects
    - Exception objects
    """

    def default(self, obj) -> str:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID) or isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, Exception):
            return f"An exception was raised: {obj.__class__.__name__}('{obj!s}')"
        return JSONEncoder.default(self, obj)


def canonical_json(experiment: Experiment) -> bytes:
    """
    Serialize and encode to utf-8 the experiment to a canonical view:

    * no identation
    * sorted keys
    * keys of a non basic types skipped

    This is mostly useful for hashing the experiment.
    """
    return json.dumps(
        experiment, skipkeys=True, sort_keys=True, indent=None
    ).encode("utf-8")


def experiment_hash(experiment: Experiment, hash_algo: str = None) -> str:
    """
    Create a hash (using the blake2b algorithm by default) of the
    experiment's cnanonical view.

    You may provide any other algorithms supported by `haslib` and available
    to your platform

    https://docs.python.org/3/library/hashlib.html#hashlib.algorithms_available
    """
    if hash_algo is not None:
        if hash_algo not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hashlib algorithm: '{hash_algo}'")
        return hashlib.new(hash_algo, canonical_json(experiment)).hexdigest()

    return hashlib.blake2b(
        canonical_json(experiment), digest_size=12
    ).hexdigest()
