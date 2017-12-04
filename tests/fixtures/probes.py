# -*- coding: utf-8 -*-
import sys


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
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {}
    },
    "name": "a name"
}

TooManyFuncArgsProbe = {
    "type": "probe",
    "name": "This probe has way too many args",
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
    "name": "This probe is a Python probe",
    "pauses": {
        "before": 0,
        "after": 0.1
    },
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": __file__,
        },
        "timeout": 30
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
        "arguments": {
            "-V": None
        },
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
    "name": "This probe is a Python probe",
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
