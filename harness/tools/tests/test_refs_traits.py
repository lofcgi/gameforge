import json

import numpy as np
import pytest
from PIL import Image

from gf.core.output import GfError
from gf.refs import picks, store, traits

RED, GREEN, BLUE = (200, 30, 30), (30, 160, 60), (20, 40, 180)


def stripes(path, size=(200, 100)):
    """왼쪽부터 빨강 50%, 초록 30%, 파랑 20%."""
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[:, :100] = RED
    pixels[:, 100:160] = GREEN
    pixels[:, 160:] = BLUE
    Image.fromarray(pixels).save(path)
    return path


def pixel_art(path, cell, cells=(24, 16), seed=1):
    rng = np.random.default_rng(seed)
    colours = np.array(
        [[20, 20, 40], [240, 200, 80], [200, 60, 60], [60, 180, 200]], dtype=np.uint8
    )
    small = colours[rng.integers(0, 4, size=(cells[1], cells[0]))]
    Image.fromarray(small).resize(
        (cells[0] * cell, cells[1] * cell), Image.Resampling.NEAREST
    ).save(path)
    return path


def noise(path, seed=2):
    rng = np.random.default_rng(seed)
    Image.fromarray(rng.integers(0, 256, size=(90, 160, 3), dtype=np.uint8)).save(path)
    return path


def test_known_palette_is_recovered(tmp_path):
    result = traits.analyse([stripes(tmp_path / "a.png")], k=3)
    assert [colour["rgb"] for colour in result["palette"]] == [list(RED), list(GREEN), list(BLUE)]
    assert [colour["share"] for colour in result["palette"]] == pytest.approx(
        [0.5, 0.3, 0.2], abs=0.02
    )
    assert result["palette"][0]["hex"] == "#c81e1e"


def test_palette_does_not_invent_colours_when_k_is_larger(tmp_path):
    result = traits.analyse([stripes(tmp_path / "a.png")], k=6)
    assert len(result["palette"]) == 3
    assert sum(colour["share"] for colour in result["palette"]) == pytest.approx(1.0, abs=0.001)


def test_small_vivid_accent_is_reported_separately(tmp_path):
    pixels = np.full((100, 100, 3), 60, dtype=np.uint8)
    pixels[50:, :] = 120
    pixels[:10, :20] = (255, 120, 0)
    Image.fromarray(pixels).save(tmp_path / "grey.png")
    result = traits.analyse([tmp_path / "grey.png"], k=2)
    assert all(
        len(set(colour["rgb"])) == 1 or colour["share"] > 0.4 for colour in result["palette"]
    )
    assert [colour["rgb"] for colour in result["accents"]] == [[255, 120, 0]]
    assert result["accents"][0]["share"] == pytest.approx(0.02, abs=0.005)
    Image.new("RGB", (32, 32), (90, 90, 90)).save(tmp_path / "flat.png")
    assert traits.analyse([tmp_path / "flat.png"], k=2)["accents"] == []


def test_palette_is_deterministic(tmp_path):
    path = noise(tmp_path / "n.png")
    assert traits.analyse([path], k=5)["palette"] == traits.analyse([path], k=5)["palette"]


def test_brightness_contrast_saturation_and_warmth(tmp_path):
    Image.new("RGB", (64, 64), (255, 255, 255)).save(tmp_path / "white.png")
    Image.new("RGB", (64, 64), (255, 0, 0)).save(tmp_path / "red.png")
    Image.new("RGB", (64, 64), (0, 0, 255)).save(tmp_path / "blue.png")
    white = traits.image_stats(tmp_path / "white.png")
    red = traits.image_stats(tmp_path / "red.png")
    blue = traits.image_stats(tmp_path / "blue.png")
    assert white["brightness"] == pytest.approx(1.0)
    assert white["contrast"] == 0 and white["saturation"] == 0 and white["edge_density"] == 0
    assert red["saturation"] == pytest.approx(1.0)
    assert red["warmth"] == pytest.approx(1.0) and blue["warmth"] == pytest.approx(-1.0)
    assert traits.analyse([tmp_path / "red.png"], 2)["temperature"] == "warm"
    assert traits.analyse([tmp_path / "blue.png"], 2)["temperature"] == "cool"
    assert traits.analyse([tmp_path / "white.png"], 2)["temperature"] == "neutral"


def test_edge_density_separates_flat_from_busy(tmp_path):
    flat = traits.image_stats(stripes(tmp_path / "flat.png"))
    busy = traits.image_stats(noise(tmp_path / "busy.png"))
    assert flat["edge_density"] < 0.05
    assert busy["edge_density"] > 0.5


@pytest.mark.parametrize("cell", [2, 4, 6, 8])
def test_pixel_art_cell_size_is_estimated(tmp_path, cell):
    stats = traits.image_stats(pixel_art(tmp_path / "p.png", cell))
    assert stats["pixel_cell"] == cell


def test_no_cell_size_for_non_pixel_art(tmp_path):
    assert traits.image_stats(noise(tmp_path / "n.png"))["pixel_cell"] is None
    Image.new("RGB", (64, 64), "white").save(tmp_path / "flat.png")
    assert traits.image_stats(tmp_path / "flat.png")["pixel_cell"] is None


def test_aspect_labels():
    assert traits.aspect_label(1920 / 1080) == "16:9"
    assert traits.aspect_label(640 / 480) == "4:3"
    assert traits.aspect_label(1080 / 1920) == "9:16"
    assert traits.aspect_label(3.5) == "기타"


def test_build_writes_traits_for_reference_and_anti(tmp_path):
    project = tmp_path
    (project / ".gf").mkdir()
    bright, dark = tmp_path / "bright.png", tmp_path / "dark.png"
    Image.new("RGB", (160, 90), (250, 220, 120)).save(bright)
    Image.new("RGB", (160, 90), (10, 20, 60)).save(dark)
    ref, _ = store.add(project, bright.read_bytes(), origin="manual")
    anti, _ = store.add(project, dark.read_bytes(), origin="manual")
    picks.set_item(project, ref["file"], picked=True, note="따뜻한 색")
    picks.set_item(project, anti["file"], picked=True, kind="anti")

    result = traits.build(project, k=4)

    saved = json.loads((store.picked(project) / "traits.json").read_text())
    assert saved == result
    assert result["reference"]["count"] == 1 and result["anti"]["count"] == 1
    assert result["reference"]["palette"][0]["hex"] == "#fadc78"
    assert result["anti"]["palette"][0]["hex"] == "#0a143c"
    assert result["difference"]["brightness"] > 0.5
    assert result["difference"]["warmth"] > 0.5
    assert result["reference"]["aspects"] == {"16:9": 1}
    assert result["notes"][ref["file"]]["note"] == "따뜻한 색"
    with Image.open(store.picked(project) / "traits-palette.png") as swatch:
        # 줄 순서: REF, REF ACCENT(선명한 색이 있을 때만), ANTI
        assert swatch.size == (760, 270)
        assert swatch.getpixel((400, 45)) == (250, 220, 120)
        assert swatch.getpixel((400, 135)) == (250, 220, 120)
        assert swatch.getpixel((400, 225)) == (10, 20, 60)
    # 결과 파일이 고른 항목으로 잡히면 안 된다.
    assert len(store.items(store.picked(project))) == 2


def test_build_requires_picked_references(tmp_path):
    (tmp_path / ".gf").mkdir()
    with pytest.raises(GfError, match="고른 레퍼런스가 없다"):
        traits.build(tmp_path, k=4)
