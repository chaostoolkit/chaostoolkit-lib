# -*- coding: utf-8 -*-
from fixtures.probes import PythonModuleProbe, BackgroundPythonModuleProbe

Secrets = {}

EmptyExperiment = {}

MissingTitleExperiment = {
    "description": "blah"
}

MissingDescriptionExperiment = {
    "title": "kaboom"
}

MissingMethodExperiment = {
    "title": "kaboom",
    "description": "blah"
}

NoStepsMethodExperiment = {
    "title": "kaboom",
    "description": "blah",
    "method": []
}

Experiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ]
}
