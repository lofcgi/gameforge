"""engine test 가 결과를 captures/test/result.json 에 직접 남기는지 (check evidence 의 근거)."""

import json

import pytest
from PIL import Image

from gf import cli
from gf.core import check_commands as check
from gf.core import state
from gf.core.output import GfError
from gf.engine import commands


class FakeGame:
    load_s = 0.2

    def __init__(self, deaf=False):
        self.header = {"tick_rate": 60, "info": {"actions": {"right": {"move": [1, 0]}}, "probe": ["right"]}}
        self.tick, self.x, self.held, self.deaf = 0, 0.0, False, deaf

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def state(self):
        return {"tick": self.tick, "t": self.tick / 60, "fps": 60, "level": "fake",
                "player": {"pos": [self.x, 0.0], "vel": [60.0 if self.held else 0.0, 0.0], "on_floor": True},
                "goal": {"pos": [100.0, 0.0], "reached": False}, "deaths": 0}

    def step(self, ticks):
        self.tick += ticks
        self.x += ticks if self.held else 0
        return self.state()

    def send_input(self, event):
        if not self.deaf:
            self.held = event["down"]

    def screenshot(self, path):
        image = Image.new("RGB", (16, 16), (20, 20, 20))
        image.paste((200, 60, 60), (0, 0, 8, 8))
        image.save(path)

    def logs(self):
        return []


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".gf").mkdir()
    state.save(tmp_path, state.new("t", "godot", "2d", "2d"))
    return tmp_path


def saved(project):
    return json.loads((project / check.TEST_RESULT).read_text())


def test_passing_test_writes_result(project, monkeypatch, capsys):
    monkeypatch.setattr(commands, "open_session", lambda p, options: FakeGame())
    assert cli.main(["--project", str(project), "engine", "test"]) == 0
    out = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert check.TEST_RESULT in out["files"]
    record = saved(project)
    assert record["ok"] is True and set(record["checks"].values()) == {"ok"} and record["load_s"] == 0.2


def test_failing_check_writes_failed_result(project, monkeypatch, capsys):
    monkeypatch.setattr(commands, "open_session", lambda p, options: FakeGame(deaf=True))
    assert cli.main(["--project", str(project), "engine", "test"]) == 1
    record = saved(project)
    assert record["ok"] is False and "input_liveness" in record["error"]


def test_boot_failure_overwrites_an_older_pass(project, monkeypatch, capsys):
    monkeypatch.setattr(commands, "open_session", lambda p, options: FakeGame())
    assert cli.main(["--project", str(project), "engine", "test"]) == 0

    def broken(p, options):
        raise GfError("게임이 뜨지 않았다")

    monkeypatch.setattr(commands, "open_session", broken)
    assert cli.main(["--project", str(project), "engine", "test"]) == 1
    record = saved(project)
    assert record["ok"] is False and record["error"] == "게임이 뜨지 않았다"


def test_check_smoke_is_gone(project):
    with pytest.raises(SystemExit):
        cli.main(["--project", str(project), "check", "smoke"])
