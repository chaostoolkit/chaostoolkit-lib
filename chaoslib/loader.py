import os.path
from urllib.parse import urlparse

import requests
import yaml
from logzero import logger

from chaoslib.exceptions import InvalidSource

try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ImportError:
    import json
    from json.decoder import JSONDecodeError

from chaoslib.control import controls
from chaoslib.exceptions import InvalidExperiment
from chaoslib.types import Experiment, Settings

__all__ = ["load_experiment"]


def parse_experiment_from_file(path: str) -> Experiment:
    """
    Parse the given experiment from `path` and return it.
    """
    with open(path) as f:
        p, ext = os.path.splitext(path)
        if ext in (".yaml", ".yml"):
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as ye:
                raise InvalidSource(f"Failed parsing YAML experiment: {str(ye)}")
        elif ext == ".json":
            return json.load(f)

    raise InvalidExperiment(
        "only files with json, yaml or yml extensions are supported"
    )


def parse_experiment_from_http(response: requests.Response) -> Experiment:
    """
    Parse the given experiment from the request's `response`.
    """
    content_type = response.headers.get("Content-Type")

    if "application/json" in content_type:
        return response.json()
    elif "application/x-yaml" in content_type or "text/yaml" in content_type:
        try:
            return yaml.safe_load(response.text)
        except yaml.YAMLError as ye:
            raise InvalidSource(f"Failed parsing YAML experiment: {str(ye)}")
    elif "text/plain" in content_type:
        content = response.text
        try:
            return json.loads(content)
        except JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                pass

    raise InvalidExperiment(
        "only files with json, yaml or yml extensions are supported"
    )


def load_experiment(
    experiment_source: str, settings: Settings = None, verify_tls: bool = True
) -> Experiment:
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

    Set `verify_tls` to `False` if the source is a over a self-signed
    certificate HTTP endpoint to instruct the loader to not verify the
    certificates.
    """
    with controls(level="loader", context=experiment_source) as control:
        if os.path.exists(experiment_source):
            parsed = parse_experiment_from_file(experiment_source)
            control.with_state(parsed)
            return parsed

        p = urlparse(experiment_source)
        if not p.scheme and not os.path.exists(p.path):
            raise InvalidSource(f'Path "{p.path}" does not exist.')

        if p.scheme not in ("http", "https"):
            raise InvalidSource(f"'{p.scheme}' is not a supported source scheme.")

        headers = {"Accept": "application/json, application/x-yaml"}
        if settings:
            auths = settings.get("auths", [])
            for domain in auths:
                if domain == p.netloc:
                    auth = auths[domain]
                    headers["Authorization"] = "{} {}".format(
                        auth["type"], auth["value"]
                    )
                    break

        r = requests.get(experiment_source, headers=headers, verify=verify_tls)
        if r.status_code != 200:
            raise InvalidSource(f"Failed to fetch the experiment: {r.text}")

        logger.debug(f"Fetched experiment: \n{r.text}")
        parsed = parse_experiment_from_http(r)
        control.with_state(parsed)
        return parsed
