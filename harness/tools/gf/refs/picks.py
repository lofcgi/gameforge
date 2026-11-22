"""고른 레퍼런스 관리. 보관함의 메타가 원본이고 picked/ 에는 그 사본을 둔다."""

import json
import shutil
from collections import Counter
from pathlib import Path

from gf.core.state import now
from gf.refs import store

INDEX = "picks.json"
DOMINANCE_MIN_PICKS = 3
DOMINANCE_SHARE = 0.6


def picked_files(project: Path) -> set[str]:
    return {meta["file"] for meta in store.items(store.picked(project))}


def _copy(project: Path, meta: dict) -> None:
    target = store.picked(project)
    target.mkdir(parents=True, exist_ok=True)
    previous = store.meta_path(target / meta["file"])
    picked_at = json.loads(previous.read_text())["picked_at"] if previous.is_file() else now()
    shutil.copyfile(store.inbox(project) / meta["file"], target / meta["file"])
    store.write_meta(target, {**meta, "picked_at": picked_at})


def remove(project: Path, file: str) -> None:
    image = store.picked(project) / file
    store.meta_path(image).unlink()
    image.unlink()


def set_item(project: Path, file: str, *, picked=None, kind=None, note=None, tags=None) -> dict:
    """보관함 항목의 메타를 바꾸고, 고른 상태면 picked/ 사본도 맞춘다."""
    meta = store.update(store.inbox(project), file, note=note, tags=tags, kind=kind)
    is_picked = file in picked_files(project)
    if picked is False and is_picked:
        remove(project, file)
    elif picked or (picked is None and is_picked):
        _copy(project, meta)
    return {**meta, "picked": file in picked_files(project)}


def dominance(metas: list[dict]) -> dict | None:
    """레퍼런스가 한 작품이나 한 사이트에 쏠렸는지 본다. 안티는 세지 않는다."""
    references = [meta for meta in metas if meta["kind"] == "reference"]
    if len(references) < DOMINANCE_MIN_PICKS:
        return None
    keys = Counter(key for key in map(store.source_key, references) if key)
    if not keys:
        return None
    (by, name), count = keys.most_common(1)[0]
    share = count / len(references)
    if share < DOMINANCE_SHARE:
        return None
    where = "한 작품" if by == "title" else "한 사이트"
    return {
        "by": by,
        "name": name,
        "count": count,
        "total": len(references),
        "share": round(share, 2),
        "message": (
            f"고른 레퍼런스 {len(references)}장 중 {count}장이 {where}({name})에서 왔다. "
            "레퍼런스는 방향만 잡는 용도다. 특정 작품을 그대로 따라가지 않도록 다른 출처를 섞는다."
        ),
    }


def write_index(project: Path) -> dict:
    target = store.picked(project)
    target.mkdir(parents=True, exist_ok=True)
    metas = store.items(target)
    warning = dominance(metas)
    index = {
        "updated": now(),
        "reference": sum(meta["kind"] == "reference" for meta in metas),
        "anti": sum(meta["kind"] == "anti" for meta in metas),
        "warnings": [warning] if warning else [],
        "picks": [
            {
                key: meta.get(key)
                for key in ("file", "kind", "note", "tags", "title", "source_url", "origin")
            }
            for meta in metas
        ],
    }
    (target / INDEX).write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    return index
