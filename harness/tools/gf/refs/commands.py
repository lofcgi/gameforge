import tempfile
from collections import Counter
from pathlib import Path

from gf.core.output import GfError, ok
from gf.core.paths import gf_dir, project_dir, rel, resolve
from gf.refs import fetch, picks, sheet, steam, store, traits, video


def _project(args) -> Path:
    project = project_dir(args)
    gf_dir(project)
    return project


def _inbox_files(project: Path, names: list[str]) -> list[str]:
    return [rel(project, store.inbox(project) / name) for name in names]


def steam_cmd(args) -> int:
    project = _project(args)
    if args.max < 1:
        raise GfError("--max 는 1 이상이어야 한다")
    with fetch.client() as http:
        result = steam.collect(project, http, steam.parse_appid(args.app), args.max)
    return ok(files=_inbox_files(project, result["added"]), cost_usd=0.0, **result)


def _frame_times(args, source: Path) -> list[float]:
    count = None if args.every is not None else (12 if args.count is None else args.count)
    return video.timestamps(video.duration(source), every=args.every, count=count, limit=args.max)


def _extract(args, source: Path, workdir: Path) -> list[tuple[Path, float | None]]:
    if args.scene is not None:
        return [
            (frame, None) for frame in video.scene_frames(source, args.scene, args.max, workdir)
        ]
    frames = []
    for index, at in enumerate(_frame_times(args, source)):
        out = workdir / f"frame-{index:04d}.jpg"
        video.grab(source, at, out)
        frames.append((out, at))
    return frames


def frames(args) -> int:
    project = _project(args)
    if args.max < 1:
        raise GfError("--max 는 1 이상이어야 한다")
    with tempfile.TemporaryDirectory(prefix="gf-frames-") as tmp:
        workdir = Path(tmp)
        if fetch.is_url(args.source):
            info = video.download(args.source, workdir)
        else:
            local = resolve(project, args.source)
            if not local.is_file():
                raise GfError(f"영상 파일이 없다: {args.source}")
            info = {"path": local, "title": local.stem, "url": None}
        added, duplicates = [], []
        for frame, at in _extract(args, info["path"], workdir):
            meta, created = store.add(
                project,
                frame.read_bytes(),
                origin="video",
                source_url=info["url"],
                page_title=info["title"],
                title=info["title"],
                note=args.note,
                tags=args.tags,
                extra={"video_time": at},
            )
            (added if created else duplicates).append(meta["file"])
    return ok(
        files=_inbox_files(project, added),
        cost_usd=0.0,
        title=info["title"],
        added=added,
        duplicates=duplicates,
    )


def _read_source(
    http, project: Path, source: str, page: str | None
) -> tuple[bytes, str | None, str | None]:
    if fetch.is_url(source):
        return fetch.get_bytes(http, source, referer=page), source, None
    path = resolve(project, source)
    if not path.is_file():
        raise GfError(f"파일이 없다: {path}")
    return path.read_bytes(), None, path.name


def add(args) -> int:
    project = _project(args)
    if args.source_url and not fetch.is_url(args.source_url):
        raise GfError(f"--source-url 은 http(s) 주소여야 한다: {args.source_url}")
    added, duplicates = [], []
    with fetch.client() as http:
        for source in args.sources:
            data, url, name = _read_source(http, project, source, args.source_url)
            try:
                meta, created = store.add(
                    project,
                    data,
                    origin="manual",
                    kind="anti" if args.anti else "reference",
                    source_url=args.source_url or url,
                    page_title=name,
                    title=args.title,
                    note=args.note,
                    tags=args.tags,
                    extra={"image_url": url} if url else None,
                )
            except GfError as exc:
                raise GfError(f"{source}: {exc}") from exc
            (added if created else duplicates).append(meta["file"])
    return ok(files=_inbox_files(project, added), cost_usd=0.0, added=added, duplicates=duplicates)


def sheet_cmd(args) -> int:
    project = _project(args)
    index = sheet.build(project, args.set)
    return ok(
        files=index["pages"],
        cost_usd=0.0,
        index=rel(project, sheet.index_path(project, args.set)),
        count=len(index["items"]),
        pages=len(index["pages"]),
    )


def _picks_result(project: Path, changed: list[str]) -> int:
    index = picks.write_index(project)
    return ok(
        files=[rel(project, store.picked(project) / name) for name in changed],
        cost_usd=0.0,
        index=rel(project, store.picked(project) / picks.INDEX),
        reference=index["reference"],
        anti=index["anti"],
        warnings=index["warnings"],
    )


def pick(args) -> int:
    project = _project(args)
    files = sheet.resolve(project, "inbox", args.numbers)
    for file in files:
        picks.set_item(
            project, file, picked=True, note=args.note, kind="anti" if args.anti else None
        )
    return _picks_result(project, files)


def unpick(args) -> int:
    project = _project(args)
    chosen = picks.picked_files(project)
    if args.all:
        files = sorted(chosen)
    elif args.numbers:
        files = sheet.resolve(project, args.set, args.numbers)
    else:
        raise GfError("뺄 번호를 주거나 --all 을 쓴다")
    missing = [file for file in files if file not in chosen]
    if missing:
        raise GfError(f"고르지 않은 항목이다: {', '.join(missing)}")
    for file in files:
        picks.remove(project, file)
    return _picks_result(project, [])


def traits_cmd(args) -> int:
    project = _project(args)
    if args.colors < 1:
        raise GfError("--colors 는 1 이상이어야 한다")
    result = traits.build(project, args.colors)
    directory = store.picked(project)
    summary = {
        kind: {
            "count": group["count"],
            "palette": [colour["hex"] for colour in group["palette"]],
            "accents": [colour["hex"] for colour in group["accents"]],
            "temperature": group["temperature"],
            **{name: group[name]["mean"] for name in traits.SCALARS},
        }
        for kind, group in (("reference", result["reference"]), ("anti", result["anti"]))
        if group
    }
    return ok(
        files=[
            rel(project, directory / "traits.json"),
            rel(project, directory / "traits-palette.png"),
        ],
        cost_usd=0.0,
        difference=result["difference"],
        **summary,
    )


def status(args) -> int:
    project = _project(args)
    metas = store.items(store.inbox(project))
    chosen = store.items(store.picked(project))
    return ok(
        files=[],
        cost_usd=0.0,
        inbox={
            "count": len(metas),
            "by_origin": dict(Counter(meta["origin"] for meta in metas)),
            "by_kind": dict(Counter(meta["kind"] for meta in metas)),
        },
        picked={
            "count": len(chosen),
            "by_kind": dict(Counter(meta["kind"] for meta in chosen)),
            "warnings": [w for w in [picks.dominance(chosen)] if w],
        },
        paths={
            "inbox": rel(project, store.inbox(project)),
            "picked": rel(project, store.picked(project)),
            "sheets": rel(project, sheet.sheets_dir(project)),
        },
    )


def register(sub) -> None:
    p = sub.add_parser("ref", help="레퍼런스 수집과 선택")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("steam", help="Steam 상점의 공개 스크린샷을 보관함에 넣는다")
    q.add_argument("app", help="appid 또는 상점 주소")
    q.add_argument("--max", type=int, default=8, help="가져올 장수 (기본 8)")
    q.set_defaults(func=steam_cmd)

    q = s.add_parser("frames", help="영상(주소 또는 파일)에서 대표 프레임을 뽑아 보관함에 넣는다")
    q.add_argument("source", help="영상 주소 또는 파일 경로")
    how = q.add_mutually_exclusive_group()
    how.add_argument("--every", type=float, help="S초마다 한 장")
    how.add_argument("--count", type=int, help="같은 간격으로 N장 (기본 12)")
    how.add_argument("--scene", type=float, help="장면 전환 기준(0~1, 보통 0.3)으로 뽑는다")
    q.add_argument("--max", type=int, default=40, help="최대 장수 (기본 40)")
    q.add_argument("--note", default="")
    q.add_argument("--tags", default="", help="쉼표로 구분")
    q.set_defaults(func=frames)

    q = s.add_parser("add", help="파일이나 이미지 주소를 직접 보관함에 넣는다")
    q.add_argument("sources", nargs="+", help="이미지 파일 경로 또는 주소")
    q.add_argument("--note", default="", help="이 이미지에서 무엇을 볼지 한 줄")
    q.add_argument("--tags", default="", help="쉼표로 구분")
    q.add_argument(
        "--source-url",
        help="이미지가 실려 있던 페이지 주소. 주면 출처로 기록하고 이미지 주소는 image_url 에 남긴다",
    )
    q.add_argument("--title", help="작품이나 작가 이름. 쏠림 판단을 사이트가 아니라 작품 단위로 한다")
    q.add_argument("--anti", action="store_true", help="'이런 느낌은 아님'으로 넣는다")
    q.set_defaults(func=add)

    q = s.add_parser("sheet", help="번호가 붙은 모음판 PNG 와 번호 색인을 만든다")
    q.add_argument("--set", choices=store.SETS, default="inbox")
    q.set_defaults(func=sheet_cmd)

    q = s.add_parser("pick", help="보관함 모음판의 번호로 레퍼런스를 고른다")
    q.add_argument("numbers", nargs="+", type=int, help="gf ref sheet 가 붙인 번호")
    q.add_argument("--note", help="여기서 무엇을 가져올지 (조명만, 팔레트, 비율 등)")
    q.add_argument("--anti", action="store_true", help="'이런 느낌은 아님'으로 고른다")
    q.set_defaults(func=pick)

    q = s.add_parser("unpick", help="고른 것에서 뺀다")
    q.add_argument("numbers", nargs="*", type=int)
    q.add_argument("--set", choices=store.SETS, default="inbox", help="번호가 어느 모음판의 것인지")
    q.add_argument("--all", action="store_true", help="전부 뺀다")
    q.set_defaults(func=unpick)

    q = s.add_parser("traits", help="고른 묶음의 팔레트·밝기·대비 등 측정값을 낸다")
    q.add_argument("--colors", type=int, default=6, help="팔레트 색 수 (기본 6)")
    q.set_defaults(func=traits_cmd)

    s.add_parser("status", help="보관함과 고른 것의 현황").set_defaults(func=status)
