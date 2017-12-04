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

MissingHypothesisExperiment = {
    "title": "kaboom",
    "description": "blah"
}

MissingHypothesisTitleExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {}
}

MissingMethodExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {
        "title": "hello"
    }
}

NoStepsMethodExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": []
}

Experiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ]
}
