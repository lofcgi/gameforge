"""오디오 파일의 숫자 검사와 반복(loop) 이음매 다듬기.

에이전트는 듣지 못한다. 여기의 숫자는 "끝에서 처음으로 넘어갈 때 튀는 것이 있는가"를 재는 것이고,
곡이 듣기 좋은지, 박자가 맞게 이어지는지는 사람이 들어야 안다.

표본은 float32 배열 [표본 수, 채널 수], 값 범위 -1..1.
"""

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

from gf.core.output import GfError

SILENCE_LEVEL = 0.001
"""-60 dBFS. 앞뒤 무음과 무음 잘라내기의 기준."""
FLOOR_DB = -200.0
EDGE_WINDOW_S = 0.05
LEVEL_WINDOW_S = 0.5
BANDS = 24
FRAME = 2048

# 이음매 판정 기준. 넘으면 그 항목이 problems 에 들어가고 seamless 가 false 가 된다.
MAX_EDGE_SILENCE_MS = 10.0
"""앞뒤 무음의 합. 반복할 때마다 그만큼 소리가 끊긴다."""
MAX_CLICK_RATIO = 4.0
"""이음매에서 파형이 꺾이는 정도 ÷ 이음매 앞뒤 50ms 안에서 흔히 꺾이는 정도(99번째 백분위)."""
MIN_CLICK_DB = -40.0
"""꺾임이 이보다 작으면 비율이 커도 들리지 않는 것으로 본다."""
MIN_EDGE_LEVEL_DB = -12.0
"""처음·끝 0.5초의 음량 − 곡 전체에서 흔한 음량. 이보다 낮으면 페이드인·페이드아웃이 반복마다 들린다."""
MAX_SPECTRAL_RATIO = 1.5
"""이음매 앞뒤의 음색 차이 ÷ 곡 안에서 이웃한 순간끼리의 음색 차이(95번째 백분위)."""

CLIP_LEVEL = 0.999
CLIP_RUN = 3
MAX_DC_OFFSET = 0.01
ENCODERS = {
    ".wav": ["-c:a", "pcm_s16le"],
    ".mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
    ".ogg": ["-c:a", "libvorbis", "-q:a", "5"],
    ".opus": ["-c:a", "libopus", "-b:a", "128k"],
}


def _tool(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        raise GfError(f"{name} 를 찾지 못했다. ffmpeg 를 설치한다.")
    return binary


def decode(path: Path) -> tuple[np.ndarray, int]:
    """ffmpeg 로 풀어 (표본, 표본율)을 돌려준다."""
    probe = subprocess.run(
        [_tool("ffprobe"), "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels",
         "-of", "json", str(path)], capture_output=True, text=True, timeout=60, check=False,
    )
    streams = json.loads(probe.stdout or "{}").get("streams") or []
    if probe.returncode != 0 or not streams:
        raise GfError(f"오디오로 읽지 못했다: {path}\n{probe.stderr.strip()[-500:]}")
    rate, channels = int(streams[0]["sample_rate"]), int(streams[0]["channels"])
    raw = subprocess.run(
        [_tool("ffmpeg"), "-v", "error", "-i", str(path), "-map", "a:0", "-f", "f32le", "-acodec", "pcm_f32le", "-"],
        capture_output=True, timeout=300, check=False,
    )
    if raw.returncode != 0:
        raise GfError(f"오디오를 풀지 못했다: {path}\n{raw.stderr.decode(errors='replace')[-500:]}")
    return np.frombuffer(raw.stdout, dtype=np.float32).reshape(-1, channels).copy(), rate


def encode(samples: np.ndarray, rate: int, path: Path) -> None:
    """확장자에 맞는 코덱으로 쓴다."""
    codec = ENCODERS.get(path.suffix.lower())
    if codec is None:
        raise GfError(f"쓸 수 있는 형식은 {', '.join(ENCODERS)} 이다: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [_tool("ffmpeg"), "-v", "error", "-y", "-f", "f32le", "-ar", str(rate), "-ac", str(samples.shape[1]),
         "-i", "-", *codec, str(path)],
        input=np.clip(samples, -1.0, 1.0).astype(np.float32).tobytes(), capture_output=True, timeout=300, check=False,
    )
    if result.returncode != 0:
        raise GfError(f"오디오를 쓰지 못했다: {path}\n{result.stderr.decode(errors='replace')[-500:]}")


def _db(level: float) -> float:
    return round(max(20 * float(np.log10(level)), FLOOR_DB), 1) if level > 0 else FLOOR_DB


def _rms(samples: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float64)))) if samples.size else 0.0


def edge_silence(samples: np.ndarray) -> tuple[int, int]:
    """앞과 뒤에서 SILENCE_LEVEL 보다 작은 표본이 이어지는 길이."""
    loud = np.flatnonzero(np.abs(samples).max(axis=1) >= SILENCE_LEVEL)
    if not loud.size:
        return len(samples), 0
    return int(loud[0]), int(len(samples) - 1 - loud[-1])


def file_report(samples: np.ndarray, rate: int) -> dict:
    """어느 오디오 파일에나 재는 것: 잘림(클리핑), 직류 치우침, 앞뒤 무음, 평균 음량."""
    lead, tail = edge_silence(samples)
    clipped = np.abs(samples).max(axis=1) >= CLIP_LEVEL
    runs = np.diff(np.flatnonzero(np.diff(np.concatenate(([False], clipped, [False])).astype(np.int8))))[::2]
    return {
        "rms_db": _db(_rms(samples)),
        "clipped_runs": int((runs >= CLIP_RUN).sum()),
        "dc_offset": round(float(np.abs(samples.mean(axis=0)).max()), 4) if samples.size else 0.0,
        "lead_silence_ms": round(1000 * lead / rate, 1),
        "tail_silence_ms": round(1000 * tail / rate, 1),
    }


def _band_levels(mono: np.ndarray, rate: int) -> np.ndarray:
    """겹치지 않는 FRAME 길이 구간마다 로그 간격 대역의 음량(dB). [구간 수, BANDS]."""
    count = len(mono) // FRAME
    frames = mono[: count * FRAME].reshape(count, FRAME) * np.hanning(FRAME)
    power = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    edges = np.geomspace(50.0, min(16000.0, rate / 2), BANDS + 1)
    bins = np.fft.rfftfreq(FRAME, 1 / rate)
    index = np.clip(np.searchsorted(edges, bins) - 1, -1, BANDS)
    levels = np.stack([power[:, index == band].sum(axis=1) for band in range(BANDS)], axis=1)
    return 10 * np.log10(np.maximum(levels / FRAME, 1e-10))


def _spectral_jump(mono: np.ndarray, rate: int) -> tuple[float, float]:
    """(이음매 앞뒤 구간의 대역 음량 차이, 곡 안 이웃 구간끼리의 차이 95번째 백분위). 단위 dB."""
    levels = _band_levels(mono, rate)
    if len(levels) < 4:
        return 0.0, 0.0
    inside = np.abs(np.diff(levels, axis=0)).mean(axis=1)
    last = _band_levels(mono[-FRAME:], rate)[0]
    return float(np.abs(levels[0] - last).mean()), float(np.percentile(inside, 95))


def _click(samples: np.ndarray, rate: int) -> tuple[float, float]:
    """(이음매에서 파형이 꺾인 크기, 그 크기 ÷ 이음매 근처에서 흔한 꺾임)."""
    window = max(4, round(EDGE_WINDOW_S * rate))
    around = np.concatenate([samples[-window:], samples[:window]])
    bends = np.abs(np.diff(around, n=2, axis=0))
    at_seam = float(bends[window - 2: window].max())
    usual = float(np.percentile(np.delete(bends, [window - 2, window - 1], axis=0), 99))
    return at_seam, at_seam / max(usual, 1e-6)


def seam_report(samples: np.ndarray, rate: int) -> dict:
    """끝에서 처음으로 이어 붙였을 때의 이음매를 잰다. 기준은 이 파일 위쪽의 상수다."""
    if len(samples) < rate:
        raise GfError("반복 이음매를 재기에는 너무 짧다 (1초 미만).")
    mono = samples.mean(axis=1)
    lead, tail = edge_silence(samples)
    click, click_ratio = _click(samples, rate)
    span = round(LEVEL_WINDOW_S * rate)
    windows = [_rms(mono[start: start + span]) for start in range(0, len(mono) - span + 1, span)]
    usual = float(np.median(windows))
    seam_jump, inside_jump = _spectral_jump(mono, rate)
    report = {
        "edge_silence_ms": round(1000 * (lead + tail) / rate, 1),
        "click_db": _db(click), "click_ratio": round(click_ratio, 2),
        "head_level_db": round(_db(_rms(mono[:span])) - _db(usual), 1),
        "tail_level_db": round(_db(_rms(mono[-span:])) - _db(usual), 1),
        "spectral_jump_db": round(seam_jump, 2), "spectral_usual_db": round(inside_jump, 2),
        "spectral_ratio": round(seam_jump / inside_jump, 2) if inside_jump > 0 else 0.0,
    }
    problems = []
    if report["edge_silence_ms"] > MAX_EDGE_SILENCE_MS:
        problems.append(f"앞뒤 무음 {report['edge_silence_ms']}ms (기준 {MAX_EDGE_SILENCE_MS}ms 이하): 반복마다 끊긴다")
    if report["click_ratio"] > MAX_CLICK_RATIO and report["click_db"] > MIN_CLICK_DB:
        problems.append(f"이음매에서 파형이 튄다 (주변의 {report['click_ratio']}배, {report['click_db']} dB): 딱 소리")
    for key, label in (("head_level_db", "처음"), ("tail_level_db", "끝")):
        if report[key] < MIN_EDGE_LEVEL_DB:
            problems.append(f"{label} 0.5초가 곡보다 {-report[key]} dB 작다 (기준 {-MIN_EDGE_LEVEL_DB} dB 이내): 반복마다 잦아든다")
    if report["spectral_ratio"] > MAX_SPECTRAL_RATIO:
        problems.append(f"이음매 앞뒤의 음색 차이가 곡 안의 변화보다 {report['spectral_ratio']}배 크다 "
                        f"(기준 {MAX_SPECTRAL_RATIO}배 이하): 넘어가는 순간이 드러난다")
    return {**report, "seamless": not problems, "problems": problems}


def trim_silence(samples: np.ndarray) -> np.ndarray:
    lead, tail = edge_silence(samples)
    return samples[lead: len(samples) - tail]


def _envelope(mono: np.ndarray, rate: int) -> np.ndarray:
    """10ms 마다의 음량이 늘어난 만큼(박자가 실리는 곳이 큰 값)."""
    hop = max(1, rate // 100)
    count = len(mono) // hop
    levels = np.sqrt(np.mean(np.square(mono[: count * hop].reshape(count, hop)), axis=1))
    return np.maximum(np.diff(levels, prepend=levels[:1]), 0.0)


def choose_fade(samples: np.ndarray, rate: int, shortest_s: float = 0.25, longest_s: float = 2.0) -> tuple[float, float]:
    """겹칠 꼬리와 머리의 박자가 가장 잘 맞는 겹침 길이(초)와 그 상관을 고른다.

    겹침 길이 F 로 다듬으면 반복 길이가 (전체 − F) 가 된다. 꼬리 F 초와 머리 F 초의 음량 변화가 닮았다는 것은
    그 반복 길이가 박자의 배수라는 뜻이다.
    """
    envelope = _envelope(samples.mean(axis=1), rate)
    longest = min(round(longest_s * 100), len(envelope) // 4)
    shortest = min(round(shortest_s * 100), longest)
    best = (shortest / 100, -1.0)
    for size in range(shortest, longest + 1):
        head, tail = envelope[:size], envelope[-size:]
        spread = float(head.std() * tail.std())
        score = float(np.mean((head - head.mean()) * (tail - tail.mean())) / spread) if spread > 0 else 0.0
        if score > best[1]:
            best = (size / 100, score)
    return best[0], round(best[1], 3)


def crossfade_loop(samples: np.ndarray, rate: int, fade_s: float) -> np.ndarray:
    """꼬리 fade_s 초를 머리 fade_s 초와 섞어 끝에 붙이고, 그만큼 짧아진 반복을 돌려준다.

    결과는 원본의 fade_s 지점에서 시작해, 섞인 구간이 원본의 fade_s 직전 표본으로 끝난다. 그래서 끝에서 처음으로
    넘어가는 자리가 원본에서 원래 이웃하던 두 표본이다. 섞는 동안 음량이 꺼지거나 부풀지 않게, 두 구간의 닮은 정도에
    맞춰 세기를 보정한다.
    """
    size = round(fade_s * rate)
    if size < 2 or size * 2 >= len(samples):
        raise GfError(f"겹침 길이 {fade_s}초가 곡 길이({len(samples) / rate:.2f}초)에 맞지 않는다.")
    head = samples[:size].astype(np.float64)
    tail = samples[-size:].astype(np.float64)
    spread = float(head.std() * tail.std())
    alike = float(np.clip(np.mean((head - head.mean()) * (tail - tail.mean())) / spread, 0.0, 1.0)) if spread > 0 else 0.0
    rise = np.linspace(0.0, 1.0, size, endpoint=False)[:, None] + 0.5 / size
    fall = 1.0 - rise
    gain = 1.0 / np.sqrt(rise**2 + fall**2 + 2 * alike * rise * fall)
    blend = (tail * fall + head * rise) * gain
    return np.concatenate([samples[size: len(samples) - size], blend.astype(np.float32)])


def make_loop(samples: np.ndarray, rate: int, fade_s: float | None) -> tuple[np.ndarray, dict]:
    """무음을 잘라내고 꼬리를 머리에 섞어 매끄러운 반복을 만든다. (표본, 한 일)을 돌려준다."""
    trimmed = trim_silence(samples)
    if len(trimmed) < rate:
        raise GfError("무음을 빼면 1초도 남지 않는다.")
    lead, tail = edge_silence(samples)
    match = None
    if fade_s is None:
        fade_s, match = choose_fade(trimmed, rate)
    looped = crossfade_loop(trimmed, rate, fade_s)
    return looped, {
        "trimmed_lead_ms": round(1000 * lead / rate, 1), "trimmed_tail_ms": round(1000 * tail / rate, 1),
        "fade_s": fade_s, "beat_match": match,
        "duration_s": round(len(looped) / rate, 3), "source_duration_s": round(len(samples) / rate, 3),
    }
