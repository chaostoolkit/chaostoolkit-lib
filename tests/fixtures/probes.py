# -*- coding: utf-8 -*-
import sys


EmptyProbe = {}

MissingTypeProbe = {
    "module": "blah",
    "title": "a title",
    "layer": "kubernetes"
}

UnknownTypeProbe = {
    "type": "whatever",
    "title": "a title",
    "layer": "kubernetes"
}

MissingModuleProbe = {
    "type": "python",
    "title": "a title",
    "layer": "kubernetes"
}

NotImportableModuleProbe = {
    "type": "python",
    "module": "fake.module",
    "func": "myfunc",
    "title": "a title",
    "layer": "kubernetes"
}

MissingFunctionProbe = {
    "type": "python",
    "module": "os.path",
    "title": "missing function name",
    "title": "a title",
    "layer": "kubernetes"
}

MissingProcessPathProbe = {
    "type": "process",
    "title": "missing proc path",
    "layer": "kubernetes"
}

ProcessPathDoesNotExistProbe = {
    "type": "process",
    "path": "somewhere/not/here",
    "title": "invalid proc path",
    "layer": "kubernetes"
}

MissingHTTPUrlProbe = {
    "type": "http",
    "title": "A probe without url",
    "layer": "kubernetes"
}

MissingFuncArgProbe = {
    "type": "python",
    "module": "os.path",
    "func": "exists",
    "title": "a title",
    "layer": "kubernetes",
    "arguments": {}
}

TooManyFuncArgsProbe = {
    "title": "This probe has way too many args",
    "type": "python",
    "module": "os.path",
    "func": "exists",
    "layer": "kubernetes",
    "arguments": {
        "path": "/some/path",
        "should_not_be_here": "indeed not"
    }
}

PythonModuleProbe = {
    "title": "This probe is a Python probe",
    "type": "python",
    "module": "os.path",
    "func": "exists",
    "layer": "kubernetes",
    "arguments": {
        "path": __file__,
    },
    "timeout": 30,
    "pauses": {
        "before": 0,
        "after": 0.1
    }
}

ProcProbe = {
    "title": "This probe is a process probe",
    "type": "process",
    "path": sys.executable,
    "layer": "kubernetes",
    "arguments": {
        "-V": None
    },
    "timeout": 1,
    "pauses": {
        "before": 0,
        "after": 0.1
    }
}

HTTPProbe = {
    "title": "This probe is a HTTP probe",
    "type": "http",
    "url": "http://example.com",
    "method": "post",
    "layer": "kubernetes",
    "arguments": {
        "q": "chaostoolkit",
    },
    "timeout": 30,
    "pauses": {
        "before": 0,
        "after": 0.1
    }
}

BackgroundPythonModuleProbe = {
    "title": "This probe is a Python probe",
    "type": "python",
    "module": "os.path",
    "func": "exists",
    "layer": "kubernetes",
    "arguments": {
        "path": __file__,
    },
    "background": True
}
