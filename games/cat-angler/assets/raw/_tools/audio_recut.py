"""박자가 또렷한 곡의 반복 길이를 박의 정수배로 다시 자른다: audio_recut.py <원본> <결과.wav>

`gf post audio-loop` 는 이음매가 튀지 않게만 다듬어서, 반복 길이가 박의 배수가 아니면 한 바퀴 돌 때마다 박자가 밀린다
(cutscene_intro 35.66박, cutscene_ending 80.38박 → 이음매에서 박의 1/3 넘게 밀렸다). 여기서는 곡 전체에서 박 길이를 재고
(시작 세기의 자기상관 → 격자가 가장 선명한 값), 꼬리를 잘라 반복 길이를 박의 정수배로 맞춘 뒤 같은 방법으로 섞는다.
격자 선명도가 MIN_CLARITY 보다 낮은 곡(박이 또렷하지 않은 곡)은 박 길이를 믿을 수 없어 거부한다.
"""
import sys
from pathlib import Path

import numpy as np

from gf.post import audio_loop

FADE_S = 0.5
MIN_CLARITY = 0.15
HOP = 441


def onsets(mono: np.ndarray, rate: int) -> tuple[np.ndarray, float]:
    """10ms 마다 소리가 새로 시작되는 세기."""
    size = 1024
    frames = np.array([np.abs(np.fft.rfft(mono[i:i + size] * np.hanning(size))) for i in range(0, len(mono) - size, HOP)])
    flux = np.maximum(0, np.diff(np.log1p(100 * frames), axis=0)).sum(axis=1)
    return np.maximum(flux - np.median(flux), 0), rate / HOP


def grid(onset: np.ndarray, per_s: float, period: float, start: int = 0, stop: int | None = None) -> tuple[float, float]:
    """박 길이 period 의 격자에 시작들이 얼마나 모이는지(0~1)와 격자의 위상(초)."""
    stop = len(onset) if stop is None else stop
    turn = (onset[start:stop] * np.exp(-2j * np.pi * np.arange(start, stop) / per_s / period)).sum()
    return float(abs(turn) / (onset[start:stop].sum() + 1e-9)), float(np.angle(turn) / (2 * np.pi) * period)


def beat(mono: np.ndarray, rate: int) -> tuple[float, float]:
    """(박 길이 초, 격자 선명도). 0.25~1초 사이에서 찾는다."""
    onset, per_s = onsets(mono, rate)
    again = np.correlate(onset, onset, "full")[len(onset) - 1:]
    low, high = int(per_s * 0.25), int(per_s * 1.0)
    rough = (low + int(np.argmax(again[low:high]))) / per_s
    period = max(np.linspace(rough * 0.97, rough * 1.03, 601), key=lambda p: grid(onset, per_s, p)[0])
    return float(period), grid(onset, per_s, period)[0]


def seam_shift(mono: np.ndarray, rate: int, period: float, span_s: float = 6.0) -> float:
    """끝에서 처음으로 넘어갈 때 박자 격자가 밀리는 양(초). 0 이면 박자가 그대로 이어진다."""
    reach = int((span_s + 0.5) * rate)
    onset, per_s = onsets(np.concatenate([mono[-reach:], mono[:reach]]), rate)
    middle, span = len(onset) // 2, int(span_s * per_s)
    before, after = grid(onset, per_s, period, middle - span, middle)[1], grid(onset, per_s, period, middle, middle + span)[1]
    return (after - before + period / 2) % period - period / 2


def main(source: Path, out: Path) -> None:
    samples, rate = audio_loop.decode(source)
    trimmed = audio_loop.trim_silence(samples)
    period, clarity = beat(trimmed.mean(axis=1), rate)
    if clarity < MIN_CLARITY:
        raise SystemExit(f"{source.name}: 박이 또렷하지 않다(격자 선명도 {clarity:.2f}). gf post audio-loop 를 쓴다")
    beats = int((len(trimmed) / rate - FADE_S) / period)
    looped = audio_loop.crossfade_loop(trimmed[: round((beats * period + FADE_S) * rate)], rate, FADE_S)
    audio_loop.encode(looped, rate, out)
    written, _ = audio_loop.decode(out)
    seam = audio_loop.seam_report(written, rate)
    shift = seam_shift(written.mean(axis=1), rate, period)
    print(f"{out.name}: 박 {period * 1000:.1f}ms(선명도 {clarity:.2f}) × {beats}박 = {len(written) / rate:.2f}초, "
          f"이음매에서 박자 밀림 {shift * 1000:+.0f}ms, 이음매 검사 {'통과' if seam['seamless'] else seam['problems']}")
    if not seam["seamless"] or abs(shift) > 0.1 * period:
        raise SystemExit(1)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
