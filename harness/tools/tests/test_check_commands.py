import json
import os

import pytest
from PIL import Image

from gf import cli
from gf.core import check_commands as check
from gf.core import state


def make_project(tmp_path, stage="graybox", style="2d", engine="godot"):
    (tmp_path / ".gf").mkdir()
    data = state.new("t", engine, "2d", style)
    data["stage"] = stage
    state.save(tmp_path, data)
    for folder in ("scripts", "assets/game", "assets/raw", "captures", "design/look"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "scripts" / "main.gd").write_text("extends Node\n")
    return tmp_path


def touch(path, when):
    os.utime(path, (when, when))


def write_result(project, passed=True):
    target = project / check.TEST_RESULT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"ok": passed}))
    return target


def shot(project, name="captures/now/shot_01.png"):
    target = project / name
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), (10, 200, 10)).save(target)
    return target


def loud(_path):
    return {"duration_s": 1.0, "mean_db": -20.0, "max_db": -3.0}


def silent(_path):
    return {"duration_s": 1.0, "mean_db": -91.0, "max_db": -91.0}


@pytest.fixture
def project(tmp_path):
    return make_project(tmp_path)


def test_plan_needs_brief(tmp_path):
    project = make_project(tmp_path, stage="plan")
    assert check.evidence_report(project, "plan")["problems"]
    (project / "design" / "brief.md").write_text("# 요약\n")
    assert not check.evidence_report(project, "plan")["problems"]


def test_look_needs_direction_and_image(tmp_path):
    project = make_project(tmp_path, stage="look")
    assert len(check.evidence_report(project, "look")["problems"]) == 2
    (project / "design" / "art-direction.md").write_text("규칙\n")
    Image.new("RGB", (4, 4)).save(project / "design" / "look" / "frame.png")
    assert not check.evidence_report(project, "look")["problems"]


def test_graybox_without_any_evidence_fails(project):
    problems = check.evidence_report(project, "graybox")["problems"]
    assert any("스모크 테스트 기록" in p for p in problems)
    assert any("스크린샷" in p for p in problems)


def test_graybox_with_fresh_evidence_passes(project):
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    assert not check.evidence_report(project, "graybox")["problems"]


def test_evidence_older_than_code_change_is_stale(project):
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    touch(project / "scripts" / "main.gd", 3000)
    problems = check.evidence_report(project, "graybox")["problems"]
    assert any("오래됐다" in p and "scripts/main.gd" in p for p in problems)
    assert any("스크린샷" in p for p in problems)


def test_failed_smoke_result_blocks(project):
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project, passed=False), 2000)
    touch(shot(project), 2000)
    assert any("실패" in p for p in check.evidence_report(project, "graybox")["problems"])


def test_first_frame_and_judge_images_do_not_count_as_shots(project):
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project, "captures/test/first_frame.png"), 2000)
    touch(shot(project, "captures/judge/p1/X.png"), 2000)
    assert any("스크린샷" in p for p in check.evidence_report(project, "graybox")["problems"])


def test_changes_outside_the_game_do_not_stale_evidence(project):
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    for name in ("assets/raw/a.png", "design/brief.md", "bot/clear.json", ".godot/cache.gd"):
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x")
        touch(target, 5000)
    assert not check.evidence_report(project, "graybox")["problems"]


def test_new_game_asset_stales_evidence(project):
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    touch(shot(project, "assets/game/tree.png"), 3000)
    assert check.evidence_report(project, "graybox")["problems"]


def test_missing_and_empty_asset_references(project):
    (project / "scripts" / "main.gd").write_text(
        'var a = load("res://assets/game/hero.png")\n'
        'var b = load("res://assets/game/empty.png")\n'
        'var c = load("res://assets/game/ok.png")\n'
        '# load("res://assets/game/commented.png")\n'
    )
    (project / "assets/game/empty.png").write_bytes(b"")
    shot(project, "assets/game/ok.png")
    report = check.assets_report(project)
    assert report["references"] == 3
    assert any("hero.png 이 없다" in p for p in report["problems"])
    assert any("empty.png 이 빈 파일" in p for p in report["problems"])
    assert len(report["problems"]) == 2


def test_reference_guarded_by_exists_is_optional(project):
    (project / "scripts" / "player.gd").write_text(
        'const SHEET := "res://assets/game/player_sheet.png"\n'
        "func _ready():\n\tif ResourceLoader.exists(SHEET):\n\t\tpass\n"
    )
    report = check.assets_report(project)
    assert report["problems"] == []
    assert report["optional_missing"] == ["assets/game/player_sheet.png"]


def test_web_references_resolve_relative_to_project(tmp_path):
    project = make_project(tmp_path, engine="web")
    (project / "src").mkdir()
    (project / "src" / "sprites.js").write_text(
        'export const SHEETS = { player: { url: "./assets/game/p.png" } };\n'
        "const remote = 'https://example.com/x.png';\n"
        "const dynamic = `assets/game/${name}.png`;\n"
    )
    assert any("assets/game/p.png" in p for p in check.assets_report(project)["problems"])
    shot(project, "assets/game/p.png")
    assert check.assets_report(project)["problems"] == []


def test_pixel_project_rejects_unprocessed_art(tmp_path):
    project = make_project(tmp_path, style="pixel")
    crisp = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    crisp.putpixel((3, 3), (255, 0, 0, 255))
    crisp.putpixel((4, 3), (0, 0, 255, 255))
    crisp.save(project / "assets/game/crisp.png")
    assert check.assets_report(project)["problems"] == []
    crisp.resize((64, 64), Image.NEAREST).save(project / "assets/game/upscaled.png")
    report = check.assets_report(project)
    assert len(report["problems"]) == 1 and "upscaled.png" in report["problems"][0]
    assert any("pixel-snap" in hint for hint in report["hints"])


def test_non_pixel_project_ignores_pixel_rule(project):
    Image.new("RGBA", (64, 64), (5, 5, 5, 120)).save(project / "assets/game/soft.png")
    assert check.assets_report(project)["problems"] == []


def test_audio_missing_empty_and_silent(project):
    (project / "scripts" / "main.gd").write_text(
        'var a = load("res://assets/game/audio/jump.ogg")\n'
        'var b = load("res://assets/game/audio/empty.wav")\n'
        'var c = load("res://assets/game/audio/hit.mp3")\n'
    )
    (project / "assets/game/audio").mkdir()
    (project / "assets/game/audio/empty.wav").write_bytes(b"")
    (project / "assets/game/audio/hit.mp3").write_bytes(b"data")
    report = check.audio_report(project, [], require=True, measure=silent)
    assert report["referenced"] == 3
    assert any("jump.ogg 이 없다" in p for p in report["problems"])
    assert any("empty.wav 이 빈 파일" in p for p in report["problems"])
    assert any("hit.mp3 은 소리가 없다" in p for p in report["problems"])
    (project / "assets/game/audio/jump.ogg").write_bytes(b"data")
    (project / "assets/game/audio/empty.wav").write_bytes(b"data")
    assert check.audio_report(project, [], require=True, measure=loud)["problems"] == []


def test_silent_build_fails_only_when_required(project):
    assert check.audio_report(project, [], require=False, measure=loud)["problems"] == []
    problems = check.audio_report(project, [], require=True, measure=loud)["problems"]
    assert any("소리 없는 빌드" in p for p in problems)


def test_extra_audio_files_are_measured(project):
    target = project / "assets/raw/sfx/coin.mp3"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"data")
    report = check.audio_report(project, [target], require=False, measure=loud)
    assert report["audio"] == [
        {"file": "assets/raw/sfx/coin.mp3", "exists": True, "bytes": 4,
         "duration_s": 1.0, "mean_db": -20.0, "max_db": -3.0}
    ]


def test_parse_volume():
    log = "  Duration: 00:01:02.50, start: 0\n[x] mean_volume: -23.4 dB\n[x] max_volume: -1.2 dB\n"
    assert check.parse_volume(log) == {"duration_s": 62.5, "mean_db": -23.4, "max_db": -1.2}
    assert check.parse_volume("max_volume: -inf dB")["max_db"] == float("-inf")
    assert check.parse_volume("not audio")["max_db"] is None


def test_polish_stage_checks_assets_and_audio(tmp_path):
    project = make_project(tmp_path, stage="polish")
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    problems = check.evidence_report(project, "polish", measure=loud)["problems"]
    assert problems and all("오디오" in p for p in problems)


def test_cli_evidence_fails_with_instructions(project, capsys):
    assert cli.main(["--project", str(project), "check", "evidence"]) == 1
    out = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert out["ok"] is False and "gf engine test" in out["error"]
    assert out["stage"] == "graybox"


def test_cli_evidence_stage_override(project, capsys):
    (project / "design" / "brief.md").write_text("요약")
    assert cli.main(["--project", str(project), "check", "evidence", "--stage", "plan"]) == 0
    assert json.loads(capsys.readouterr().out.splitlines()[-1])["ok"] is True


def test_cli_outside_project_fails(tmp_path, capsys):
    assert cli.main(["--project", str(tmp_path), "check", "assets"]) == 1
    assert ".gf" in json.loads(capsys.readouterr().out.splitlines()[-1])["error"]


def test_user_can_declare_a_silent_game(tmp_path):
    project = make_project(tmp_path, stage="polish")
    touch(project / "scripts" / "main.gd", 1000)
    touch(write_result(project), 2000)
    touch(shot(project), 2000)
    (project / ".gf" / "config.toml").write_text("[check]\nallow_silent = true\n")
    assert check.evidence_report(project, "polish", measure=loud)["problems"] == []


def test_inspect_adds_fields_and_warnings_for_loops(project):
    (project / "scripts" / "main.gd").write_text(
        'var a = load("res://assets/game/audio/jump.mp3")\n'
        'var b = load("res://assets/game/audio/theme.wav")\n'
        'var c = load("res://assets/game/audio/wind.wav")  # loop\n'
    )
    (project / "assets/game/audio").mkdir()
    for name in ("jump.mp3", "theme.wav", "wind.wav"):
        (project / "assets/game/audio" / name).write_bytes(b"data")
    loops = check.loop_hints(project)
    assert loops == {"assets/game/audio/theme.wav", "assets/game/audio/wind.wav"}

    def inspect(_path, loop):
        return {"rms_db": -20.0 if loop else -14.0, "loop": loop}, (["반복 이음매: 끊긴다"] if loop else [])

    report = check.audio_report(project, [], require=True, measure=loud, inspect=inspect, loops=frozenset(loops))
    assert report["problems"] == []
    assert report["warnings"] == ["assets/game/audio/theme.wav: 반복 이음매: 끊긴다", "assets/game/audio/wind.wav: 반복 이음매: 끊긴다"]
    assert report["balance"] == {"loop_rms_db": -20.0, "oneshot_rms_db_median": -14.0, "loop_minus_oneshot_db": -6.0}
    assert "warnings" not in check.audio_report(project, [], require=True, measure=loud)
