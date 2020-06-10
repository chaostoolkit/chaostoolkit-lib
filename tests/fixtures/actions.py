EmptyAction = {}


DoNothingAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "do_nothing"
    }
}


EchoAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "echo_message",
        "arguments": {
            "message": "kaboom"
        }
    }
}


def echo(message: str):
    return message


EchoAction = {
    "type": "action",
    "name": "echo-message",
    "provider": {
        "type": "python",
        "module": "fixtures.actions",
        "func": "echo",
        "arguments": {
            "message": "${message}"
        }
    }
}


FailAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "force_failed_activity"
    }
}


InterruptAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "force_interrupting_experiment"
    }
}
SecretEchoAction = {
    "type": "action",
    "name": "echo-secret-key",
    "provider": {
        "type": "python",
        "module": "fixtures.actions",
        "func": "echo",
        "secrets": ["aws"],
        "arguments": {
            "message": "${mykey}"
        }
    }
}
