import os.path
import stat
from unittest.mock import MagicMock, patch

import pytest

from chaoslib.provider.process import run_process_activity

settings_dir = os.path.join(os.path.dirname(__file__), "fixtures")

# the script path shall be relative to chaostoolkit-lib folder
dummy_script = "./tests/dummy.sh"


def setup_module(module: pytest.Module) -> None:
    """
    setup any state specific to the execution of the given module.

    - create the dummy script that can be used as process action
    """
    with open(dummy_script, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("exit 0\n")

    # gives exec right on the script: chmod +x
    st = os.stat(dummy_script)
    os.chmod(dummy_script, st.st_mode | stat.S_IEXEC)


def teardown_module(module: pytest.Module) -> None:
    """
    teardown any state that was previously setup with a setup_module method.

    - delete the dummy script, once it's not needed anymore
    """
    os.remove(dummy_script)


def test_process_not_utf8_cannot_fail() -> None:
    result = run_process_activity(
        {
            "provider": {
                "type": "process",
                "path": "python",
                "arguments": (
                    "-c \"import sys; sys.stdout.buffer.write(bytes('é', 'latin-1'))\""
                ),
            }
        },
        {"": ""},
        {},
    )

    # unfortunately, this doesn't seem to work well on mac
    if result["status"] == 0:
        assert result["stderr"] == ""
        assert result["stdout"] == "é"


def test_process_homedir_relative_path() -> None:
    path = os.path.abspath(dummy_script).replace(os.path.expanduser("~"), "~")
    result = run_process_activity(
        {"provider": {"type": "process", "path": path, "arguments": ""}}, {"": ""}, {}
    )
    assert result["status"] == 0


def test_process_absolute_path() -> None:
    result = run_process_activity(
        {
            "provider": {
                "type": "process",
                "path": os.path.abspath(dummy_script),
                "arguments": "",
            }
        },
        {"": ""},
        {},
    )
    assert result["status"] == 0


def test_process_cwd_relative_path() -> None:
    result = run_process_activity(
        {"provider": {"type": "process", "path": dummy_script, "arguments": ""}},
        {"": ""},
        {},
    )
    assert result["status"] == 0


@patch("chaoslib.provider.process.logger")
def test_process_non_exit_zero_warning(logger: MagicMock) -> None:
    run_process_activity(
        {
            "provider": {
                "type": "process",
                "path": "python",
                "arguments": '-c "import sys; sys.exit(1)"',
            }
        },
        {"": ""},
        {},
    )

    assert logger.warning.call_count == 1
    assert (
        "This process returned a non-zero exit code." in logger.warning.call_args[0][0]
    )
