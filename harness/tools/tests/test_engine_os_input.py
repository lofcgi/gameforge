import pytest

from gf.core.output import GfError
from gf.engine import app_focus, os_input
from gf.engine.adapter import BRIDGE_VERSION, require_bridge


def test_key_names_cover_both_engines():
    assert os_input.keycode("Right") == os_input.keycode("ArrowRight") == 124
    assert os_input.keycode("Space") == 49
    assert os_input.keycode("A") == os_input.keycode("KeyA") == 0
    with pytest.raises(GfError):
        os_input.keycode("F13")


def test_key_for_action_and_raw_key():
    info = {"actions": {"jump": {"keys": ["Space", "Up"]}, "dash": {}}}
    assert os_input.key_for({"action": "jump", "down": True}, info) == "Space"
    assert os_input.key_for({"device": "key", "code": "KeyQ", "down": True}, info) == "KeyQ"
    with pytest.raises(GfError):
        os_input.key_for({"action": "dash", "down": True}, info)
    with pytest.raises(GfError):
        os_input.key_for({"device": "mouse", "code": 0, "down": True}, info)


def test_parse_frontmost_pid():
    assert app_focus.parse_pid('"pid"=851\n') == 851
    assert app_focus.parse_pid("") is None


def test_old_bridge_is_rejected_with_the_fix(tmp_path):
    require_bridge(BRIDGE_VERSION, tmp_path, "bridge.js", "web-2d")
    with pytest.raises(GfError) as error:
        require_bridge(None, tmp_path, "gf_bridge.gd", "godot-2d")
    assert "cp " in str(error.value) and "templates/godot-2d/gf/gf_bridge.gd" in str(error.value)
