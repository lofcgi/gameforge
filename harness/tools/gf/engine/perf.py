"""프레임 시간 표본을 요약한다."""

import math

from gf.core.output import GfError


def percentile(sorted_values: list[float], fraction: float) -> float:
    index = max(0, math.ceil(fraction * len(sorted_values)) - 1)
    return sorted_values[index]


def frame_stats(frame_ms: list[float]) -> dict:
    """p95_fps 는 느린 쪽 5% 경계 프레임의 FPS, min_fps 는 가장 느린 프레임의 FPS 다."""
    if not frame_ms:
        raise GfError("프레임 시간 표본이 없다. 게임이 프레임을 그리지 않았다.")
    ordered = sorted(frame_ms)
    avg = sum(ordered) / len(ordered)
    p95 = percentile(ordered, 0.95)
    return {
        "frames": len(ordered),
        "avg_fps": round(1000.0 / avg, 1),
        "p95_fps": round(1000.0 / p95, 1),
        "min_fps": round(1000.0 / ordered[-1], 1),
        "avg_frame_ms": round(avg, 3),
        "p95_frame_ms": round(p95, 3),
        "max_frame_ms": round(ordered[-1], 3),
    }
