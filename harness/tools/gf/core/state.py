import json
from datetime import UTC, datetime
from pathlib import Path

from gf.core.output import GfError
from gf.core.paths import gf_dir

STAGES = ["plan", "look", "graybox", "assets", "polish", "publish"]
ENGINES = ["godot", "web"]
DIMS = ["2d", "3d"]
STYLES = ["pixel", "2d", "3d-code", "3d-gen"]


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def path(project: Path) -> Path:
    return gf_dir(project) / "state.json"


def load(project: Path) -> dict:
    return json.loads(path(project).read_text())


def save(project: Path, state: dict) -> None:
    path(project).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def new(name: str, engine: str, dim: str, style: str) -> dict:
    return {
        "name": name,
        "engine": engine,
        "dim": dim,
        "style": style,
        "stage": STAGES[0],
        "approvals": [],
        "created": now(),
    }


def approve(project: Path, note: str) -> dict:
    """현재 단계를 승인하고 다음 단계로 넘어간다."""
    state = load(project)
    index = STAGES.index(state["stage"])
    state["approvals"].append({"stage": state["stage"], "at": now(), "note": note})
    if index + 1 < len(STAGES):
        state["stage"] = STAGES[index + 1]
    save(project, state)
    return state


def set_stage(project: Path, stage: str) -> dict:
    if stage not in STAGES:
        raise GfError(f"알 수 없는 단계 '{stage}'. 가능한 값: {', '.join(STAGES)}")
    state = load(project)
    state["stage"] = stage
    save(project, state)
    return state
