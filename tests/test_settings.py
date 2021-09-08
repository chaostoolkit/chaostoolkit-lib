import os.path

from chaoslib.settings import (
    get_loaded_settings,
    load_settings,
    locate_settings_entry,
    save_settings,
)

settings_dir = os.path.join(os.path.dirname(__file__), "fixtures")


def test_do_not_fail_when_settings_do_not_exist():
    assert load_settings(os.path.join(settings_dir, "no_settings.yaml")) is None


def test_load_settings():
    settings = load_settings(os.path.join(settings_dir, "settings.yaml"))
    assert "notifications" in settings


def test_save_settings():
    settings = load_settings(os.path.join(settings_dir, "settings.yaml"))
    new_settings_location = os.path.join(settings_dir, "new_settings.yaml")
    try:
        os.remove(new_settings_location)
    except OSError:
        pass
    save_settings(settings, new_settings_location)
    saved_settings = load_settings(new_settings_location)
    assert "notifications" in saved_settings
    os.remove(new_settings_location)


def test_load_unsafe_settings():
    settings = load_settings(os.path.join(settings_dir, "unsafe-settings.yaml"))
    assert settings is None


def test_create_settings_file_on_save():
    ghost = os.path.abspath(os.path.join(settings_dir, "bah", "ghost.yaml"))
    assert not os.path.exists(ghost)
    try:
        save_settings({}, ghost)
        assert os.path.exists(ghost)
    finally:
        try:
            os.remove(ghost)
        except OSError:
            pass


def test_get_loaded_settings():
    settings = load_settings(os.path.join(settings_dir, "settings.yaml"))
    assert get_loaded_settings() is settings


def test_locate_root_level_entry():
    settings = {"auths": {"chaos.example.com": {"type": "bearer"}}}
    parent, entry, k, i = locate_settings_entry(settings, "auths")
    assert parent == settings
    assert entry == settings["auths"]
    assert k == "auths"
    assert i is None


def test_locate_dotted_entry():
    settings = {"auths": {"chaos.example.com": {"type": "bearer"}}}
    parent, entry, k, i = locate_settings_entry(settings, "auths.chaos\\.example\\.com")
    assert parent == settings["auths"]
    assert entry == {"type": "bearer"}
    assert k == "chaos.example.com"
    assert i is None


def test_locate_indexed_entry():
    settings = {
        "auths": {
            "chaos.example.com": {
                "type": "bearer",
                "headers": [
                    {"name": "X-Client", "value": "blah"},
                    {"name": "X-For", "value": "other"},
                ],
            }
        }
    }
    parent, entry, k, i = locate_settings_entry(
        settings, "auths.chaos\\.example\\.com.headers[1]"
    )
    assert parent == settings["auths"]["chaos.example.com"]["headers"]
    assert entry == {"name": "X-For", "value": "other"}
    assert k is None
    assert i == 1


def test_locate_dotted_key_from_indexed_entry():
    settings = {
        "auths": {
            "chaos.example.com": {
                "type": "bearer",
                "headers": [
                    {"name": "X-Client", "value": "blah"},
                    {"name": "X-For", "value": "other"},
                ],
            }
        }
    }
    parent, entry, k, i = locate_settings_entry(
        settings, "auths.chaos\\.example\\.com.headers[1].name"
    )
    assert parent == settings["auths"]["chaos.example.com"]["headers"][1]
    assert entry == "X-For"
    assert k == "name"
    assert i is None


def test_cannot_locate_dotted_entry():
    settings = {"auths": {"chaos.example.com": {"type": "bearer"}}}
    assert locate_settings_entry(settings, "auths.chaos.example.com") is None
