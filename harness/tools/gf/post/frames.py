"""ffmpeg 로 영상에서 프레임을 뽑는다. 여러 캐릭터가 격자로 놓인 영상은 칸별로 잘라 낸다."""

import json
import shutil
import subprocess
from pathlib import Path

from gf.core.output import GfError


def _run(command: list[str]) -> str:
    if not shutil.which(command[0]):
        raise GfError(f"{command[0]} 가 PATH 에 없다. `brew install ffmpeg` 로 설치한다.")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise GfError(f"{command[0]} 실패: {result.stderr.strip()[-600:]}")
    return result.stdout


def probe(video: Path) -> dict:
    output = _run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(video)]
    )
    data = json.loads(output)
    if not data.get("streams"):
        raise GfError(f"영상 스트림이 없다: {video}")
    stream = data["streams"][0]
    numerator, denominator = stream["r_frame_rate"].split("/")
    return {
        "width": stream["width"],
        "height": stream["height"],
        "fps": round(int(numerator) / int(denominator), 3),
        "duration": float(data["format"]["duration"]),
    }


def slot_rect(width: int, height: int, columns: int, rows: int, slot: int, inset: int) -> tuple[int, int, int, int]:
    """격자의 slot 번째 칸(왼쪽 위부터 가로 순서)의 x, y, w, h."""
    if not 0 <= slot < columns * rows:
        raise GfError(f"칸 번호 {slot} 가 {columns}x{rows} 격자를 벗어난다.")
    cell_w, cell_h = width // columns, height // rows
    row, column = divmod(slot, columns)
    rect = (column * cell_w + inset, row * cell_h + inset, cell_w - 2 * inset, cell_h - 2 * inset)
    if rect[2] <= 0 or rect[3] <= 0:
        raise GfError(f"--inset {inset} 가 칸 크기 {cell_w}x{cell_h} 보다 크다.")
    return rect


def extract(
    video: Path,
    out_dir: Path,
    fps: float,
    count: int | None = None,
    start: float | None = None,
    end: float | None = None,
    crop: tuple[int, int, int, int] | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("frame_*.png"):
        stale.unlink()
    filters = [f"fps={fps:.6f}"]
    if crop:
        x, y, w, h = crop
        filters.append(f"crop={w}:{h}:{x}:{y}")
    command = ["ffmpeg", "-v", "error", "-y"]
    if start is not None:
        command += ["-ss", str(start)]
    if end is not None:
        command += ["-to", str(end)]
    command += ["-i", str(video), "-vf", ",".join(filters)]
    if count is not None:
        command += ["-frames:v", str(count)]
    _run([*command, str(out_dir / "frame_%04d.png")])
    return sorted(out_dir.glob("frame_*.png"))
