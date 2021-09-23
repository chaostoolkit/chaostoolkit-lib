from typing import Any, Dict

EmptyConfig = {}

SomeConfig: Dict[str, Any] = {
    "name": "Jane",
    "age": 34,
    "path": {"type": "env", "key": "PATH"},
}
