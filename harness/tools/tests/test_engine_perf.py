import pytest

from gf.core.output import GfError
from gf.engine import perf


def test_frame_stats_summarises_fps():
    stats = perf.frame_stats([10.0] * 95 + [20.0] * 4 + [50.0])
    assert stats["frames"] == 100
    assert stats["avg_fps"] == round(1000 / 10.8, 1)
    assert stats["p95_frame_ms"] == 10.0
    assert stats["max_frame_ms"] == 50.0
    assert stats["min_fps"] == 20.0


def test_p95_reflects_slow_tail():
    stats = perf.frame_stats([16.0] * 90 + [33.0] * 10)
    assert stats["p95_frame_ms"] == 33.0
    assert stats["p95_fps"] == 30.3


def test_no_frames_is_an_error():
    with pytest.raises(GfError):
        perf.frame_stats([])
