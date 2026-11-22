import numpy as np
import pytest
from PIL import Image

from gf.core.output import GfError
from gf.engine import image


def _save(path, pixels):
    Image.fromarray(pixels.astype(np.uint8), "RGB").save(path)
    return path


def test_uniform_image_is_blank(tmp_path):
    path = _save(tmp_path / "black.png", np.zeros((90, 160, 3)))
    assert image.dominant_fraction(path) == 1.0
    assert image.is_blank(path)


def test_scene_with_shapes_is_not_blank(tmp_path):
    pixels = np.full((90, 160, 3), 30)
    pixels[70:, :] = (110, 115, 130)
    pixels[56:70, 20:30] = (240, 220, 90)
    assert not image.is_blank(_save(tmp_path / "scene.png", pixels))


def test_few_stray_pixels_still_count_as_blank(tmp_path):
    pixels = np.zeros((100, 100, 3))
    pixels[0, :10] = 255
    assert image.is_blank(_save(tmp_path / "stray.png", pixels))


def test_require_rendered_names_blank_and_missing_files(tmp_path):
    blank = _save(tmp_path / "blank.png", np.full((10, 10, 3), 200))
    with pytest.raises(GfError, match="blank.png"):
        image.require_rendered([blank])
    with pytest.raises(GfError, match="nope.png"):
        image.require_rendered([tmp_path / "nope.png"])
