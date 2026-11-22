"""chroma, pixel-snap, palette, inspect: 테스트 안에서 만든 합성 이미지로 검증한다."""

import argparse
import json

import numpy as np
import pytest
from PIL import Image, ImageDraw

from gf.core.output import GfError
from gf.post import chroma, commands, inspect_image, palette, pixel

SPRITE_COLOURS = np.array([[30, 30, 40], [220, 60, 50], [250, 210, 90], [60, 140, 220]], dtype=np.uint8)


def run(project, *argv) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(project))
    commands.register(parser.add_subparsers(dest="group"))
    args = parser.parse_args(["post", *argv])
    return args.func(args)


def last_json(capsys) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def make_sprite(size: int = 16, seed: int = 1) -> np.ndarray:
    """투명 테두리 안에 네 가지 색이 무작위로 놓인 1x 스프라이트."""
    rng = np.random.default_rng(seed)
    sprite = np.zeros((size, size, 4), dtype=np.uint8)
    inner = rng.integers(0, len(SPRITE_COLOURS), (size - 4, size - 4))
    sprite[2:-2, 2:-2, :3] = SPRITE_COLOURS[inner]
    sprite[2:-2, 2:-2, 3] = 255
    return sprite


def fake_hd(sprite: np.ndarray, cell: int, seed: int = 2) -> np.ndarray:
    """모델이 그린 가짜 픽셀 아트 흉내: 확대 뒤 살짝 흐리고 잡음을 얹는다."""
    rng = np.random.default_rng(seed)
    big = pixel.upscale(sprite, cell).astype(np.float32)
    blurred = (big + np.roll(big, 1, axis=0) + np.roll(big, 1, axis=1)) / 3
    noisy = blurred + rng.normal(0, 3, blurred.shape)
    noisy[..., 3] = blurred[..., 3]
    return np.clip(np.rint(noisy), 0, 255).astype(np.uint8)


def test_pixel_snap_recovers_grid_and_colours():
    sprite = make_sprite()
    hd = fake_hd(sprite, 8)
    detected = pixel.detect_cell(hd)
    assert detected["cell"] == [8, 8]
    pixel.require_grid(detected)
    small = pixel.snap(hd, tuple(detected["cell"]), tuple(detected["offset"]))
    assert small.shape == sprite.shape
    assert np.array_equal(small[..., 3], sprite[..., 3])
    error = np.abs(small[..., :3].astype(int) - sprite[..., :3].astype(int))
    assert error.max() <= 8


def test_pixel_snap_finds_shifted_grid():
    sprite = make_sprite(seed=5)
    hd = np.roll(fake_hd(sprite, 6), (3, 3), axis=(0, 1))
    detected = pixel.detect_cell(hd)
    assert detected["cell"] == [6, 6]
    assert detected["offset"] == [3, 3]


def test_pixel_snap_detects_fractional_cell():
    """512px 에 100칸(5.12px)처럼 정수가 아닌 격자. 실제 모델 출력에서 본 형태다."""
    sprite = make_sprite(size=50, seed=7)
    hd = np.array(Image.fromarray(sprite, "RGBA").resize((256, 256), Image.Resampling.NEAREST))
    detected = pixel.detect_cell(hd)
    assert detected["cell"] == [5.12, 5.12]
    small = pixel.snap(hd, tuple(detected["cell"]), tuple(detected["offset"]))
    assert np.array_equal(small, sprite)


def test_pixel_snap_rejects_image_without_grid():
    rng = np.random.default_rng(0)
    noise = rng.integers(0, 255, (64, 64, 4), dtype=np.uint8)
    noise[..., 3] = 255
    with pytest.raises(GfError, match="격자"):
        pixel.require_grid(pixel.detect_cell(noise))


def test_pixel_snap_command_writes_1x_and_preview(tmp_path, capsys):
    Image.fromarray(fake_hd(make_sprite(), 8), "RGBA").save(tmp_path / "hero.png")
    assert run(tmp_path, "pixel-snap", "hero.png", "--out", "out") == 0
    result = last_json(capsys)
    assert result["images"][0]["cell"] == [8, 8]
    assert Image.open(tmp_path / "out/hero.png").size == (16, 16)
    assert result["files"] == ["out/hero.png"]
    assert result["previews"] == ["captures/inspect/pixel/out/hero_x8.png"]
    assert Image.open(tmp_path / "captures/inspect/pixel/out/hero_x8.png").size == (128, 128)
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["hero.png"]


def test_pixel_snap_preview_cannot_share_the_output_folder(tmp_path):
    Image.fromarray(fake_hd(make_sprite(), 8), "RGBA").save(tmp_path / "hero.png")
    with pytest.raises(GfError, match="--preview"):
        run(tmp_path, "pixel-snap", "hero.png", "--out", "out", "--preview", "out")
    assert run(tmp_path, "pixel-snap", "hero.png", "--out", "out", "--no-preview") == 0
    assert not (tmp_path / "captures").exists()


def test_resize_keeps_edges_free_of_hidden_colour_and_canvas_uniform(tmp_path, capsys):
    for index, width in enumerate((400, 360)):
        frame = np.zeros((400, 400, 4), dtype=np.uint8)
        frame[..., :3] = (0, 255, 0)  # 투명한 곳에 숨은 배경색
        frame[100:400, 20:width - 20] = (200, 40, 40, 255)
        Image.fromarray(frame, "RGBA").save(tmp_path / f"f{index}.png")
    assert run(tmp_path, "resize", "f0.png", "f1.png", "--height", "100", "--out", "small") == 0
    result = last_json(capsys)
    assert result["factor"] == 0.25 and result["uniform_canvas"] is True
    small = np.array(Image.open(tmp_path / "small/f0.png"))
    assert small.shape == (100, 100, 4)
    visible = small[small[..., 3] > 8]
    assert visible[:, 1].max() < 80, "투명 영역의 초록이 가장자리에 번졌다"
    assert small[60, 50].tolist() == [200, 40, 40, 255] and small[5, 50, 3] == 0

    assert run(tmp_path, "resize", "f0.png", "--scale", "0.1", "--canvas", "64x48", "--out", "pad") == 0
    padded = np.array(Image.open(tmp_path / "pad/f0.png"))
    assert padded.shape == (48, 64, 4) and padded[47, 32, 3] == 255 and padded[0, 32, 3] == 0
    with pytest.raises(GfError, match="정확히 하나"):
        run(tmp_path, "resize", "f0.png", "--out", "x")


def test_pixel_snap_with_target_size_handles_fractional_cells():
    sprite = make_sprite(size=12)
    hd = np.array(Image.fromarray(pixel.upscale(sprite, 10), "RGBA").resize((100, 100), Image.Resampling.BILINEAR))
    small = pixel.snap(hd, (100 / 12, 100 / 12), (0, 0))
    assert small.shape[:2] == (12, 12)
    opaque = sprite[..., 3] == 255
    error = np.abs(small[opaque][:, :3].astype(int) - sprite[opaque][:, :3].astype(int))
    assert (error.max(axis=1) <= 12).mean() > 0.95


def magenta_scene() -> np.ndarray:
    """마젠타 배경 위에 안티에일리어싱된 원. 가장자리에 마젠타가 섞인다."""
    image = Image.new("RGB", (256, 256), (255, 0, 255))
    ImageDraw.Draw(image).ellipse([48, 48, 208, 208], fill=(40, 160, 220))
    small = image.resize((64, 64), Image.Resampling.LANCZOS)
    return np.array(small.convert("RGBA"))


def test_chroma_keys_magenta_and_removes_fringe():
    scene = magenta_scene()
    key = chroma.border_colour(scene)
    assert chroma.to_hex(key) == "#FF00FF"
    keyed = chroma.key_out(scene, key)
    assert keyed[0, 0, 3] == 0 and keyed[32, 2, 3] == 0
    assert tuple(keyed[32, 32]) == (40, 160, 220, 255)
    visible = keyed[keyed[..., 3] > 0].astype(int)
    pinkish = (visible[:, 0] > visible[:, 1] + 30) & (visible[:, 2] > visible[:, 1] + 30)
    assert not pinkish.any()
    assert 0.25 < (keyed[..., 3] > 0).mean() < 0.32


def test_chroma_hard_alpha_is_binary():
    keyed = chroma.key_out(magenta_scene(), chroma.parse_colour("#FF00FF"), hard=True)
    assert set(np.unique(keyed[..., 3])) <= {0, 255}


def test_chroma_despills_green_edge():
    scene = np.zeros((9, 9, 4), dtype=np.uint8)
    scene[..., :3] = (0, 255, 0)
    scene[..., 3] = 255
    scene[2:7, 2:7, :3] = (200, 180, 160)
    scene[2, 2:7, :3] = (150, 230, 120)
    keyed = chroma.key_out(scene, chroma.parse_colour("#00FF00"), erode=0)
    r, g, b, a = keyed[2, 4].astype(int)
    assert a > 0 and g <= max(r, b)
    assert tuple(keyed[4, 4]) == (200, 180, 160, 255)


def test_chroma_rejects_bad_colour():
    with pytest.raises(GfError):
        chroma.parse_colour("magenta")


def test_palette_extract_and_apply_reduce_colours(tmp_path, capsys):
    rng = np.random.default_rng(3)
    base = SPRITE_COLOURS[rng.integers(0, 4, (32, 32))].astype(int)
    noisy = np.clip(base + rng.integers(-10, 11, base.shape), 0, 255).astype(np.uint8)
    pixels = np.dstack([noisy, np.full((32, 32), 255, dtype=np.uint8)])
    pixels[:4, :, 3] = 0
    Image.fromarray(pixels, "RGBA").save(tmp_path / "noisy.png")

    assert run(tmp_path, "palette", "extract", "noisy.png", "--colors", "4", "--out", "design/palette.json") == 0
    extracted = last_json(capsys)
    assert extracted["count"] == 4
    saved = json.loads((tmp_path / "design/palette.json").read_text())
    assert len(saved["colors"]) == 4
    assert Image.open(tmp_path / "design/palette.png").size == (8 * 32, 32)
    found = palette.load(tmp_path / "design/palette.json").astype(int)
    for colour in SPRITE_COLOURS.astype(int):
        assert np.abs(found - colour).sum(axis=1).min() <= 24

    assert run(tmp_path, "palette", "apply", "noisy.png", "--out", "out") == 0
    applied = last_json(capsys)["images"][0]
    assert applied["colours_before"] > 100
    assert applied["colours_after"] == 4
    result = np.array(Image.open(tmp_path / "out/noisy.png"))
    assert np.array_equal(result[..., 3], pixels[..., 3])


def test_palette_apply_picks_nearest_colour():
    table = np.array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=np.uint8)
    pixels = np.array([[[10, 5, 0, 255], [240, 250, 245, 255], [200, 40, 30, 255], [9, 9, 9, 0]]], dtype=np.uint8)
    mapped = palette.apply(pixels, table)
    assert mapped[0, :3, :3].tolist() == [[0, 0, 0], [255, 255, 255], [255, 0, 0]]
    assert mapped[0, 3].tolist() == [0, 0, 0, 0]


def test_palette_extract_keeps_exact_colours_when_few():
    sprite = make_sprite()
    colours = palette.extract([sprite], 16)
    assert {tuple(c) for c in colours.tolist()} <= {tuple(c) for c in SPRITE_COLOURS.tolist()}


def test_palette_loads_hex_file(tmp_path):
    (tmp_path / "p.hex").write_text("ff0000\n00ff00\n")
    assert palette.load(tmp_path / "p.hex").tolist() == [[255, 0, 0], [0, 255, 0]]


def test_inspect_tells_true_pixel_art_from_fake(tmp_path, capsys):
    sprite = make_sprite()
    true_report = inspect_image.report(sprite, 64)
    assert true_report["pixel_art"] and true_report["unique_colours"] <= 4
    assert true_report["size"] == [16, 16]
    assert true_report["alpha_coverage"] == round(144 / 256, 4)

    upscaled = inspect_image.report(pixel.upscale(sprite, 4), 64)
    assert upscaled["integer_scale"] == 4 and not upscaled["pixel_art"]

    fake = inspect_image.report(fake_hd(sprite, 8), 64)
    assert not fake["pixel_art"] and fake["unique_colours"] > 64

    Image.fromarray(sprite, "RGBA").save(tmp_path / "s.png")
    assert run(tmp_path, "inspect", "s.png", "--check", "captures/check.png", "--check-scale", "4") == 0
    assert last_json(capsys)["files"] == ["captures/check.png"]
    check = Image.open(tmp_path / "captures/check.png")
    assert check.size == (2 * (64 + 64), 64 + 64)
    assert check.getpixel((0, 0)) == inspect_image.LIGHT and check.getpixel((check.width - 1, 0)) == inspect_image.DARK


def test_outputs_outside_project_are_rejected(tmp_path):
    project = tmp_path / "game"
    project.mkdir()
    Image.fromarray(make_sprite(), "RGBA").save(project / "s.png")
    with pytest.raises(GfError, match="프로젝트 안"):
        run(project, "chroma", "s.png", "--out", "../elsewhere")


def test_pixel_snap_trim_and_height_scale_the_subject_not_the_canvas(tmp_path, capsys):
    canvas = np.zeros((512, 512, 4), dtype=np.uint8)
    canvas[100:340, 200:360] = (220, 60, 50, 255)  # 대상은 160x240, 화면의 일부
    Image.fromarray(canvas, "RGBA").save(tmp_path / "hero.png")
    assert run(tmp_path, "pixel-snap", "hero.png", "--trim", "--height", "24", "--out", "out", "--no-preview") == 0
    report = last_json(capsys)["images"][0]
    assert report["size"] == [16, 24] and report["cell_source"] == "height"
    assert np.array(Image.open(tmp_path / "out/hero.png"))[..., 3].min() == 255


def test_resize_trim_scales_the_subject_not_the_canvas(tmp_path, capsys):
    """생성 그림에서 대상은 화면의 일부다(실측 1024px 중 762px). --trim 없이는 --height 가 빈 여백까지 센다."""
    (tmp_path / ".gf").mkdir()
    image = np.zeros((400, 400, 4), dtype=np.uint8)
    image[100:300, 150:250] = (200, 90, 40, 255)
    Image.fromarray(image, "RGBA").save(tmp_path / "subject.png")

    run(tmp_path, "resize", "subject.png", "--trim", "--height", "50", "--out", "trimmed")
    assert last_json(capsys)["images"][0] == {"file": "trimmed/subject.png", "from": [100, 200], "size": [25, 50]}
    run(tmp_path, "resize", "subject.png", "--height", "50", "--out", "whole")
    assert last_json(capsys)["images"][0]["size"] == [50, 50]

    Image.fromarray(np.zeros((8, 8, 4), dtype=np.uint8), "RGBA").save(tmp_path / "empty.png")
    with pytest.raises(GfError, match="보이는 픽셀이 없어"):
        run(tmp_path, "resize", "empty.png", "--trim", "--height", "4", "--out", "trimmed")


def test_resize_inset_removes_the_frame_around_a_generated_tile(tmp_path, capsys):
    """모델이 타일에 둘러 준 테두리 선(실측 1024px 에 22px)을 잘라 내야 타일을 이었을 때 줄이 안 보인다."""
    (tmp_path / ".gf").mkdir()
    tile = np.full((120, 120, 4), (190, 110, 60, 255), dtype=np.uint8)
    tile[:10], tile[-10:], tile[:, :10], tile[:, -10:] = [(20, 25, 60, 255)] * 4
    Image.fromarray(tile, "RGBA").save(tmp_path / "tile.png")

    run(tmp_path, "resize", "tile.png", "--inset", "12", "--height", "32", "--out", "out")
    report = last_json(capsys)["images"][0]
    assert report["from"] == [96, 96] and report["size"] == [32, 32]
    small = np.array(Image.open(tmp_path / "out/tile.png").convert("RGBA"))
    assert np.abs(small[..., :3].astype(int) - (190, 110, 60)).max() <= 2

    with pytest.raises(GfError, match="남는 것이 없다"):
        run(tmp_path, "resize", "tile.png", "--inset", "60", "--height", "32", "--out", "out")
