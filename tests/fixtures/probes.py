# -*- coding: utf-8 -*-
from copy import deepcopy
import os.path
import sys
from typing import Any

from chaoslib.exceptions import ActivityFailed


EmptyProbe = {}

MissingTypeProbe = {
    "name": "a name",
    "provider": {
        "module": "blah"
    }
}

UnknownTypeProbe = {
    "type": "whatever",
    "name": "a name",
    "provider": {
        "type": "python"
    }
}

UnknownProviderTypeProbe = {
    "type": "probe",
    "name": "a name",
    "provider": {
        "type": "pizza"
    }
}

MissingModuleProbe = {
    "type": "probe",
    "name": "a name",
    "provider": {
        "type": "python"
    }
}

NotImportableModuleProbe = {
    "type": "probe",
    "name": "a name",
    "provider": {
        "type": "python",
        "module": "fake.module",
        "func": "myfunc"
    }
}

MissingFunctionProbe = {
    "type": "probe",
    "provider": {
        "type": "python",
        "module": "os.path"
    },
    "name": "a name"
}

MissingProcessPathProbe = {
    "type": "probe",
    "provider": {
        "type": "process"
    },
    "name": "missing proc path"
}

ProcessPathDoesNotExistProbe = {
    "type": "probe",
    "provider": {
        "type": "process",
        "path": "somewhere/not/here",
    },
    "name": "invalid proc path"
}

MissingHTTPUrlProbe = {
    "type": "probe",
    "provider": {
        "type": "http"
    },
    "name": "A probe without url"
}

MissingFuncArgProbe = {
    "type": "probe",
    "name": "a name",
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {}
    }
}

TooManyFuncArgsProbe = {
    "type": "probe",
    "name": "too-many-args-pause",
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": "/some/path",
            "should_not_be_here": "indeed not"
        }
    }
}

PythonModuleProbe = {
    "type": "probe",
    "name": "path-must-exists",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": os.path.abspath(__file__),
        },
        "timeout": 30
    }
}

PythonModuleProbeWithLongPause = {
    "type": "probe",
    "name": "probe-with-long-pause",
    "pauses": {
        "before": 0,
        "after": 5
    },
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": os.path.abspath(__file__),
        },
        "timeout": 30
    }
}

BackgroundPythonModuleProbeWithLongPause = {
    "type": "probe",
    "name": "background-probe-with-long-pause",
    "background": True,
    "pauses": {
        "before": 0,
        "after": 5
    },
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": os.path.abspath(__file__),
        },
        "timeout": 30
    }
}

BackgroundPythonModuleProbeWithLongPauseBefore = deepcopy(BackgroundPythonModuleProbeWithLongPause)
BackgroundPythonModuleProbeWithLongPauseBefore["pauses"]["after"] = 0
BackgroundPythonModuleProbeWithLongPauseBefore["pauses"]["before"] = 5

PythonModuleProbeWithBoolTolerance = PythonModuleProbe.copy()
# tolerance can be a scalar, a range or a mapping with lower/upper keys
PythonModuleProbeWithBoolTolerance["tolerance"] = True
PythonModuleProbeWithBoolTolerance["name"] = "boolean-probe"

PythonModuleProbeWithExternalTolerance = PythonModuleProbe.copy()
# tolerance can be a scalar, a range or a mapping with lower/upper keys
PythonModuleProbeWithExternalTolerance["tolerance"] = PythonModuleProbe.copy()
PythonModuleProbeWithExternalTolerance["name"] = "external-probe"

PythonModuleProbeWithHTTPStatusTolerance = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": [200, 301, 302],
    "provider": {
        "type": "http",
        "url": "http://example.com",
        "timeout": 30
    }
}

PythonModuleProbeWithHTTPStatusToleranceDeviation = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": [500],
    "provider": {
        "type": "http",
        "url": "http://example.com",
        "timeout": 30
    }
}

PythonModuleProbeWithHTTPBodyTolerance = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": {
        "type": "regex",
        "target": "body",
        "pattern": "[0-9]{2}"
    },
    "provider": {
        "type": "http",
        "url": "http://example.com",
        "timeout": 30
    }
}

PythonModuleProbeWithHTTPMaxRetries = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": [200],
    "provider": {
        "type": "http",
        "url": "http://localhost:{}",
        "timeout": 10,
        "max_retries": 1
    }
}

PythonModuleProbeWithProcessStatusTolerance = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": 0,
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": ["-V"],
        "timeout": 1
    }
}

PythonModuleProbeWithProcessFailedStatusTolerance = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": 2,
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": ["--burp"],
        "timeout": 1
    }
}

PythonModuleProbeWithProcesStdoutTolerance = {
    "type": "probe",
    "name": "A dummy tolerance ready probe",
    "tolerance": {
        "type": "regex",
        "target": "stdout",
        "pattern": "Python [0-9]\.[0-9]\.[0-9]"
    },
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": ["-V"],
        "timeout": 1
    }
}

ProcProbe = {
    "type": "probe",
    "name": "This probe is a process probe",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": ["-V"],
        "timeout": 1
    }
}

DeprecatedProcArgumentsProbe = {
    "type": "probe",
    "name": "This probe is a process probe",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": {
            "-V": None
        },
        "timeout": 1
    }
}

ProcEchoArrayProbe = {
    "type": "probe",
    "name": "This probe is a process probe that simply echoes its arguments passed as an array",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": [
            "-c", "import sys; print(sys.argv)",
            "--empty",
            "--number", 1,
            "--string", "with spaces",
            "--string", "a second string with the same option"
        ],
        "timeout": 1
    }
}

ProcEchoStrProbe = {
    "type": "probe",
    "name": "This probe is a process probe that simply echoes its arguments passed as a string",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "process",
        "path": sys.executable,
        "arguments": "-c 'import sys; print(sys.argv)' --empty --number 1 --string 'with spaces' --string 'a second string with the same option'",
        "timeout": 1
    }
}

HTTPProbe = {
    "type": "probe",
    "name": "This probe is a HTTP probe",
    "provider": {
        "type": "http",
        "url": "http://example.com",
        "method": "post",
        "arguments": {
            "q": "chaostoolkit",
        },
        "timeout": 30
    },
    "pauses": {
        "before": 0,
        "after": 0.1
    }
}

BackgroundPythonModuleProbe = {
    "type": "probe",
    "name": "a-background-probe",
    "background": True,
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": __file__,
        }
    }
}


def must_be_in_range(a: int, b: int, value: Any = None) -> bool:
    if not (a < int(value.get("body")) < b):
        raise ActivityFailed("body is not in expected range")
    else:
        return True

FailProbe = {
    "name": "a name",
    "type": "probe",
    "tolerance": True,
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "force_failed_activity"
    }
}


GenerateSecretTokenProbe = {
    "type": "probe",
    "name": "generate-token",
    "provider": {
        "type": "python",
        "module": "random",
        "func": "choice",
        "arguments": {
            "seq": ["RED", "BLUE", "YELLOW"]
        }
    }
}


ReadSecretTokenProbe = {
    "type": "action",
    "name": "use-token",
    "provider": {
        "type": "python",
        "module": "pprint",
        "func": "pformat",
        "arguments": {
            "object": "${my_token}"
        }
    }
}


ReadSecretTokenFromSecretsProbe = {
    "type": "action",
    "name": "use-token",
    "provider": {
        "type": "python",
        "module": "pprint",
        "func": "pformat",
        "secrets": ["mytokens"],
        "arguments": {
            "object": "${my_token}"
        }
    }
}