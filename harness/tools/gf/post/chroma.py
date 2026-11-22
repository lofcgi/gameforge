"""단색 배경을 알파로 뺀다. 가장자리에 남는 배경색 번짐과 1px 테두리까지 지운다."""

import numpy as np

from gf.core.output import GfError


def parse_colour(text: str) -> np.ndarray:
    value = text.lstrip("#")
    if len(value) != 6:
        raise GfError(f"색은 #RRGGBB 형태다: {text}")
    try:
        return np.array([int(value[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)
    except ValueError as exc:
        raise GfError(f"색은 #RRGGBB 형태다: {text}") from exc


def to_hex(colour: np.ndarray) -> str:
    return "#" + "".join(f"{round(float(c)):02X}" for c in colour[:3])


def border_colour(pixels: np.ndarray) -> np.ndarray:
    """이미지 테두리 2px 의 중앙값. 모델이 낸 배경색은 지정한 값과 조금 다르다."""
    edges = [pixels[:2], pixels[-2:], pixels[:, :2], pixels[:, -2:]]
    border = np.concatenate([edge.reshape(-1, 4)[:, :3] for edge in edges])
    return np.median(border, axis=0).astype(np.float32)


def dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    """8방향 팽창."""
    result = mask
    for _ in range(radius):
        padded = np.pad(result, 1)
        height, width = result.shape
        grown = np.zeros_like(result)
        for dy in range(3):
            for dx in range(3):
                grown |= padded[dy : dy + height, dx : dx + width]
        result = grown
    return result


def _despill(rgb: np.ndarray, key: np.ndarray, band: np.ndarray) -> None:
    """band 안에서 키 색 쪽으로 치우친 만큼을 키의 강한 채널에서 뺀다."""
    high = key >= 128
    if high.all() or not high.any():
        return
    spill = rgb[..., high].min(axis=-1) - rgb[..., ~high].max(axis=-1)
    spill = np.where(band, np.clip(spill, 0, None), 0)
    rgb[..., high] -= spill[..., None]


def key_out(
    pixels: np.ndarray,
    key: np.ndarray,
    tolerance: float = 60,
    soft: float = 40,
    erode: int = 1,
    despill: int = 3,
    hard: bool = False,
) -> np.ndarray:
    rgb = pixels[..., :3].astype(np.float32)
    distance = np.linalg.norm(rgb - key, axis=-1)
    cover = (distance > tolerance).astype(np.float32)
    if soft > 0:
        cover = np.clip((distance - tolerance) / soft, 0, 1)
    # 반투명 가장자리는 배경색이 섞여 있으므로 그 몫을 빼서 원래 색을 되찾는다.
    partial = (cover > 0) & (cover < 1)
    safe = np.where(partial, cover, 1)[..., None]
    rgb = np.where(partial[..., None], (rgb - (1 - safe) * key) / safe, rgb)
    alpha = cover * pixels[..., 3]
    if erode:
        alpha[dilate(alpha == 0, erode)] = 0
    if despill:
        _despill(rgb, key, dilate(alpha == 0, despill) & (alpha > 0))
    if hard:
        alpha = np.where(alpha >= 128, 255, 0)
    rgb[alpha == 0] = 0
    result = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)])
    return np.rint(result).astype(np.uint8)
