import json

import pytest

from gf.core.output import GfError
from gf.play import session

HEADER = {"type": "header", "version": 1, "engine": "web", "tick_rate": 60, "seed": 5, "size": [320, 180],
          "info": {"actions": {"right": {"keys": ["ArrowRight"]}}}}
STATE = {"level": "l", "player": {"pos": [0, 0], "vel": [0, 0]}, "goal": {"pos": [9, 0], "reached": False}, "deaths": 0}
ENTRIES = [
    HEADER,
    {"type": "state", "tick": 6, "t": 0.1, "state": STATE},
    {"type": "input", "tick": 7, "t": 0.1167, "down": True, "device": "key", "code": "ArrowRight", "actions": ["right"]},
    {"type": "input", "tick": 40, "t": 0.6667, "down": False, "device": "key", "code": "ArrowRight", "actions": ["right"]},
    {"type": "state", "tick": 12, "t": 0.2, "state": STATE},
]


def _lines(entries):
    return [json.dumps(entry) for entry in entries]


def test_round_trip_through_file(tmp_path):
    path = tmp_path / "s.jsonl"
    path.write_text("".join(session.dump_line(entry) for entry in ENTRIES))
    loaded = session.load(path)
    assert loaded.header["seed"] == 5
    assert [entry["tick"] for entry in loaded.inputs] == [7, 40]
    assert [entry["tick"] for entry in loaded.samples] == [6, 12]
    assert loaded.last_tick == 40


def test_blank_lines_are_skipped():
    assert len(session.parse(["", *_lines(ENTRIES), "  "]).inputs) == 2


def test_header_only_session_has_tick_zero():
    assert session.parse(_lines([HEADER])).last_tick == 0


@pytest.mark.parametrize("lines, message", [
    ([], "header"),
    (_lines(ENTRIES[1:]), "header"),
    (_lines([{**HEADER, "version": 2}]), "버전"),
    (_lines([{k: v for k, v in HEADER.items() if k != "tick_rate"}]), "tick_rate"),
    (_lines([HEADER, {"type": "input", "tick": 1, "down": True}]), "session:2.*device"),
    (_lines([HEADER, {"type": "state", "tick": 1}]), "state"),
    (_lines([HEADER, {"type": "mystery"}]), "mystery"),
    ([json.dumps(HEADER), "{broken"], "session:2.*JSON"),
])
def test_malformed_sessions_are_rejected(lines, message):
    with pytest.raises(GfError, match=message):
        session.parse(lines)


def test_missing_file(tmp_path):
    with pytest.raises(GfError):
        session.load(tmp_path / "none.jsonl")
