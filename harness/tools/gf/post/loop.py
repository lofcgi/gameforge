"""프레임 열에서 가장 매끄럽게 이어지는 반복 구간을 찾는다."""

import numpy as np
from PIL import Image

from gf.core.output import GfError

COMPARE_SIZE = 64
TIE_RATIO = 1.1


def _signature(pixels: np.ndarray) -> np.ndarray:
    """비교용 축소본. 투명 영역의 숨은 색이 차이로 잡히지 않게 알파를 곱한다."""
    alpha = pixels[..., 3:4].astype(np.float32) / 255
    premultiplied = np.concatenate([pixels[..., :3] * alpha, pixels[..., 3:4]], axis=-1)
    image = Image.fromarray(np.rint(premultiplied).astype(np.uint8), "RGBA")
    image.thumbnail((COMPARE_SIZE, COMPARE_SIZE), Image.Resampling.BOX)
    return np.asarray(image, dtype=np.float32) / 255


def find(frames: list[np.ndarray], min_length: int, max_length: int | None = None) -> dict:
    """frames[start:end] 를 반복했을 때 이음매(frames[end] 와 frames[start])가 가장 닮은 구간.

    끝 프레임 다음에 시작 프레임이 와야 하므로 frames[end] 가 frames[start] 와 같아지는 곳을 찾는다.
    """
    if len({frame.shape for frame in frames}) != 1:
        raise GfError("프레임 크기가 서로 다르다. 먼저 gf post align 으로 맞춘다.")
    count = len(frames)
    if count < min_length + 1:
        raise GfError(f"프레임 {count}장으로는 길이 {min_length} 이상의 반복을 찾을 수 없다.")
    signatures = np.stack([_signature(frame) for frame in frames]).reshape(count, -1)
    candidates = []
    for start in range(count - min_length):
        longest = count - 1 if max_length is None else min(count - 1, start + max_length)
        for end in range(start + min_length, longest + 1):
            score = float(np.abs(signatures[start] - signatures[end]).mean())
            candidates.append((score, end - start, start))
    best = min(score for score, _, _ in candidates)
    # 여러 주기가 들어 있으면 한 주기만 남도록 비슷한 점수 중 가장 짧은 구간을 고른다.
    score, length, start = min((c for c in candidates if c[0] <= best * TIE_RATIO + 1e-6), key=lambda c: (c[1], c[2]))
    step = float(np.abs(np.diff(signatures, axis=0)).mean()) if count > 1 else 0.0
    return {
        "start": start,
        "end": start + length,
        "length": length,
        "seam": round(score, 5),
        "mean_step": round(step, 5),
    }
