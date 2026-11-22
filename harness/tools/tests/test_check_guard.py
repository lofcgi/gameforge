"""hooks/guard.py 를 실제 훅처럼 표준 입력 JSON 으로 돌려 본다."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[2] / "hooks" / "guard.py"


def run(event, cwd):
    done = subprocess.run(
        [sys.executable, str(GUARD)], input=json.dumps({"cwd": str(cwd), **event}),
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)["hookSpecificOutput"] if done.stdout.strip() else None


def bash(command, cwd, **extra):
    return run({"tool_name": "Bash", "tool_input": {"command": command}, **extra}, cwd)


def tool(name, path, cwd, **extra):
    return run({"tool_name": name, "tool_input": {"file_path": str(path)}, **extra}, cwd)


@pytest.fixture
def game(tmp_path):
    project = tmp_path / "work" / "mygame"
    (project / ".gf").mkdir(parents=True)
    (tmp_path / "work" / ".env").write_text("FAL_KEY=secret\n")
    return project


@pytest.fixture
def elsewhere(tmp_path):
    folder = tmp_path / "other"
    folder.mkdir()
    (folder / ".env").write_text("X=1\n")
    return folder


@pytest.fixture
def guard():
    spec = importlib.util.spec_from_file_location("gf_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_silent_outside_gameforge_projects(elsewhere):
    assert tool("Read", elsewhere / ".env", elsewhere) is None
    assert bash("cat .env", elsewhere) is None
    assert bash("gf state approve", elsewhere) is None
    assert tool("Edit", elsewhere / "gf" / "bridge.js", elsewhere) is None


def test_env_read_is_denied_in_and_above_project(game):
    for path, cwd in ((game.parent / ".env", game), (game.parent / ".env", game.parent), (game / ".env.local", game)):
        result = tool("Read", path, cwd)
        assert result["permissionDecision"] == "deny"
        assert "gf doctor" in result["permissionDecisionReason"]
    assert tool("Read", game / ".env.example", game) is None
    assert run({"tool_name": "Grep", "tool_input": {"pattern": "KEY", "path": str(game.parent / ".env")}}, game)


def test_env_bash_commands(game):
    for command in ("cat .env", "cat ../.env | head -1", "grep FAL_KEY '../.env'", "source .env && echo $FAL_KEY",
                    "python -c \"print(open('.env').read())\""):
        assert bash(command, game)["permissionDecision"] == "deny", command
    for command in ("ls -la .env", "test -f ../.env && echo yes", "cp .env.example notes.txt", "echo environment"):
        assert bash(command, game) is None, command
    assert bash("cat .env", game.parent)["permissionDecision"] == "deny"


def test_records_and_bridge_are_not_hand_edited(game):
    for relative in (".gf/state.json", ".gf/judge/p1.json", ".gf/ledger.jsonl", "gf/gf_bridge.gd", "gf/bridge.js",
                     "captures/test/result.json"):
        assert tool("Write", game / relative, game)["permissionDecision"] == "deny", relative
    for relative in ("scripts/main.gd", ".gf/config.toml", "design/brief.md", "src/gf/bridge.js"):
        assert tool("Edit", game / relative, game) is None, relative


def test_deleting_records_is_denied(game):
    assert bash("rm -rf .gf/judge", game)["permissionDecision"] == "deny"
    assert bash("echo '{}' > .gf/state.json", game)["permissionDecision"] == "deny"
    assert bash("rm -rf captures/old", game) is None
    assert bash("cat .gf/state.json", game) is None


def test_blind_judge_reads_only_the_pair_folder(game):
    pair = game / "captures" / "judge" / "p1"
    pair.mkdir(parents=True)
    judge = {"agent_type": "gameforge:blind-judge"}
    assert tool("Read", pair / "X.png", game, **judge) is None
    assert tool("Read", pair / "rubric.md", game, **judge) is None
    for path in (game / ".gf" / "judge" / "p1.json", game / "design" / "brief.md", game / "captures" / "now" / "a.png"):
        assert tool("Read", path, game, **judge)["permissionDecision"] == "deny"
    assert tool("Read", game / "design" / "brief.md", game) is None
    assert tool("Read", game / "design" / "brief.md", game, agent_type="gameforge:playtest-reviewer") is None


def test_approve_is_gated_on_evidence(game, guard, monkeypatch, capsys):
    command = f'uv run -q --project "/h/tools" gf --project {game} state approve --note "ok"'
    assert guard.approve_target(command, Path("/tmp")) == game.resolve()
    assert guard.approve_target("gf state approve", game) == game.resolve()
    assert guard.approve_target(f"cd /tmp && gf --project {game} engine test && gf --project {game} state approve", Path("/tmp")) == game.resolve()
    assert guard.approve_target("gf --project /nowhere state approve", game) is None
    assert guard.approve_target('grep -rn "gf state approve" skills', game) is None
    assert guard.approve_target(f"gf --project {game} state show", game) is None

    monkeypatch.setattr(guard, "check_evidence", lambda project: "스크린샷이 없다")
    with pytest.raises(SystemExit):
        guard.guard_bash(command, Path("/tmp"))
    reason = json.loads(capsys.readouterr().out)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "스크린샷이 없다" in reason and "사용자" in reason

    monkeypatch.setattr(guard, "check_evidence", lambda project: None)
    guard.guard_bash(command, Path("/tmp"))
    guard.guard_bash(f"gf --project {game} state show", Path("/tmp"))
    assert capsys.readouterr().out == ""


def test_broken_input_never_blocks(game):
    done = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True, check=False)
    assert done.returncode == 0 and done.stdout == ""
    assert run({"tool_name": "Bash", "tool_input": None}, game) is None
    assert run({"tool_name": "Read", "tool_input": {}}, game) is None
