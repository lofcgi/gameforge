import json

import pytest

from gf.cli import build_parser
from gf.core.output import GfError
from gf.core.paths import TEMPLATES
from gf.engine.adapter import parse_size
from gf.play import script

NAMES = ["godot-2d", "godot-3d", "web-2d", "web-3d"]


def test_bridge_copies_are_identical_per_engine():
    assert (TEMPLATES / "godot-2d/gf/gf_bridge.gd").read_bytes() == (TEMPLATES / "godot-3d/gf/gf_bridge.gd").read_bytes()
    assert (TEMPLATES / "web-2d/gf/bridge.js").read_bytes() == (TEMPLATES / "web-3d/gf/bridge.js").read_bytes()


@pytest.mark.parametrize("name", NAMES)
def test_template_has_agent_guide_and_clear_script(name):
    template = TEMPLATES / name
    assert (template / "AGENTS.md").is_file()
    assert script.load(template / "bot/clear.json")["events"]


@pytest.mark.parametrize("name", NAMES)
def test_template_carries_no_build_output(name):
    """gf init 은 템플릿을 통째로 복사한다. 캐시가 섞여 있으면 새 프로젝트가 오염된다."""
    template = TEMPLATES / name
    assert not (template / "node_modules").exists()
    assert not (template / ".godot").exists()
    assert not list(template.rglob("*.uid"))


@pytest.mark.parametrize("name", ["godot-2d", "godot-3d"])
def test_godot_template_registers_bridge_and_actions(name):
    project = (TEMPLATES / name / "project.godot").read_text()
    assert 'GfBridge="*res://gf/gf_bridge.gd"' in project
    main = (TEMPLATES / name / "scripts/main.gd").read_text()
    assert "GfBridge.state_provider" in main and "GfBridge.info" in main
    for event in script.load(TEMPLATES / name / "bot/clear.json")["events"]:
        assert f"\n{event['action']}={{" in project


def test_godot_2d_is_pixel_perfect():
    project = (TEMPLATES / "godot-2d/project.godot").read_text()
    for setting in (
        "textures/canvas_textures/default_texture_filter=0",
        'window/stretch/mode="viewport"',
        'window/stretch/scale_mode="integer"',
        "2d/snap/snap_2d_transforms_to_pixel=true",
        "art/pixels_per_unit=1",
    ):
        assert setting in project


def _init(tmp_path, engine: str, style: str, capsys) -> dict:
    project = tmp_path / f"{engine}-{style}"
    args = build_parser().parse_args(["--project", str(project), "init", "--engine", engine, "--dim", "2d", "--style", style])
    assert args.func(args) == 0
    return {**json.loads(capsys.readouterr().out.strip().splitlines()[-1]), "project": project}


def test_init_keeps_pixel_rendering_for_pixel_style(tmp_path, capsys):
    godot = _init(tmp_path, "godot", "pixel", capsys)
    assert godot["render"] == {"units": [320, 180], "pixels_per_unit": 1, "filter": "nearest", "scaling": "integer"}
    assert (godot["project"] / "project.godot").read_bytes() == (TEMPLATES / "godot-2d/project.godot").read_bytes()
    web = _init(tmp_path, "web", "pixel", capsys)
    assert "ppu: 1, smooth: false" in (web["project"] / "src/view.js").read_text()


def test_init_switches_non_pixel_2d_to_window_resolution(tmp_path, capsys):
    """픽셀이 아닌 그림을 320x180 nearest 로 그리면 뭉개진다. --style 2d 는 레벨 단위는 두고 화면만 바꾼다."""
    godot = _init(tmp_path, "godot", "2d", capsys)
    assert godot["render"] == {"units": [320, 180], "pixels_per_unit": 4, "filter": "linear", "scaling": "window"}
    project = (godot["project"] / "project.godot").read_text()
    for setting in (
        'window/stretch/mode="canvas_items"',
        'window/stretch/scale_mode="fractional"',
        "textures/canvas_textures/default_texture_filter=1",
        "2d/snap/snap_2d_transforms_to_pixel=false",
        "2d/snap/snap_2d_vertices_to_pixel=false",
        "art/pixels_per_unit=4",
        "window/size/viewport_width=320",
    ):
        assert setting in project
    assert "integer" not in project and "=true" not in project.split("[rendering]")[1]
    web = _init(tmp_path, "web", "2d", capsys)
    assert "ppu: 4, smooth: true" in (web["project"] / "src/view.js").read_text()


def test_init_fails_when_template_line_to_patch_is_missing(tmp_path):
    from gf.core import render_profile

    (tmp_path / "src").mkdir()
    (tmp_path / "src/view.js").write_text("export const VIEW = { w: 320, h: 180 };\n")
    with pytest.raises(GfError, match="정확히 한 번 찾지 못해"):
        render_profile.apply(tmp_path, "web-2d", "2d")
    assert render_profile.apply(tmp_path, "web-3d", "3d-code") is None


def test_2d_templates_place_art_by_pixels_per_unit():
    """그림 크기를 단위당 픽셀로 나누는 곳이 도우미 한 군데여야 스타일을 바꿔도 게임 코드가 그대로다."""
    sheet = (TEMPLATES / "godot-2d/scripts/sprite_sheet.gd").read_text()
    assert 'ProjectSettings.get_setting("gameforge/art/pixels_per_unit", 1)' in sheet
    assert sheet.count("Vector2.ONE / ") >= 4
    sprites = (TEMPLATES / "web-2d/src/sprites.js").read_text()
    for helper in ("drawFrame", "drawStanding", "drawTiled", "loadManifest"):
        assert f"function {helper}(" in sprites
    assert "VIEW.ppu" in sprites
    render = (TEMPLATES / "web-2d/src/render.js").read_text()
    assert "player.facing < 0" in render and "ctx.canvas.width / VIEW.w" in render


def test_web_2d_audio_waits_for_a_user_gesture():
    """입력 전에 AudioContext 를 만들면 Chrome 이 콘솔 경고를 내고 engine test 가 실패한다."""
    audio = (TEMPLATES / "web-2d/src/audio.js").read_text()
    unlock = audio.index("async function unlock()")
    assert audio.index("new AudioContext()") > unlock
    assert audio.count("new AudioContext()") == 1
    for event in ("keydown", "pointerdown"):
        assert event in audio


def test_godot_bridge_guards_held_keys_against_focus_loss():
    """앱이 포커스를 잃으면 Godot 이 눌린 키를 전부 뗀다. 브리지는 포커스를 고정하고, 그래도 풀리면 다시 눌러 오류로 남긴다."""
    bridge = (TEMPLATES / "godot-2d/gf/gf_bridge.gd").read_text()
    assert "NOTIFICATION_APPLICATION_FOCUS_OUT" in bridge and "func _pin_focus()" in bridge
    assert "func _restore_held()" in bridge and "push_error" in bridge
    assert '"yield_focus"' in bridge


def test_bridge_versions_match_the_harness():
    from gf.engine.adapter import BRIDGE_VERSION

    assert f"const BRIDGE := {BRIDGE_VERSION}\n" in (TEMPLATES / "godot-2d/gf/gf_bridge.gd").read_text()
    assert f"const BRIDGE = {BRIDGE_VERSION};\n" in (TEMPLATES / "web-2d/gf/bridge.js").read_text()


@pytest.mark.parametrize("name", ["web-2d", "web-3d"])
def test_web_input_keeps_taps_shorter_than_a_tick(name):
    source = (TEMPLATES / name / "src/input.js").read_text()
    assert "tapped.add(event.code)" in source and "tapped.clear()" in source


@pytest.mark.parametrize("name", ["godot-2d", "web-2d"])
def test_2d_clear_script_stops_past_the_goal(name):
    """끝까지 오른쪽을 누르고 있으면 캐릭터가 레벨 끝 벽에 붙어 화면 밖으로 잘린 채 목표 화면이 찍힌다."""
    events = script.load(TEMPLATES / name / "bot/clear.json")["events"]
    assert events[-1]["action"] == "right" and events[-1]["down"] is False


def test_web_3d_pins_three_with_lockfile():
    manifest = json.loads((TEMPLATES / "web-3d/package.json").read_text())
    assert "three" in manifest["dependencies"]
    assert (TEMPLATES / "web-3d/bun.lock").is_file()


def test_parse_size():
    assert parse_size("1280x720") == (1280, 720)
    for bad in ("1280", "0x720", "axb", "1x2x3"):
        with pytest.raises(GfError):
            parse_size(bad)


def test_engine_commands_are_registered():
    parser = build_parser()
    for argv in (
        ["engine", "run", "--record", "--seconds", "5"],
        ["engine", "record"],
        ["engine", "capture", "--out", "captures/x", "--at", "1,2", "--script", "a.json", "--size", "640x360"],
        ["engine", "bot", "--policy", "goal", "--seconds", "10"],
        ["engine", "replay", "abc"],
        ["engine", "perf", "--seconds", "2"],
        ["engine", "test"],
    ):
        assert callable(parser.parse_args(argv).func)


@pytest.mark.parametrize("name", ["godot-2d", "godot-3d"])
def test_godot_does_not_import_harness_output(name):
    """.gdignore 가 없으면 Godot 이 스크린샷과 생성 원본을 전부 텍스처로 가져온다."""
    for directory in ("captures", "assets/raw", "references", "design"):
        assert (TEMPLATES / name / directory / ".gdignore").is_file()


def test_3d_templates_turn_model_front_plus_z_toward_movement():
    """GLB 의 정면은 +Z 다 (templates/README.md 7절). 두 템플릿이 같은 식으로 돌려야 한다."""
    godot = (TEMPLATES / "godot-3d/scripts/player.gd").read_text()
    web = (TEMPLATES / "web-3d/src/core.js").read_text()
    assert "return atan2(direction.x, direction.y)" in godot and "atan2(-" not in godot
    assert "return Math.atan2(x, z)" in web and "atan2(-" not in web
    assert "정면은 +Z" in (TEMPLATES / "README.md").read_text()
