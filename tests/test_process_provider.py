# -*- coding: utf-8 -*-
import os.path
from chaoslib.provider.process import run_process_activity

settings_dir = os.path.join(os.path.dirname(__file__), "fixtures")


def test_process_not_utf8_cannot_fail():
    result = run_process_activity({
        "provider": {
            "type": "process",
            "path": "python",
            "arguments": '-c "import sys; sys.stdout.buffer.write(bytes(\'é\', \'latin-1\'))"'
        }
    }, None, None)

    assert result['status'] == 0
    assert result['stderr'] == u''
    assert result['stdout'] == u'é'
