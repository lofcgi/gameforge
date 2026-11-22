"""픽셀 아트가 아닌 스프라이트의 크기 줄이기. 모든 입력에 같은 배율을 써서 프레임끼리 크기가 어긋나지 않게 한다."""

import numpy as np
from PIL import Image

from gf.core.output import GfError


def inset(pixels: np.ndarray, margin: int) -> np.ndarray:
    """네 가장자리를 margin 픽셀씩 잘라 낸다."""
    if margin < 0:
        raise GfError("--inset 은 0 이상이다.")
    height, width = pixels.shape[:2]
    if margin * 2 >= min(width, height):
        raise GfError(f"--inset {margin} 이 그림({width}x{height})보다 커서 남는 것이 없다.")
    return pixels[margin:height - margin, margin:width - margin] if margin else pixels


def scale(pixels: np.ndarray, factor: float, nearest: bool = False) -> np.ndarray:
    """RGBA 를 factor 배로. 알파를 미리 곱해 줄여서 투명 픽셀의 색이 가장자리에 번지지 않는다."""
    height, width = pixels.shape[:2]
    size = (max(1, round(width * factor)), max(1, round(height * factor)))
    if nearest:
        return np.array(Image.fromarray(pixels, "RGBA").resize(size, Image.Resampling.NEAREST))
    data = pixels.astype(np.float32) / 255
    data[..., :3] *= data[..., 3:4]
    channels = [
        np.array(Image.fromarray(data[..., index], "F").resize(size, Image.Resampling.LANCZOS))
        for index in range(4)
    ]
    out = np.clip(np.stack(channels, axis=-1), 0, 1)
    alpha = out[..., 3:4]
    out[..., :3] = np.where(alpha > 1 / 510, out[..., :3] / np.maximum(alpha, 1e-6), 0)
    return np.rint(np.clip(out, 0, 1) * 255).astype(np.uint8)


def pad(pixels: np.ndarray, canvas: tuple[int, int]) -> np.ndarray:
    """캔버스의 아래 가운데에 놓는다 (발 기준선이 캔버스 바닥에 온다)."""
    height, width = pixels.shape[:2]
    if width > canvas[0] or height > canvas[1]:
        raise GfError(f"줄인 그림({width}x{height})이 캔버스({canvas[0]}x{canvas[1]})보다 크다.")
    out = np.zeros((canvas[1], canvas[0], 4), dtype=np.uint8)
    left = (canvas[0] - width) // 2
    out[canvas[1] - height:, left:left + width] = pixels
    return out
