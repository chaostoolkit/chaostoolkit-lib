# -*- coding: utf-8 -*-
import io
import os.path
from urllib.parse import urlparse

from chaoslib.exceptions import InvalidSource
from logzero import logger
import requests
import yaml
try:
    import simplejson as json
except ImportError:
    import json

from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Experiment, Settings


__all__ = ["load_experiment"]


def parse_experiment_from_file(path: str) -> Experiment:
    """
    Parse the given experiment from `path` and return it.
    """
    with io.open(path) as f:
        p, ext = os.path.splitext(path)
        if ext in (".yaml", ".yml"):
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as ye:
                raise InvalidSource(
                    "Failed parsing YAML experiment: {}".format(str(ye)))
        elif ext == ".json":
            return json.load(f)

    raise InvalidExperiment(
        "only files with json, yaml or yml extensions are supported")


def parse_experiment_from_http(response: requests.Response) -> Experiment:
    """
    Parse the given experiment from the request's `response`.
    """
    content_type = response.headers.get("Content-Type")

    if 'application/json' in content_type:
        return response.json()
    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
        try:
            return yaml.safe_load(response.text)
        except yaml.YAMLError as ye:
            raise InvalidSource(
                "Failed parsing YAML experiment: {}".format(str(ye)))

    raise InvalidExperiment(
        "only files with json, yaml or yml extensions are supported")


def load_experiment(experiment_source: str,
                    settings: Settings = None) -> Experiment:
    """
    Load an experiment from the given source.

    The source may be a local file or a HTTP(s) URL. If the endpoint requires
    authentication, please set the appropriate entry in the settings file,
    under the `auths:` section, keyed by domain. For instance:

    ```yaml
    auths:
      mydomain.com:
        type: basic
        value: XYZ
      otherdomain.com:
        type: bearer
        value: UIY
      localhost:8081:
        type: digest
        value: UIY
    ```
    """
    if os.path.exists(experiment_source):
        return parse_experiment_from_file(experiment_source)

    p = urlparse(experiment_source)
    if not p.scheme and not os.path.exists(p.path):
        raise InvalidSource('Path "{}" does not exist.'.format(p.path))

    if p.scheme not in ("http", "https"):
        raise InvalidSource(
            "'{}' is not a supported source scheme.".format(p.scheme))

    headers = {
        "Accept": "application/json, application/x-yaml"
    }
    if settings:
        auths = settings.get("auths", [])
        for domain in auths:
            if domain == p.netloc:
                auth = auths[domain]
                headers["Authorization"] = '{} {}'.format(
                    auth["type"], auth["value"])
                break

    r = requests.get(experiment_source, headers=headers)
    if r.status_code != 200:
        raise InvalidSource(
            "Failed to fetch the experiment: {}".format(r.text))

    logger.debug("Fetched experiment: \n{}".format(r.text))
    return parse_experiment_from_http(r)
