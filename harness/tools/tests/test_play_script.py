import json

import pytest

from gf.core.output import GfError
from gf.play import script


def test_parse_expands_taps_and_sorts_by_time():
    parsed = script.parse({"seed": 3, "actions": [
        {"t": 1.0, "tap": "jump", "hold": 0.2},
        {"t": 0.5, "press": "right"},
        {"t": 1.1, "release": "right"},
    ]})
    assert parsed["seed"] == 3
    assert [(e["t"], e["action"], e["down"]) for e in parsed["events"]] == [
        (0.5, "right", True), (1.0, "jump", True), (1.1, "right", False), (1.2, "jump", False),
    ]


def test_bare_list_and_default_tap_hold():
    parsed = script.parse([{"t": 0, "tap": "jump"}])
    assert parsed["seed"] is None
    assert parsed["events"][1]["t"] == script.DEFAULT_TAP_HOLD


def test_raw_key_event():
    event = script.parse([{"t": 2, "key": "KeyA", "down": True}])["events"][0]
    assert event == {"t": 2.0, "down": True, "device": "key", "code": "KeyA"}


@pytest.mark.parametrize("item", [
    "press right",
    {"press": "right"},
    {"t": -1, "press": "right"},
    {"t": True, "press": "right"},
    {"t": 0},
    {"t": 0, "press": "a", "release": "a"},
    {"t": 0, "press": ""},
    {"t": 0, "tap": "jump", "hold": 0},
    {"t": 0, "key": "KeyA"},
])
def test_invalid_items_are_rejected(item):
    with pytest.raises(GfError, match=r"actions\[0\]"):
        script.parse([item])


def test_invalid_top_level_is_rejected():
    with pytest.raises(GfError):
        script.parse({"steps": []})


def test_to_ticks_rounds_to_nearest_tick():
    events = script.to_ticks([{"t": 0.5, "down": True, "action": "a"}, {"t": 0.26, "down": False, "action": "a"}], 60)
    assert [event["tick"] for event in events] == [30, 16]


def test_unknown_actions_are_reported():
    info = {"actions": {"left": {}, "right": {}}}
    script.require_known_actions([{"action": "left"}, {"device": "key", "code": "KeyQ"}], info)
    with pytest.raises(GfError, match="fly"):
        script.require_known_actions([{"action": "fly"}], info)


def test_load_reports_missing_and_malformed_files(tmp_path):
    with pytest.raises(GfError, match="없다"):
        script.load(tmp_path / "missing.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    with pytest.raises(GfError, match="JSON"):
        script.load(broken)
    good = tmp_path / "good.json"
    good.write_text(json.dumps([{"t": 0, "press": "right"}]))
    assert len(script.load(good)["events"]) == 1
