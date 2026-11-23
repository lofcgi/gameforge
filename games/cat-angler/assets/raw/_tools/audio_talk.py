"""talk(대사 글자가 찍히는 소리)를 계산으로 만든다 → assets/game/audio/talk.wav (최대 -3 dB).

1초에 열 번쯤 나는 소리라 생성물 대신 길이와 음색을 정확히 정한다: 45ms, 부드럽게 시작해(3ms) 빨리 잦아드는
낮은 사인파(660Hz + 옅은 배음)에 나무를 두드린 듯한 짧은 잡음을 조금 섞는다. 난수는 시드를 고정했다.
"""
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RATE = 44100
t = np.arange(int(RATE * 0.045)) / RATE
attack = np.minimum(1.0, t / 0.003)
tone = np.sin(2 * np.pi * 660 * t) + 0.25 * np.sin(2 * np.pi * 1320 * t) * np.exp(-t / 0.006)
noise = np.random.default_rng(7).standard_normal(len(t))
noise = np.convolve(noise, np.ones(12) / 12, mode="same") * np.exp(-t / 0.002) * 0.5
wave_ = (tone * np.exp(-t / 0.011) + noise) * attack
wave_ *= np.minimum(1.0, (t[-1] - t) / 0.008)
wave_ *= 10 ** (-3 / 20) / np.abs(wave_).max()
out = ROOT / "assets/game/audio/talk.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(np.round(wave_ * 32767).astype(np.int16).tobytes())
print(out)
