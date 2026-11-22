"""영상에서 대표 프레임을 뽑는다. 내려받기는 yt-dlp, 추출은 ffmpeg 를 쓴다."""

import json
import shutil
import subprocess
from pathlib import Path

from gf.core.output import GfError

# 느낌을 보는 용도라 480p 면 충분하다. 더 낮은 것밖에 없으면 그중 가장 큰 것을 받는다.
FORMAT_SORT = "res:480"


def _run(command: list[str], what: str, timeout: int) -> str:
    if not shutil.which(command[0]):
        raise GfError(f"{command[0]} 가 PATH 에 없다.")
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise GfError(f"{what} 시간 초과 ({timeout}초)") from exc
    if result.returncode != 0:
        tail = " | ".join(result.stderr.strip().splitlines()[-3:])
        raise GfError(f"{what} 실패: {tail}")
    return result.stdout


def download(url: str, workdir: Path) -> dict:
    """영상만(소리 없이) 내려받고 경로·제목·페이지 주소를 돌려준다."""
    stdout = _run(
        [
            "yt-dlp",
            "--no-playlist",
            "--no-progress",
            "--quiet",
            "-f",
            "bv*/b",
            "-S",
            FORMAT_SORT,
            "-o",
            str(workdir / "video.%(ext)s"),
            "--print",
            "after_move:%(.{title,webpage_url,filepath})j",
            url,
        ],
        "영상 내려받기",
        timeout=600,
    )
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise GfError("yt-dlp 가 내려받은 파일 정보를 내지 않았다.")
    info = json.loads(lines[-1])
    return {"path": Path(info["filepath"]), "title": info["title"], "url": info["webpage_url"]}


def duration(path: Path) -> float:
    stdout = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        "영상 길이 확인",
        timeout=60,
    )
    try:
        seconds = float(stdout.strip())
    except ValueError as exc:
        raise GfError(f"영상 길이를 알 수 없다: {path.name}") from exc
    if seconds <= 0:
        raise GfError(f"영상 길이가 0 이다: {path.name}")
    return seconds


def timestamps(
    seconds: float, *, every: float | None, count: int | None, limit: int
) -> list[float]:
    """구간 한가운데를 고른다. 첫 프레임과 끝 프레임은 로고나 암전인 경우가 많다."""
    if every is not None:
        if every <= 0:
            raise GfError("--every 는 0 보다 커야 한다")
        total = max(1, int(seconds // every))
        step = every
    else:
        if not count or count <= 0:
            raise GfError("--count 는 1 이상이어야 한다")
        total = count
        step = seconds / count
    return [round(step * (index + 0.5), 3) for index in range(min(total, limit))]


def grab(path: Path, at: float, out: Path) -> None:
    _run(
        [
            "ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", str(path),
            "-frames:v", "1", "-q:v", "2", str(out),
        ],
        f"{at}초 프레임 추출",
        timeout=120,
    )  # fmt: skip
    if not out.is_file():
        raise GfError(f"{at}초 위치에서 프레임을 얻지 못했다.")


def scene_frames(path: Path, threshold: float, limit: int, outdir: Path) -> list[Path]:
    """장면이 바뀌는 지점의 프레임만 뽑는다."""
    if not 0 < threshold < 1:
        raise GfError("--scene 값은 0 과 1 사이여야 한다")
    _run(
        [
            "ffmpeg", "-v", "error", "-y", "-i", str(path),
            "-vf", f"select='gt(scene,{threshold})'", "-fps_mode", "vfr",
            "-frames:v", str(limit), "-q:v", "2", str(outdir / "scene-%04d.jpg"),
        ],
        "장면 전환 프레임 추출",
        timeout=900,
    )  # fmt: skip
    frames = sorted(outdir.glob("scene-*.jpg"))
    if not frames:
        raise GfError(f"장면 전환을 찾지 못했다 (기준 {threshold}). --scene 값을 낮춰 본다.")
    return frames
