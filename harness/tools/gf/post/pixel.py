"""이미지 모델이 그린 '가짜 픽셀 아트'(큰 해상도에 흐릿한 격자)를 진짜 1x 픽셀 아트로 바꾼다."""

import numpy as np

from gf.core.output import GfError

MIN_CONFIDENCE = 0.25


def edge_profile(pixels: np.ndarray, axis: int) -> np.ndarray:
    """이웃한 열(axis=1) 또는 행(axis=0) 사이의 색 차이 합. 격자 경계에서 값이 솟는다."""
    alpha = pixels[..., 3:4].astype(np.float32) / 255
    premultiplied = np.concatenate([pixels[..., :3] * alpha, pixels[..., 3:4]], axis=-1)
    difference = np.abs(np.diff(premultiplied, axis=axis))
    return difference.sum(axis=(1 - axis, 2))


def _score(profile: np.ndarray, cell: float) -> tuple[float, float]:
    """칸 크기 cell 의 격자선이 전체 경계 세기 중 우연보다 얼마나 더 설명하는지(0~1)와 시작 위치.

    진짜 칸의 배수는 격자선 사이의 경계를 놓쳐 설명하는 몫이 줄고, 약수는 같은 몫을 설명하지만
    우연으로 맞는 몫이 커서 둘 다 진짜 칸보다 점수가 낮다.
    """
    length = len(profile)
    offsets = np.arange(0, cell, 0.5)[:, None]
    lines = np.rint(offsets + np.arange(int(length / cell) + 2)[None, :] * cell).astype(int) - 1
    valid = (lines >= 0) & (lines < length)
    explained = np.where(valid, profile[np.clip(lines, 0, length - 1)], 0).sum(axis=1) / profile.sum()
    chance = valid.sum(axis=1) / length
    excess = (explained - chance) / (1 - chance)
    best = int(np.argmax(excess))
    return float(excess[best]), float(offsets[best, 0])


def _candidates(low: float, high: float, length: int) -> list[float]:
    """이미지 끝에서 격자가 반 픽셀 넘게 어긋나지 않을 만큼 촘촘한 칸 크기 후보."""
    cells = []
    cell = low
    while cell <= high:
        cells.append(cell)
        cell *= 1 + 0.5 / length
    return cells


def _refine(profile: np.ndarray, cell: float) -> tuple[float, float, float]:
    """격자가 이미지 전체를 정수 칸으로 나누는 경우가 많으므로 그 값이 더 잘 맞으면 그쪽을 쓴다."""
    whole = (len(profile) + 1) / max(1, round((len(profile) + 1) / cell))
    scored = [(*_score(profile, candidate), candidate) for candidate in (whole, cell)]
    score, offset, chosen = max(scored, key=lambda item: item[0])
    return chosen, offset, score


def detect_cell(pixels: np.ndarray, min_cell: float = 2, max_cell: float = 64) -> dict:
    """아트 픽셀 한 칸의 크기(소수 가능)와 격자 시작 위치를 찾는다.

    이미지 모델이 그린 픽셀 아트는 칸이 5.12px 처럼 정수가 아닌 경우가 흔하다.
    """
    height, width = pixels.shape[:2]
    limit = min(max_cell, min(height, width) / 4)
    if limit < min_cell:
        raise GfError(f"이미지가 너무 작아 격자를 찾을 수 없다: {width}x{height}")
    columns, rows = edge_profile(pixels, 1), edge_profile(pixels, 0)
    if columns.sum() == 0 or rows.sum() == 0:
        raise GfError("이미지가 단색이라 격자를 찾을 수 없다.")
    cells = _candidates(min_cell, limit, max(height, width))
    scores = [min(_score(columns, cell)[0], _score(rows, cell)[0]) for cell in cells]
    best = cells[int(np.argmax(scores))]
    (cx, ox, sx), (cy, oy, sy) = _refine(columns, best), _refine(rows, best)
    return {"cell": [round(cx, 3), round(cy, 3)], "offset": [ox, oy], "confidence": round(min(sx, sy), 3)}


def require_grid(detected: dict) -> None:
    if detected["confidence"] < MIN_CONFIDENCE:
        raise GfError(
            f"격자를 확신할 수 없다 (신뢰도 {detected['confidence']} < {MIN_CONFIDENCE}). "
            "이미 1x 이거나 격자가 고르지 않다. --cell 또는 --size 로 직접 지정한다."
        )


def _sample_positions(length: int, cell: float, offset: float) -> np.ndarray:
    """칸마다 가운데 절반에서 고른 표본 좌표. 칸 가장자리는 이웃 색이 번져 있어 피한다."""
    start = offset if offset <= cell / 2 else offset - cell
    count = max(1, round((length - start) / cell))
    taps = min(5, max(1, int(cell // 2) | 1))
    fractions = np.linspace(0.25, 0.75, taps) if taps > 1 else np.array([0.5])
    positions = start + (np.arange(count)[:, None] + fractions[None, :]) * cell
    return np.clip(np.floor(positions).astype(int), 0, length - 1)


def snap(pixels: np.ndarray, cell: tuple[float, float], offset: tuple[float, float]) -> np.ndarray:
    """칸마다 표본의 중앙값 한 색으로 줄인 1x 이미지."""
    height, width = pixels.shape[:2]
    xs = _sample_positions(width, cell[0], offset[0])
    ys = _sample_positions(height, cell[1], offset[1])
    samples = pixels[ys[:, :, None, None], xs[None, None, :, :]]
    samples = samples.transpose(0, 2, 1, 3, 4).reshape(len(ys), len(xs), -1, 4)
    small = np.rint(np.median(samples, axis=2)).astype(np.uint8)
    opaque = small[..., 3] >= 128
    small[..., 3] = np.where(opaque, 255, 0)
    small[~opaque, :3] = 0
    return small


def upscale(pixels: np.ndarray, scale: int) -> np.ndarray:
    return pixels.repeat(scale, axis=0).repeat(scale, axis=1)


def integer_scale(pixels: np.ndarray, limit: int = 64) -> int:
    """이미지가 정수배로 확대된 픽셀 아트라면 그 배율, 아니면 1."""
    height, width = pixels.shape[:2]
    for scale in range(min(limit, height, width), 1, -1):
        if height % scale or width % scale:
            continue
        small = pixels[::scale, ::scale]
        if np.array_equal(upscale(small, scale), pixels):
            return scale
    return 1
