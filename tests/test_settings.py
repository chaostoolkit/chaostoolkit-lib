# -*- coding: utf-8 -*-
import os.path
from chaoslib.settings import load_settings, save_settings

settings_dir = os.path.join(os.path.dirname(__file__), "fixtures")


def test_do_not_fail_when_settings_do_not_exist():
    assert load_settings(
        os.path.join(settings_dir, "no_settings.yaml")) is None


def test_load_settings():
    settings = load_settings(os.path.join(settings_dir, "settings.yaml"))
    assert "notifications" in settings


def test_save_settings():
    settings = load_settings(os.path.join(settings_dir, "settings.yaml"))
    new_settings_location =  os.path.join(settings_dir, "new_settings.yaml")
    try:
        os.remove(new_settings_location)
    except OSError:
        pass
    save_settings(settings, new_settings_location)
    saved_settings = load_settings(new_settings_location)
    assert "notifications" in saved_settings
    os.remove(new_settings_location)
