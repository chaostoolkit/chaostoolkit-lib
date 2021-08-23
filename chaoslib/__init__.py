# -*- coding: utf-8 -*-
from collections import ChainMap
import os.path
from string import Template
from typing import Any, Dict, List, Mapping, Tuple, Union

HAS_CHARDET = True
try:
    import cchardet as chardet
except ImportError:
    try:
        import chardet
    except ImportError:
        HAS_CHARDET = False
from logzero import logger
try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ImportError:
    import json
    from json.decoder import JSONDecodeError
import yaml

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, ConfigVars, Secrets, SecretVars

__all__ = ["__version__", "decode_bytes", "substitute", "merge_vars",
           "convert_vars"]
__version__ = '1.21.0'


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


class TypedTemplate(Template):
    def safe_substitute(self, mapping: Dict[str, Any]) -> Any:
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
            except ValueError:
                pass
        return Template.safe_substitute(self, mapping)


def substitute_string(data: str, mapping: Mapping[str, Any]) -> Any:
    return TypedTemplate(data).safe_substitute(mapping)


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


def merge_vars(var: Dict[str, Union[str, float, int, bytes]] = None,  # noqa: C901
               var_files: List[str] = None) -> Tuple[ConfigVars, SecretVars]:
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
            logger.debug("Loading var from file '{}'".format(var_file))

            if not os.path.isfile(var_file):
                logger.error("Cannot read var file '{}'".format(var_file))
                continue

            content = None
            with open(var_file) as f:
                content = f.read()

            if not content:
                logger.debug("Var file '{}' is empty".format(var_file))
                continue

            data = None
            _, ext = os.path.splitext(var_file)
            if ext in (".yaml", ".yml"):
                try:
                    data = yaml.safe_load(content)
                except yaml.YAMLError as y:
                    logger.error(
                        "Failed to parse variable file '{}': {}".format(
                            var_file, str(y)))
                    continue
            elif ext in (".json"):
                try:
                    data = json.loads(content)
                except JSONDecodeError as x:
                    logger.error(
                        "Failed to parse variable file '{}': {}".format(
                            var_file, str(x)))
                    continue

            # process .env files
            if not data:
                for line in content.split(os.linesep):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    k, v = line.split('=', 1)
                    os.environ[k] = v
                    logger.debug(
                        "Inject environment variable '{}' from "
                        "file '{}'".format(k, var_file))
            else:
                logger.debug(
                    "Reading configuration/secrets from {}".format(f.name))
                config_vars.update(data.get("configuration", {}))
                secret_vars.update(data.get("secrets", {}))

    if var:
        for k in var:
            logger.debug("Using configuration variable '{}'".format(k))
            config_vars[k] = var[k]

    return (config_vars, secret_vars)


def convert_vars(value: List[str]) -> Dict[str, Any]:  # noqa: C901
    """
    Process all variables and return a dictionnary of them with the
    value converted to the appropriate type.

    The list of values is as follows: `key[:type]=value` with `type` being one
    of: str, int, float and bytes. `str` is the default and can be omitted.
    """
    var = {}
    for v in value:
        try:
            k, v = v.split('=', 1)
            if ':' in k:
                k, typ = k.rsplit(':', 1)
                try:
                    if typ == 'str':
                        pass
                    elif typ == 'int':
                        v = int(v)
                    elif typ == 'float':
                        v = float(v)
                    elif typ == 'bytes':
                        v = v.encode('utf-8')
                    else:
                        raise ValueError(
                            'var supports only: str, int, float and bytes')
                except (TypeError, UnicodeEncodeError):
                    raise ValueError(
                        'var cannot convert value to required type')
            var[k] = v
        except ValueError:
            raise
        except Exception:
            raise ValueError('var needs to be in the format name[:type]=value')

    return var
