"""효과음의 최대 음량을 -3 dB 로 맞춘다(생성물의 최대 음량이 -1.4 ~ -20 dB 로 제각각이었다). audio_post.sh 뒤에 돌린다."""
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MUSIC = {"title", "town", "sea_shallow", "sea_open", "sea_deep", "fight", "legend_fight", "cutscene_intro", "cutscene_ending"}
TARGET = 10 ** (-3 / 20)
for f in sorted((ROOT / "assets/game/audio").glob("*.wav")):
    if f.stem in MUSIC:
        continue
    with wave.open(str(f)) as w:
        params = w.getparams()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    peak = np.abs(data).max() / 32768
    out = np.clip(data * (TARGET / peak), -32768, 32767).astype(np.int16)
    with wave.open(str(f), "wb") as w:
        w.setparams(params)
        w.writeframes(out.tobytes())
    print(f.stem, f"{20 * np.log10(peak):.1f} -> -3.0 dB")
