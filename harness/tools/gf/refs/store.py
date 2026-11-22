"""레퍼런스 보관함. 이미지 하나마다 같은 이름의 .json 메타를 둔다."""

import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError

from gf.core.output import GfError

ORIGINS = ["steam", "video", "manual"]
KINDS = ["reference", "anti"]
SETS = ["inbox", "picked"]
# 이 형식은 원본 바이트를 그대로 둔다. 그 밖의 형식은 에이전트가 열어 볼 수 있게 PNG로 바꾼다.
KEEP_FORMATS = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "GIF": ".gif"}
MAX_PIXELS = 64_000_000


def references(project: Path) -> Path:
    return project / "references"


def set_dir(project: Path, which: str) -> Path:
    if which not in SETS:
        raise GfError(f"알 수 없는 묶음 '{which}'. 가능한 값: {', '.join(SETS)}")
    return references(project) / which


def inbox(project: Path) -> Path:
    return set_dir(project, "inbox")


def picked(project: Path) -> Path:
    return set_dir(project, "picked")


def clean_tags(tags) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, str):
        tags = tags.split(",")
    if not isinstance(tags, (list, tuple)):
        raise GfError("tags 는 문자열 목록이어야 한다")
    seen: list[str] = []
    for tag in tags:
        text = str(tag).strip()
        if text and text not in seen:
            seen.append(text)
    return seen


def check_kind(kind: str) -> str:
    if kind not in KINDS:
        raise GfError(f"알 수 없는 종류 '{kind}'. 가능한 값: {', '.join(KINDS)}")
    return kind


def _decode(data: bytes) -> tuple[bytes, str, tuple[int, int]]:
    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            if width * height > MAX_PIXELS:
                raise GfError(f"이미지가 너무 크다 ({width}x{height})")
            image.load()
            if image.format in KEEP_FORMATS:
                return data, KEEP_FORMATS[image.format], image.size
            buffer = io.BytesIO()
            image.convert("RGBA").save(buffer, "PNG")
            return buffer.getvalue(), ".png", image.size
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise GfError("이미지로 읽을 수 없는 데이터다") from exc


def meta_path(image: Path) -> Path:
    return image.with_suffix(".json")


def write_meta(directory: Path, meta: dict) -> None:
    path = meta_path(directory / meta["file"])
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")


def items(directory: Path) -> list[dict]:
    """메타가 붙은 이미지만 수집 시각 순으로 돌려준다."""
    found = []
    if not directory.is_dir():
        return found
    for image in directory.iterdir():
        if image.suffix not in KEEP_FORMATS.values() or not meta_path(image).is_file():
            continue
        found.append(json.loads(meta_path(image).read_text()))
    return sorted(found, key=lambda meta: (meta["captured"], meta["file"]))


def get(directory: Path, file: str) -> dict:
    if Path(file).name != file or not (directory / file).is_file():
        raise GfError(f"항목이 없다: {file}")
    path = meta_path(directory / file)
    if not path.is_file():
        raise GfError(f"메타가 없는 파일이다: {file}")
    return json.loads(path.read_text())


def add(
    project: Path,
    data: bytes,
    *,
    origin: str,
    kind: str = "reference",
    source_url: str | None = None,
    page_title: str | None = None,
    title: str | None = None,
    note: str = "",
    tags=None,
    extra: dict | None = None,
) -> tuple[dict, bool]:
    """보관함에 넣는다. 같은 해시가 이미 있으면 기존 메타와 False 를 돌려준다."""
    if origin not in ORIGINS:
        raise GfError(f"알 수 없는 출처 '{origin}'. 가능한 값: {', '.join(ORIGINS)}")
    check_kind(kind)
    directory = inbox(project)
    directory.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(data).hexdigest()
    for existing in items(directory):
        if existing["sha256"] == sha:
            return existing, False
    body, suffix, (width, height) = _decode(data)
    meta = {
        "file": f"{origin}-{sha[:12]}{suffix}",
        "sha256": sha,
        "origin": origin,
        "kind": kind,
        "source_url": source_url,
        "page_title": page_title,
        "title": title,
        "note": note.strip(),
        "tags": clean_tags(tags),
        "captured": datetime.now(UTC).isoformat(),
        "width": width,
        "height": height,
        **(extra or {}),
    }
    (directory / meta["file"]).write_bytes(body)
    write_meta(directory, meta)
    return meta, True


def update(directory: Path, file: str, *, note=None, tags=None, kind=None) -> dict:
    meta = get(directory, file)
    if note is not None:
        meta["note"] = str(note).strip()
    if tags is not None:
        meta["tags"] = clean_tags(tags)
    if kind is not None:
        meta["kind"] = check_kind(kind)
    write_meta(directory, meta)
    return meta


def source_key(meta: dict) -> tuple[str, str] | None:
    """쏠림 판단에 쓰는 출처 묶음: 작품 제목이 있으면 제목, 없으면 도메인."""
    if meta.get("title"):
        return ("title", meta["title"])
    host = urlparse(meta.get("source_url") or "").hostname
    if host:
        return ("domain", host.removeprefix("www."))
    return None
