"""번호가 붙은 모음판. 사용자는 이 번호로 고른다."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from gf.core.output import GfError
from gf.core.paths import rel
from gf.core.state import now
from gf.refs import picks, store

COLS, ROWS = 5, 4
PER_PAGE = COLS * ROWS
CELL = (368, 216)
GAP = 8
BACKGROUND = (24, 24, 28)
EMPTY = (40, 40, 46)
BORDERS = {"reference": (60, 200, 110), "anti": (230, 70, 70)}


def sheets_dir(project: Path) -> Path:
    return store.references(project) / "sheets"


def index_path(project: Path, which: str) -> Path:
    return sheets_dir(project) / f"{which}-index.json"


def _label(entry: dict) -> str:
    if entry["kind"] == "anti":
        return f"{entry['n']} ANTI"
    return f"{entry['n']} PICK" if entry["picked"] else str(entry["n"])


def _draw_cell(page: Image.Image, origin: tuple[int, int], image_path: Path, entry: dict) -> None:
    x, y = origin
    with Image.open(image_path) as image:
        thumb = ImageOps.pad(image.convert("RGB"), CELL, color=EMPTY)
    page.paste(thumb, (x, y))
    draw = ImageDraw.Draw(page)
    marked = entry["picked"] or entry["kind"] == "anti"
    if marked:
        box = (x - 3, y - 3, x + CELL[0] + 2, y + CELL[1] + 2)
        draw.rectangle(box, outline=BORDERS[entry["kind"]], width=4)
    font = ImageFont.load_default(size=30)
    text = _label(entry)
    width = draw.textlength(text, font=font)
    draw.rectangle((x, y, x + width + 16, y + 40), fill=(0, 0, 0))
    colour = BORDERS[entry["kind"]] if marked else (255, 255, 255)
    draw.text((x + 8, y + 3), text, font=font, fill=colour)


def _render_page(directory: Path, entries: list[dict]) -> Image.Image:
    size = (COLS * (CELL[0] + GAP) + GAP, ROWS * (CELL[1] + GAP) + GAP)
    page = Image.new("RGB", size, BACKGROUND)
    for slot, entry in enumerate(entries):
        origin = (
            GAP + (slot % COLS) * (CELL[0] + GAP),
            GAP + (slot // COLS) * (CELL[1] + GAP),
        )
        _draw_cell(page, origin, directory / entry["file"], entry)
    return page


def build(project: Path, which: str) -> dict:
    """모음판 PNG 와 번호→파일 색인을 새로 만든다. 이전 판은 지운다."""
    directory = store.set_dir(project, which)
    metas = store.items(directory)
    if not metas:
        raise GfError(f"references/{which} 가 비어 있다.")
    chosen = picks.picked_files(project)
    entries = [
        {
            "n": number,
            "file": meta["file"],
            "page": (number - 1) // PER_PAGE + 1,
            "kind": meta["kind"],
            "picked": meta["file"] in chosen,
            "title": meta.get("title") or meta.get("page_title"),
            "note": meta.get("note", ""),
        }
        for number, meta in enumerate(metas, start=1)
    ]
    out = sheets_dir(project)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob(f"{which}-[0-9]*.png"):
        stale.unlink()
    pages = []
    for start in range(0, len(entries), PER_PAGE):
        path = out / f"{which}-{start // PER_PAGE + 1:02d}.png"
        _render_page(directory, entries[start : start + PER_PAGE]).save(path)
        pages.append(rel(project, path))
    index = {"set": which, "generated": now(), "pages": pages, "items": entries}
    index_path(project, which).write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    return index


def load_index(project: Path, which: str) -> dict | None:
    path = index_path(project, which)
    return json.loads(path.read_text()) if path.is_file() else None


def resolve(project: Path, which: str, numbers: list[int]) -> list[str]:
    """사용자가 본 모음판의 번호를 파일 이름으로 바꾼다."""
    index = load_index(project, which)
    if index is None:
        raise GfError(f"{which} 모음판이 없다. 먼저 gf ref sheet --set {which} 를 실행한다.")
    by_number = {entry["n"]: entry["file"] for entry in index["items"]}
    missing = [number for number in numbers if number not in by_number]
    if missing:
        raise GfError(
            f"모음판에 없는 번호: {', '.join(map(str, missing))} (1~{len(by_number)} 중에서 고른다)"
        )
    return [by_number[number] for number in dict.fromkeys(numbers)]
