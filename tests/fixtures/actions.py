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
