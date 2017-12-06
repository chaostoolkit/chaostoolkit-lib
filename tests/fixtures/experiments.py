# -*- coding: utf-8 -*-
from fixtures.probes import BackgroundPythonModuleProbe, MissingFuncArgProbe, \
    PythonModuleProbe, PythonModuleProbeWithBoolTolerance, \
    PythonModuleProbeWithExternalTolerance, PythonModuleProbeWithLongPause, \
    BackgroundPythonModuleProbeWithLongPause

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

ExperimentWithInvalidHypoProbe = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            MissingFuncArgProbe
        ]
    },
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ],
    "rollbacks": [
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}

ExperimentWithLongPause = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        PythonModuleProbeWithLongPause, 
        BackgroundPythonModuleProbeWithLongPause
    ],
    "rollbacks": [
        BackgroundPythonModuleProbe
    ]
}

RefProbeExperiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
        ]
    },
    "method": [
        PythonModuleProbe,
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}

MissingRefProbeExperiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
        ]
    },
    "method": [
        PythonModuleProbe,
        {
            "ref": "pizza"
        }
    ]
}

Experiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
            PythonModuleProbeWithExternalTolerance
        ]
    },
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ],
    "rollbacks": [
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}
