"""효과음의 크기를 맞춘다. audio_post.sh 뒤에 돌린다(여러 번 돌려도 결과가 같다: 늘 방금 변환한 파일에서 시작한다).

최대 음량만 -3 dB 로 맞췄더니 순간 피크가 큰 소리(bite, pick)는 몸통이 10 dB 넘게 작았다. 그래서 가장 큰 0.1초의
평균 음량(귀가 짧은 소리의 크기를 느끼는 구간)을 LOUD dB 로 맞추고, 넘치는 피크는 리미터로 -3 dB 아래에 눌러 둔다
(누르는 양은 MAX_SHAVE_DB 까지만. 그래서 망치질·종이처럼 피크뿐인 소리는 LOUD 에 조금 못 미친다).
소리마다의 역할(알림은 크게, 발소리·글자 소리는 작게)은 파일이 아니라 scripts/audio.gd 의 표가 정한다.
"""
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MUSIC = {"title", "town", "sea_shallow", "sea_open", "sea_deep", "fight", "legend_fight", "cutscene_intro", "cutscene_ending"}
SYNTHESISED = {"talk"}
"""계산으로 만든 소리는 만든 스크립트가 크기까지 정한다."""
LOUD = -16.0
CEILING = 10 ** (-3 / 20)
MAX_SHAVE_DB = 6.0
WINDOW_S = 0.1
ONSET_DB = -30.0
RELEASE_S = 0.05


def trim(data: np.ndarray, rate: int) -> np.ndarray:
    """최대 크기보다 ONSET_DB 넘게 작은 앞부분(누른 뒤 늦게 들리게 하는 옅은 전주)을 잘라 내고 2ms 로 열어 준다."""
    loud = np.nonzero(np.abs(data) > np.abs(data).max() * 10 ** (ONSET_DB / 20))[0]
    out = data[max(0, loud[0] - int(rate * 0.003)):].copy()
    fade = int(rate * 0.002)
    out[:fade] *= np.linspace(0.0, 1.0, fade)
    return out


def loudest(data: np.ndarray, rate: int) -> float:
    """가장 큰 WINDOW_S 구간의 평균 음량(dB). 그보다 짧은 소리는 뒤를 무음으로 채운 것으로 본다."""
    size = int(rate * WINDOW_S)
    padded = np.concatenate([data, np.zeros(max(0, size - len(data)))])
    power = np.convolve(padded ** 2, np.ones(size) / size, mode="valid")
    return 10 * np.log10(power.max() + 1e-12)


def limit(data: np.ndarray, rate: int) -> np.ndarray:
    """앞을 내다보는 리미터: 앞뒤 1ms 안의 최대 크기가 천장을 넘는 만큼 줄이고, 줄인 양은 RELEASE_S 에 걸쳐 천천히 푼다.
    빨리 풀면 낮은 소리의 한 주기 안에서 음량이 출렁여 찌그러진다."""
    reach = max(1, int(rate * 0.001))
    padded = np.pad(np.abs(data), reach, mode="edge")
    envelope = np.lib.stride_tricks.sliding_window_view(padded, 2 * reach + 1).max(axis=1)
    reduce = np.minimum(1.0, CEILING / np.maximum(envelope, 1e-9))
    keep = np.exp(-1.0 / (rate * RELEASE_S))
    level = 1.0
    for i, wanted in enumerate(reduce):
        level = min(wanted, 1.0 - (1.0 - level) * keep)
        reduce[i] = level
    return data * reduce


def main() -> None:
    for f in sorted((ROOT / "assets/game/audio").glob("*.wav")):
        if f.stem in MUSIC or f.stem in SYNTHESISED:
            continue
        with wave.open(str(f)) as w:
            params = w.getparams()
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        rate = params.framerate
        cut = trim(data, rate)
        before = loudest(cut, rate)
        gain = LOUD - before
        for _ in range(8):
            out = limit(cut * 10 ** (gain / 20), rate)
            shaved = 20 * np.log10(np.abs(cut).max()) + gain - 20 * np.log10(np.abs(out).max())
            gain += min(LOUD - loudest(out, rate), MAX_SHAVE_DB - shaved)
        out = limit(cut * 10 ** (gain / 20), rate)
        with wave.open(str(f), "wb") as w:
            w.setparams(params)
            w.writeframes(np.round(out * 32767).astype(np.int16).tobytes())
        peak = 20 * np.log10(np.abs(out).max())
        shaved = 20 * np.log10(np.abs(cut).max()) + gain - peak
        print(f"{f.stem:14s} 앞 {(len(data) - len(cut)) / rate * 1000:4.0f}ms 자름, 0.1초 음량 {before:6.1f} -> {loudest(out, rate):6.1f} dB, "
              f"최대 {peak:5.1f} dB, 리미터가 누른 양 {shaved:4.1f} dB")

if __name__ == "__main__":
    main()
