"""프레임마다 흔들리는 캐릭터를 한 기준선(발)과 한 가로 기준점에 맞추고 캔버스 크기를 통일한다."""

import numpy as np

from gf.core.output import GfError

ALPHA_THRESHOLD = 16


def measure(pixels: np.ndarray, anchor: str) -> dict:
    """보이는 영역의 경계 상자와 가로 기준점."""
    mask = pixels[..., 3] > ALPHA_THRESHOLD
    if not mask.any():
        raise GfError("보이는 픽셀이 없는 프레임이다")
    ys, xs = np.nonzero(mask)
    left, right, top, bottom = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    centre = xs.mean() + 0.5 if anchor == "mass" else (left + right) / 2
    return {"left": int(left), "right": int(right), "top": int(top), "bottom": int(bottom), "anchor": float(centre)}


def canvas_for(boxes: list[dict], pad: int) -> tuple[int, int]:
    half = max(max(b["anchor"] - b["left"], b["right"] - b["anchor"]) for b in boxes)
    height = max(b["bottom"] - b["top"] for b in boxes)
    return 2 * int(np.ceil(half)) + 2 * pad, height + 2 * pad


def place(pixels: np.ndarray, box: dict, size: tuple[int, int], pad: int) -> tuple[np.ndarray, list[int]]:
    """경계 상자를 잘라 발이 바닥선(캔버스 아래 - pad)에, 기준점이 가로 중앙에 오게 놓는다."""
    width, height = size
    crop = pixels[box["top"] : box["bottom"], box["left"] : box["right"]]
    x = round(width / 2 - (box["anchor"] - box["left"]))
    y = height - pad - crop.shape[0]
    if x < 0 or y < 0 or x + crop.shape[1] > width:
        raise GfError(f"캔버스 {width}x{height} 에 내용 {crop.shape[1]}x{crop.shape[0]} 이 들어가지 않는다")
    canvas = np.zeros((height, width, 4), dtype=np.uint8)
    canvas[y : y + crop.shape[0], x : x + crop.shape[1]] = crop
    return canvas, [x - box["left"], y - box["top"]]
