"""frames, align, loop, sheet, contact: 합성 프레임 열과 ffmpeg 로 만든 시험 영상으로 검증한다."""

import argparse
import json
import subprocess

import numpy as np
import pytest
from PIL import Image

from gf.core.output import GfError
from gf.post import align, commands, frames, loop, sheet


def run(project, *argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(project))
    commands.register(parser.add_subparsers(dest="group"))
    args = parser.parse_args(["post", *argv])
    return args.func(args)


def last_json(capsys) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def blob(canvas: tuple[int, int], left: int, bottom: int, width: int, height: int) -> np.ndarray:
    pixels = np.zeros((canvas[1], canvas[0], 4), dtype=np.uint8)
    pixels[bottom - height : bottom, left : left + width] = (200, 80, 40, 255)
    return pixels


def save_frames(folder, arrays) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for index, pixels in enumerate(arrays):
        Image.fromarray(pixels, "RGBA").save(folder / f"f_{index:03d}.png")


def test_align_puts_feet_on_one_baseline(tmp_path, capsys):
    drifting = [blob((40, 40), 5 + i * 3, 30 - i * 2, 10, 12 + i) for i in range(4)]
    save_frames(tmp_path / "in", drifting)
    assert run(tmp_path, "align", "in", "--out", "out", "--pad", "2") == 0
    result = last_json(capsys)
    assert result["canvas"] == [14, 19]
    assert result["baseline_y"] == 17
    for name in sorted((tmp_path / "out").iterdir()):
        pixels = np.array(Image.open(name))
        assert pixels.shape[:2] == (19, 14)
        ys, xs = np.nonzero(pixels[..., 3])
        assert ys.max() + 1 == 17
        assert (xs.min(), xs.max() + 1) == (2, 12)


def test_align_reports_empty_frame(tmp_path):
    save_frames(tmp_path / "in", [blob((8, 8), 1, 6, 3, 3), np.zeros((8, 8, 4), dtype=np.uint8)])
    with pytest.raises(GfError, match="f_001.png"):
        run(tmp_path, "align", "in", "--out", "out")


def test_align_mass_anchor_ignores_thin_limb():
    body = blob((40, 20), 10, 18, 10, 10)
    body[10, 20:30] = (200, 80, 40, 255)
    assert align.measure(body, "bbox")["anchor"] == 20
    assert align.measure(body, "mass")["anchor"] < 17


def cycle(count: int, period: int) -> list[np.ndarray]:
    """period 프레임마다 같은 자세로 돌아오는 열."""
    arrays = []
    for index in range(count):
        phase = 2 * np.pi * index / period
        left = round(14 + 8 * np.sin(phase))
        height = round(10 + 4 * np.cos(phase))
        arrays.append(blob((40, 32), left, 28, 8, height))
    return arrays


def test_loop_finds_one_period():
    found = loop.find(cycle(20, 8), min_length=4)
    assert found["length"] == 8
    assert found["seam"] == 0
    assert found["start"] == 0


def test_loop_skips_non_cyclic_lead_in(tmp_path, capsys):
    lead = [blob((40, 32), 1, 10 + i, 3, 3) for i in range(3)]
    save_frames(tmp_path / "in", lead + cycle(14, 6))
    assert run(tmp_path, "loop", "in", "--out", "out", "--min-length", "4") == 0
    result = last_json(capsys)
    assert (result["start"], result["length"]) == (3, 6)
    assert len(result["files"]) == 6
    first = np.array(Image.open(tmp_path / "out/frame_0000.png"))
    assert np.array_equal(first, cycle(1, 6)[0])


def test_loop_needs_enough_frames():
    with pytest.raises(GfError):
        loop.find(cycle(4, 8), min_length=4)


def test_sheet_manifest_and_godot_resource(tmp_path, capsys):
    arrays = []
    for index in range(5):
        pixels = np.zeros((6, 4, 4), dtype=np.uint8)
        pixels[...] = (index * 40, 10, 10, 255)
        arrays.append(pixels)
    save_frames(tmp_path / "in", arrays)
    assert run(tmp_path, "sheet", "in", "--out", "assets/game/hero", "--name", "walk", "--fps", "10", "--columns", "3", "--padding", "1") == 0
    result = last_json(capsys)
    assert result["sheet_size"] == [14, 13]
    assert result["texture"] == "res://assets/game/hero/walk.png"

    data = json.loads((tmp_path / "assets/game/hero/walk.json").read_text())
    animation = data["animations"]["walk"]
    assert data["image"] == "walk.png" and data["frame_size"] == [4, 6]
    assert animation["fps"] == 10 and animation["loop"] is True
    assert animation["frames"][0] == {"x": 0, "y": 0, "w": 4, "h": 6}
    assert animation["frames"][4] == {"x": 5, "y": 7, "w": 4, "h": 6}

    packed = np.array(Image.open(tmp_path / "assets/game/hero/walk.png"))
    for index, rect in enumerate(animation["frames"]):
        region = packed[rect["y"] : rect["y"] + rect["h"], rect["x"] : rect["x"] + rect["w"]]
        assert np.array_equal(region, arrays[index])
    assert packed[6, 0, 3] == 0

    tres = (tmp_path / "assets/game/hero/walk.tres").read_text()
    assert tres.startswith('[gd_resource type="SpriteFrames" load_steps=7 format=3]')
    assert 'path="res://assets/game/hero/walk.png"' in tres
    assert tres.count("[sub_resource") == 5
    assert "region = Rect2(5, 7, 4, 6)" in tres
    assert '"name": &"walk"' in tres and '"speed": 10.0' in tres and '"loop": true' in tres


def test_sheet_rejects_mixed_sizes():
    with pytest.raises(GfError, match="align"):
        sheet.pack([np.zeros((4, 4, 4), np.uint8), np.zeros((5, 4, 4), np.uint8)], None, 0)


def test_contact_sheet_lists_every_image(tmp_path, capsys):
    save_frames(tmp_path / "in", [blob((20, 20), 2, 18, 6, 6) for _ in range(5)])
    assert run(tmp_path, "contact", "in", "--out", "captures/pick.png", "--columns", "3", "--thumb", "64") == 0
    result = last_json(capsys)
    assert result["count"] == 5 and result["index"]["4"] == "in/f_004.png"
    image = Image.open(tmp_path / "captures/pick.png")
    assert image.size == (3 * 72 + 8, 2 * (64 + 22 + 8) + 8)


@pytest.fixture
def grid_video(tmp_path):
    """왼쪽 절반은 빨강, 오른쪽 절반은 파랑인 1초짜리 영상."""
    target = tmp_path / "clip.mp4"
    source = "color=c=red:s=64x48:r=10:d=1[a];color=c=blue:s=64x48:r=10:d=1[b];[a][b]hstack"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-filter_complex", source, "-pix_fmt", "yuv420p", str(target)], check=True
    )
    return target


def test_frames_probe_and_count(tmp_path, grid_video, capsys):
    assert frames.probe(grid_video)["width"] == 128
    assert run(tmp_path, "frames", "clip.mp4", "--out", "frames", "--count", "5") == 0
    result = last_json(capsys)
    assert result["count"] == 5
    assert Image.open(tmp_path / result["files"][0]).size == (128, 48)


def test_frames_split_grid_slots(tmp_path, grid_video, capsys):
    assert run(tmp_path, "frames", "clip.mp4", "--out", "frames", "--fps", "4", "--grid", "2x1", "--names", "red,blue") == 0
    slots = last_json(capsys)["slots"]
    assert slots["red"]["rect"] == [0, 0, 64, 48] and slots["blue"]["rect"] == [64, 0, 64, 48]
    assert slots["red"]["count"] == 4
    red = np.array(Image.open(tmp_path / "frames/red/frame_0001.png").convert("RGB"))[24, 32]
    blue = np.array(Image.open(tmp_path / "frames/blue/frame_0001.png").convert("RGB"))[24, 32]
    assert red[0] > 200 and red[2] < 60
    assert blue[2] > 200 and blue[0] < 60


def test_frames_rejects_slot_outside_grid():
    with pytest.raises(GfError):
        frames.slot_rect(100, 100, 2, 2, 4, 0)
