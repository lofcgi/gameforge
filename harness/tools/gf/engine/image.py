"""스크린샷이 실제로 그려진 화면인지 판별한다."""

from pathlib import Path

import numpy as np
from PIL import Image

from gf.core.output import GfError

# 한 색이 화면의 이 비율 이상을 차지하면 아무것도 그려지지 않은 것으로 본다.
BLANK_DOMINANT_FRACTION = 0.995


def dominant_fraction(path: Path) -> float:
    pixels = np.asarray(Image.open(path).convert("RGB")).reshape(-1, 3)
    _, counts = np.unique(pixels, axis=0, return_counts=True)
    return float(counts.max() / len(pixels))


def is_blank(path: Path) -> bool:
    return dominant_fraction(path) >= BLANK_DOMINANT_FRACTION


def require_rendered(paths: list[Path]) -> None:
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise GfError(f"스크린샷 파일이 만들어지지 않았다: {', '.join(missing)}")
    blank = [str(p) for p in paths if is_blank(p)]
    if blank:
        raise GfError(f"스크린샷이 비어 있거나 단색이다 (렌더링 실패): {', '.join(blank)}")
