# -*- coding: utf-8 -*-
import importlib
from typing import Any, Dict, List

from logzero import logger

from chaostoolkit.types import Layer, TargetLayers

__all__ = ["load_layers"]


def load_layers(target_layers: TargetLayers) -> Dict[str, Layer]:
    layers = {}

    logger.info("Loading the following target layers:")
    for layer in ("platforms", "applications"):
        for target in target_layers.get(layer, []):
            key = target.get("key")
            logger.info(" {layer}: {key} => {mod}".format(
                layer=layer, key=key, mod=mod_name))
            layers[key] = importlib.import_module(mod_name)

    return layers
