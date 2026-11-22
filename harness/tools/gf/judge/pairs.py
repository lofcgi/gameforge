"""블라인드 심사용 쌍. 심사자가 보는 폴더와 정답 대응표를 서로 다른 곳에 둔다."""

import json
import re
import secrets
import shutil
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from gf.core.output import GfError
from gf.core.paths import gf_dir, rel
from gf.core.state import now

RUBRIC = Path(__file__).with_name("rubric.md")
LABELS = ("X", "Y")
MODES = {
    "change": "a=수정 전, b=수정 후. b가 이기거나 비길 때만 변경을 남긴다.",
    "target": "a=목표 그림, b=게임 화면. b가 목표를 이기면 그 방향은 끝난 것이다.",
}
DEFAULT_STOP = 2
RULES = [
    "변경은 심사에서 이기거나 비겼을 때만 남긴다. 지면 되돌린다.",
    "목표 그림에 없다는 이유만으로 게임 화면의 요소를 지우지 않는다.",
    "멈춤 조건을 만족하면 더 다듬지 않고 다음 작업으로 넘어간다.",
]


def pair_dir(project: Path, pair_id: str) -> Path:
    return project / "captures" / "judge" / pair_id


def secret_dir(project: Path) -> Path:
    return gf_dir(project) / "judge"


def secret_path(project: Path, pair_id: str) -> Path:
    return secret_dir(project) / f"{pair_id}.json"


def history_path(project: Path) -> Path:
    return secret_dir(project) / "history.jsonl"


def check_id(pair_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", pair_id) or pair_id == "history":
        raise GfError(f"id 는 영문·숫자·._- 만 쓴다: {pair_id}")
    return pair_id


def _open(path: Path) -> Image.Image:
    try:
        with Image.open(path) as image:
            return image.convert("RGB")
    except FileNotFoundError as exc:
        raise GfError(f"이미지가 없다: {path}") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise GfError(f"이미지로 읽을 수 없다: {path}") from exc


def normalise(images: list[Image.Image]) -> tuple[list[Image.Image], bool]:
    """가장 작은 이미지 크기에 맞춘다. 비율이 다르면 자르지 않고 여백을 넣고, 그 사실을 알린다."""
    box = min(images, key=lambda image: image.width * image.height).size
    ratio = box[0] / box[1]
    mismatch = any(abs(image.width / image.height - ratio) / ratio > 0.01 for image in images)
    return [ImageOps.pad(image, box, color=(0, 0, 0)) for image in images], mismatch


def create(
    project: Path,
    pair_id: str,
    a: Path,
    b: Path,
    *,
    target: Path | None = None,
    mode: str = "change",
    series: str = "default",
    flip: bool | None = None,
) -> dict:
    """flip 을 주지 않으면 X/Y 순서를 무작위로 정한다."""
    check_id(pair_id)
    if mode not in MODES:
        raise GfError(f"알 수 없는 방식 '{mode}'. 가능한 값: {', '.join(MODES)}")
    if mode == "target" and target is not None:
        raise GfError("target 방식에서는 --a 가 목표 그림이다. --target 을 따로 주지 않는다.")
    folder = pair_dir(project, pair_id)
    if folder.exists() or secret_path(project, pair_id).exists():
        raise GfError(f"심사 쌍 '{pair_id}' 가 이미 있다. 다른 id 를 쓴다.")
    sources = [a, b] + ([target] if target else [])
    images, mismatch = normalise([_open(path) for path in sources])
    flip = bool(secrets.randbelow(2)) if flip is None else flip
    order = ("b", "a") if flip else ("a", "b")
    by_side = {"a": images[0], "b": images[1]}
    folder.mkdir(parents=True)
    files = []
    # 다시 인코딩해서 원본 파일 이름과 메타데이터가 심사자에게 넘어가지 않게 한다.
    for label, side in zip(LABELS, order):
        by_side[side].save(folder / f"{label}.png")
        files.append(folder / f"{label}.png")
    if target:
        images[2].save(folder / "target.png")
        files.append(folder / "target.png")
    shutil.copyfile(RUBRIC, folder / "rubric.md")
    files.append(folder / "rubric.md")
    secret_dir(project).mkdir(parents=True, exist_ok=True)
    secret = {
        "id": pair_id,
        "created": now(),
        "mode": mode,
        "series": series,
        "mapping": dict(zip(LABELS, order)),
        "a": str(a),
        "b": str(b),
        "target": str(target) if target else None,
        "recorded": False,
    }
    secret_path(project, pair_id).write_text(
        json.dumps(secret, ensure_ascii=False, indent=2) + "\n"
    )
    return {
        "folder": rel(project, folder),
        "files": [rel(project, path) for path in files],
        "size": list(images[0].size),
        "aspect_mismatch": mismatch,
    }


def load_history(project: Path) -> list[dict]:
    path = history_path(project)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def stop_rule(rounds: list[dict], stop_after: int) -> dict:
    """target: b가 stop_after 번 이기면 끝. change: 최근 stop_after 판 연속으로 b가 못 이기면 끝."""
    mode = rounds[-1]["mode"]
    if mode == "target":
        wins = sum(entry["winner"] == "b" for entry in rounds)
        met = wins >= stop_after
        reason = f"게임 화면이 목표를 {wins}번 이겼다 (기준 {stop_after}번)."
    else:
        recent = rounds[-stop_after:]
        met = len(recent) == stop_after and all(entry["winner"] != "b" for entry in recent)
        streak = 0
        for entry in reversed(rounds):
            if entry["winner"] == "b":
                break
            streak += 1
        reason = f"최근 {streak}판 연속으로 수정 후가 이기지 못했다 (기준 {stop_after}판)."
    return {"met": met, "reason": reason, "stop_after": stop_after}


def summarise(rounds: list[dict], stop_after: int = DEFAULT_STOP) -> dict:
    return {
        "rounds": len(rounds),
        "wins": sum(entry["winner"] == "b" for entry in rounds),
        "ties": sum(entry["winner"] == "tie" for entry in rounds),
        "losses": sum(entry["winner"] == "a" for entry in rounds),
        "mode": rounds[-1]["mode"],
        "stop": stop_rule(rounds, stop_after),
    }


def _resolve_scores(scores: dict | None, mapping: dict) -> dict | None:
    if scores is None:
        return None
    if not isinstance(scores, dict) or set(scores) - set(LABELS):
        raise GfError('--scores 는 {"X": {...}, "Y": {...}} 형태여야 한다')
    return {mapping[label]: value for label, value in scores.items()}


def record(
    project: Path,
    pair_id: str,
    winner: str,
    *,
    scores: dict | None = None,
    notes: str = "",
    series: str | None = None,
    stop_after: int = DEFAULT_STOP,
) -> dict:
    path = secret_path(project, check_id(pair_id))
    if not path.is_file():
        raise GfError(f"심사 쌍 '{pair_id}' 가 없다. 먼저 gf judge pair 로 만든다.")
    secret = json.loads(path.read_text())
    if secret["recorded"]:
        raise GfError(f"심사 쌍 '{pair_id}' 의 결과는 이미 기록했다.")
    if winner not in (*LABELS, "tie"):
        raise GfError("winner 는 X, Y, tie 중 하나다")
    if stop_after < 1:
        raise GfError("--stop-after 는 1 이상이어야 한다")
    side = "tie" if winner == "tie" else secret["mapping"][winner]
    entry = {
        "at": now(),
        "id": pair_id,
        "series": series or secret["series"],
        "mode": secret["mode"],
        "winner": side,
        "winner_file": None if side == "tie" else secret[side],
        "a": secret["a"],
        "b": secret["b"],
        "scores": _resolve_scores(scores, secret["mapping"]),
        "notes": notes,
    }
    with history_path(project).open("a") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    path.write_text(json.dumps({**secret, "recorded": True}, ensure_ascii=False, indent=2) + "\n")
    rounds = [item for item in load_history(project) if item["series"] == entry["series"]]
    return {"entry": entry, "summary": summarise(rounds, stop_after)}
