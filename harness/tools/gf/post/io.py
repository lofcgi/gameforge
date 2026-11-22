"""후처리 공용: 이미지 목록 펴기와 RGBA 배열 입출력. 경로 해석은 gf.core.paths 에 있다."""

from pathlib import Path

import numpy as np
from PIL import Image

from gf.core.output import GfError
from gf.core.paths import source

IMAGE_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".gif"}


def images(project: Path, values: list[str]) -> list[Path]:
    """파일과 폴더를 섞어 받아 이미지 파일 목록으로 편다. 폴더 안은 이름순이다."""
    found: list[Path] = []
    for value in values:
        path = source(project, value)
        if path.is_dir():
            found += sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
        else:
            found.append(path)
    if not found:
        raise GfError(f"이미지가 하나도 없다: {', '.join(values)}")
    return found


def load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.array(image.convert("RGBA"))


def save_rgba(pixels: np.ndarray, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels, "RGBA").save(path)
    return path


def unique_colours(pixels: np.ndarray) -> int:
    """보이는 픽셀(알파 > 0)의 서로 다른 RGB 수."""
    visible = pixels[pixels[..., 3] > 0][:, :3]
    return len(np.unique(visible, axis=0))
