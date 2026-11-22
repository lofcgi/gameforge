import numpy as np
import pytest

from gf.core.output import GfError
from gf.post import audio_loop

RATE = 22050


def tone(seconds: float, hz: float = 220.0, level: float = 0.3) -> np.ndarray:
    t = np.arange(round(seconds * RATE)) / RATE
    wave = level * np.sin(2 * np.pi * hz * t)
    return np.stack([wave, wave], axis=1).astype(np.float32)


def test_whole_periods_loop_seamlessly():
    report = audio_loop.seam_report(tone(2.0, hz=220.0), RATE)
    assert report["seamless"] and report["problems"] == []
    assert report["edge_silence_ms"] == 0.0


def test_edge_silence_is_reported():
    silence = np.zeros((round(0.02 * RATE), 2), dtype=np.float32)
    report = audio_loop.seam_report(np.concatenate([silence, tone(2.0), silence]), RATE)
    assert not report["seamless"]
    assert report["edge_silence_ms"] == pytest.approx(40.0, abs=1.0)
    assert any("무음" in problem for problem in report["problems"])


def test_waveform_jump_at_the_seam_is_a_click():
    cut = tone(2.0)[: round(1.9989 * RATE)]  # 주기 중간에서 끊겨 끝과 처음이 이어지지 않는다
    report = audio_loop.seam_report(cut, RATE)
    assert report["click_ratio"] > audio_loop.MAX_CLICK_RATIO
    assert any("튄다" in problem for problem in report["problems"])


def test_fade_out_tail_is_reported():
    samples = tone(4.0)
    samples[-RATE:] *= np.linspace(1.0, 0.0, RATE)[:, None] ** 2
    report = audio_loop.seam_report(samples, RATE)
    assert report["tail_level_db"] < audio_loop.MIN_EDGE_LEVEL_DB
    assert any("끝 0.5초" in problem for problem in report["problems"])


def test_timbre_change_across_the_seam_is_reported():
    rng = np.random.default_rng(0)
    noise = (0.2 * rng.standard_normal((2 * RATE, 2))).astype(np.float32)
    report = audio_loop.seam_report(np.concatenate([tone(2.0, hz=110.0), noise]), RATE)
    assert report["spectral_ratio"] > audio_loop.MAX_SPECTRAL_RATIO


def test_too_short_for_a_loop():
    with pytest.raises(GfError):
        audio_loop.seam_report(tone(0.5), RATE)


def test_crossfade_makes_the_wrap_continuous():
    rng = np.random.default_rng(1)
    samples = np.cumsum(rng.standard_normal((3 * RATE, 2)), axis=0).astype(np.float32)
    samples /= np.abs(samples).max() * 2
    size = round(0.5 * RATE)
    looped = audio_loop.crossfade_loop(samples, RATE, 0.5)
    assert len(looped) == len(samples) - size
    assert np.array_equal(looped[0], samples[size])
    # 섞인 구간의 끝은 원본에서 결과의 첫 표본 바로 앞에 있던 표본에 닿는다.
    assert np.abs(looped[-1] - samples[size - 1]).max() < 0.01
    assert audio_loop.seam_report(looped, RATE)["click_ratio"] <= audio_loop.MAX_CLICK_RATIO


def test_crossfade_keeps_level_for_identical_and_unrelated_material():
    same = audio_loop.crossfade_loop(tone(3.0), RATE, 0.5)
    assert np.abs(same[-round(0.25 * RATE)]).max() <= 0.31
    with pytest.raises(GfError):
        audio_loop.crossfade_loop(tone(1.0), RATE, 0.6)


def test_make_loop_fixes_silence_and_fade():
    samples = tone(4.0, hz=200.0)
    samples[-RATE:] *= np.linspace(1.0, 0.0, RATE)[:, None] ** 2
    silence = np.zeros((round(0.03 * RATE), 2), dtype=np.float32)
    broken = np.concatenate([silence, samples, silence])
    assert not audio_loop.seam_report(broken, RATE)["seamless"]
    looped, done = audio_loop.make_loop(broken, RATE, 1.5)
    assert done["trimmed_lead_ms"] == pytest.approx(30.0, abs=1.0)
    assert done["duration_s"] < done["source_duration_s"]
    after = audio_loop.seam_report(looped, RATE)
    assert after["edge_silence_ms"] == 0.0 and after["tail_level_db"] > audio_loop.MIN_EDGE_LEVEL_DB


def test_choose_fade_prefers_a_beat_aligned_overlap():
    # 0.5초마다 박이 있는 4.3초짜리. 겹침이 0.3초(+0.5초의 배수)여야 반복 길이가 박의 배수가 된다.
    samples = np.zeros((round(4.3 * RATE), 2), dtype=np.float32)
    burst = tone(0.05, hz=880.0)
    for beat in np.arange(0.0, 4.2, 0.5):
        start = round(beat * RATE)
        samples[start: start + len(burst)] += burst[: len(samples) - start]
    fade, match = audio_loop.choose_fade(samples, RATE)
    assert match > 0.7
    assert min(abs(fade - value) for value in (0.3, 0.8)) <= 0.05


def test_file_report_finds_clipping_offset_and_silence():
    samples = tone(1.0, level=0.5)
    samples[100:110] = 1.0
    samples += 0.05
    report = audio_loop.file_report(np.concatenate([np.zeros((RATE // 10, 2), dtype=np.float32) + 0.0, samples]), RATE)
    assert report["clipped_runs"] == 1
    assert report["dc_offset"] > audio_loop.MAX_DC_OFFSET
    assert report["lead_silence_ms"] == pytest.approx(100.0, abs=1.0)
    clean = audio_loop.file_report(tone(1.0), RATE)
    assert clean["clipped_runs"] == 0 and clean["dc_offset"] < 0.001 and clean["rms_db"] == pytest.approx(-13.5, abs=0.2)


def test_wav_round_trip_keeps_the_loop(tmp_path):
    looped, _ = audio_loop.make_loop(tone(3.0, hz=200.0), RATE, 0.5)
    target = tmp_path / "loop.wav"
    audio_loop.encode(looped, RATE, target)
    written, rate = audio_loop.decode(target)
    assert rate == RATE and len(written) == len(looped)
    assert audio_loop.seam_report(written, rate)["seamless"]
    with pytest.raises(GfError):
        audio_loop.encode(looped, RATE, tmp_path / "loop.xyz")
