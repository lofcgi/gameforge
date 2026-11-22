"""trimesh 백엔드는 항상, Blender 백엔드는 Blender 가 설치돼 있을 때만 검증한다."""

import argparse
import json

import pytest
import trimesh
from PIL import Image

from gf.blender import commands, glb, runner
from gf.core.output import GfError

needs_blender = pytest.mark.skipif(runner.find_blender() is None, reason="Blender 가 설치돼 있지 않다")


def run(project, *argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(project))
    commands.register(parser.add_subparsers(dest="group"))
    args = parser.parse_args(["blender", *argv])
    return args.func(args)


def last_json(capsys) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


@pytest.fixture
def ball(tmp_path):
    """원점에서 벗어난 2m 높이의 타원체 (5120 삼각형)."""
    mesh = trimesh.creation.icosphere(subdivisions=4, radius=0.5)
    mesh.apply_scale([1, 2, 1])
    mesh.apply_translation([3, 4, 1])
    mesh.export(tmp_path / "ball.glb")
    return tmp_path


def test_info_with_trimesh(ball, capsys):
    assert run(ball, "info", "ball.glb", "--backend", "trimesh") == 0
    result = last_json(capsys)
    assert result["backend"] == "trimesh"
    assert result["triangles"] == 5120 and result["vertices"] == 2562
    assert result["bounds"] == {"min": [2.5, 3.0, 0.5], "max": [3.5, 5.0, 1.5]}
    assert result["height"] == 2.0 and result["up"] == "Y"
    assert result["has_armature"] is False and result["animations"] == []


def test_info_falls_back_to_trimesh_and_says_so(ball, capsys, monkeypatch):
    monkeypatch.setattr(runner, "find_blender", lambda: None)
    assert run(ball, "info", "ball.glb") == 0
    assert last_json(capsys)["backend"] == "trimesh"


def test_blender_commands_fail_clearly_without_blender(ball, monkeypatch):
    monkeypatch.setattr(runner, "find_blender", lambda: None)
    for argv in (["clean", "ball.glb"], ["decimate", "ball.glb", "--triangles", "100"], ["turntable", "ball.glb"]):
        with pytest.raises(GfError, match="brew install --cask blender"):
            run(ball, *argv)
    with pytest.raises(GfError, match="brew install --cask blender"):
        run(ball, "info", "ball.glb", "--backend", "blender")


def test_trimesh_backend_rejects_other_formats(tmp_path):
    (tmp_path / "a.fbx").write_bytes(b"x")
    with pytest.raises(GfError, match="glb"):
        glb.stats(tmp_path / "a.fbx")


def test_glb_json_reports_skins_and_animations(tmp_path):
    import struct

    document = json.dumps({"asset": {"version": "2.0"}, "skins": [{}], "animations": [{"name": "walk"}]}).encode()
    document += b" " * (-len(document) % 4)
    header = struct.pack("<4sII", b"glTF", 2, 20 + len(document)) + struct.pack("<I4s", len(document), b"JSON")
    (tmp_path / "rig.glb").write_bytes(header + document)
    assert glb.read_json(tmp_path / "rig.glb")["animations"][0]["name"] == "walk"
    (tmp_path / "bad.glb").write_bytes(b"not a glb file....")
    with pytest.raises(GfError, match="GLB 파일이 아니다"):
        glb.read_json(tmp_path / "bad.glb")


@needs_blender
def test_blender_info_matches_trimesh(ball, capsys):
    assert run(ball, "info", "ball.glb", "--backend", "blender") == 0
    result = last_json(capsys)
    assert result["backend"] == "blender"
    assert result["triangles"] == 5120
    assert result["bounds"] == {"min": [2.5, 3.0, 0.5], "max": [3.5, 5.0, 1.5]}


@needs_blender
def test_clean_decimate_rescale_chain(ball, capsys):
    assert run(ball, "clean", "ball.glb") == 0
    cleaned = last_json(capsys)
    assert cleaned["files"] == ["ball_clean.glb"]
    assert cleaned["after"]["bounds"]["min"] == pytest.approx([-0.5, 0.0, -0.5], abs=1e-4)

    assert run(ball, "decimate", "ball_clean.glb", "--triangles", "1000") == 0
    decimated = last_json(capsys)
    assert decimated["after"]["triangles"] <= 1000
    assert decimated["after"]["height"] == pytest.approx(2.0, abs=0.02)

    assert run(ball, "rescale", "ball_clean_decimated.glb", "--height", "1.8", "--out", "models/ball.glb") == 0
    scaled = last_json(capsys)
    assert scaled["after"]["height"] == pytest.approx(1.8, abs=1e-3)
    assert scaled["after"]["bounds"]["min"][1] == pytest.approx(0.0, abs=1e-4)

    # 다시 읽어도(다른 백엔드로) 같은 수치여야 엔진에서 본 크기와 같다.
    reread = glb.stats(ball / "models/ball.glb")
    assert reread["height"] == pytest.approx(1.8, abs=1e-3)
    assert reread["triangles"] == decimated["after"]["triangles"]


@needs_blender
def test_decimate_leaves_small_model_alone(ball, capsys):
    assert run(ball, "decimate", "ball.glb", "--triangles", "99999") == 0
    result = last_json(capsys)
    assert result["ratio"] == 1.0 and result["after"]["triangles"] == 5120


@needs_blender
def test_turntable_renders_and_builds_sheet(ball, capsys):
    assert run(ball, "turntable", "ball.glb", "--count", "3", "--size", "96") == 0
    result = last_json(capsys)
    assert len(result["files"]) == 4 and result["sheet"] == "captures/turntable/ball_sheet.png"
    render = Image.open(ball / result["files"][0])
    assert render.size == (96, 96)
    alpha = render.convert("RGBA").getchannel("A")
    assert alpha.getpixel((48, 48)) == 255 and alpha.getpixel((1, 1)) == 0


@needs_blender
def test_run_passes_arguments_and_reports_failure(ball, capsys):
    script = ball / "make.py"
    script.write_text(
        "import json, os, sys\n"
        "import bpy\n"
        "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
        "bpy.ops.mesh.primitive_cube_add()\n"
        "out = sys.argv[sys.argv.index('--') + 1]\n"
        "bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')\n"
        "open(os.environ['GF_RESULT'], 'w').write(json.dumps({'files': [out]}))\n"
    )
    assert run(ball, "run", "make.py", "--", "cube.glb") == 0
    assert last_json(capsys)["files"] == ["cube.glb"]
    assert glb.stats(ball / "cube.glb")["triangles"] == 12

    (ball / "bad.py").write_text("raise ValueError('boom')\n")
    with pytest.raises(GfError, match="boom"):
        run(ball, "run", "bad.py")
