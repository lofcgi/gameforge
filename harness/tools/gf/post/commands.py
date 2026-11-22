import json
import shutil
from pathlib import Path

import numpy as np

from gf.core.output import GfError, fail, ok
from gf.core.paths import inside, project_dir, rel, source
from gf.post import (
    align,
    audio_loop,
    chroma,
    contact,
    frames,
    inspect_image,
    loop,
    palette,
    pixel,
    resize,
    sheet,
)
from gf.post.io import images, load_rgba, save_rgba, unique_colours


def _targets(project: Path, paths: list[Path], out: str) -> list[Path]:
    """입력 파일마다 결과 폴더 안의 같은 이름 PNG."""
    out_dir = inside(project, out)
    names = [path.stem for path in paths]
    if len(set(names)) != len(names):
        raise GfError("입력 파일 이름이 겹쳐 결과가 서로 덮어쓴다. 폴더를 나눠 실행한다.")
    return [out_dir / f"{name}.png" for name in names]


def _coverage(pixels: np.ndarray) -> float:
    return round(float((pixels[..., 3] > 0).mean()), 4)


def cmd_chroma(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    reports = []
    for path, target in zip(paths, _targets(project, paths, args.out)):
        pixels = load_rgba(path)
        key = chroma.border_colour(pixels) if args.key == "auto" else chroma.parse_colour(args.key)
        keyed = chroma.key_out(pixels, key, args.tolerance, args.soft, args.erode, args.despill, args.hard)
        save_rgba(keyed, target)
        reports.append({"file": rel(project, target), "key": chroma.to_hex(key), "alpha_coverage": _coverage(keyed)})
    return ok(files=[r["file"] for r in reports], cost_usd=0.0, images=reports)


def _grid(args, pixels: np.ndarray) -> dict:
    """칸 크기를 --size, --height, --cell, 자동 감지 순으로 정한다."""
    height, width = pixels.shape[:2]
    if args.size:
        target_w, target_h = _parse_size(args.size)
        return {"cell": [width / target_w, height / target_h], "offset": [0, 0], "source": "size"}
    if args.height:
        return {"cell": [height / args.height, height / args.height], "offset": [0, 0], "source": "height"}
    if args.cell:
        return {"cell": [args.cell, args.cell], "offset": [0, 0], "source": "cell"}
    detected = pixel.detect_cell(pixels, max_cell=args.max_cell)
    pixel.require_grid(detected)
    return {**detected, "source": "detected"}


def _trim(pixels: np.ndarray, path: Path) -> np.ndarray:
    """보이는 픽셀의 경계 상자로 자른다. 생성 그림은 대상이 화면의 일부만 차지한다."""
    rows, columns = np.where(pixels[..., 3] > 0)
    if not len(rows):
        raise GfError(f"{path.name}: 보이는 픽셀이 없어 자를 수 없다 (먼저 post chroma 로 배경을 뺀다).")
    return pixels[rows.min():rows.max() + 1, columns.min():columns.max() + 1]


def _parse_size(text: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in text.lower().split("x"))
    except ValueError as exc:
        raise GfError(f"크기는 가로x세로 형태다: {text}") from exc
    if width <= 0 or height <= 0:
        raise GfError(f"크기는 양수여야 한다: {text}")
    return width, height


def cmd_pixel_snap(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    out_dir = inside(project, args.out)
    preview_dir = None if args.no_preview else inside(project, args.preview or f"captures/inspect/pixel/{out_dir.name}")
    if preview_dir == out_dir:
        raise GfError("--preview 는 --out 과 다른 폴더여야 한다 (미리보기가 1x 결과와 섞인다).")
    reports, files, previews = [], [], []
    for path, target in zip(paths, _targets(project, paths, args.out)):
        pixels = load_rgba(path)
        if args.trim:
            pixels = _trim(pixels, path)
        try:
            grid = _grid(args, pixels)
        except GfError as exc:
            raise GfError(f"{path.name}: {exc}") from exc
        small = pixel.snap(pixels, tuple(grid["cell"]), tuple(grid["offset"]))
        scale = args.scale or max(1, round(grid["cell"][0]))
        save_rgba(small, target)
        files.append(rel(project, target))
        preview = None
        if preview_dir:
            preview = rel(project, save_rgba(pixel.upscale(small, scale), preview_dir / f"{target.stem}_x{scale}.png"))
            previews.append(preview)
        reports.append(
            {
                "file": rel(project, target),
                "preview": preview,
                "cell": [round(c, 3) for c in grid["cell"]],
                "offset": grid["offset"],
                "cell_source": grid["source"],
                "confidence": grid.get("confidence"),
                "size": [small.shape[1], small.shape[0]],
                "unique_colours": unique_colours(small),
            }
        )
    return ok(files=files, previews=previews, cost_usd=0.0, images=reports)


def cmd_resize(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    loaded = [resize.inset(load_rgba(path), args.inset) for path in paths]
    if args.trim:
        loaded = [_trim(pixels, path) for pixels, path in zip(loaded, paths)]
    given = [name for name in ("height", "width", "scale", "fit") if getattr(args, name) is not None]
    if len(given) != 1:
        raise GfError("--height, --width, --scale, --fit 중 정확히 하나를 준다.")
    widest, tallest = max(p.shape[1] for p in loaded), max(p.shape[0] for p in loaded)
    if args.scale is not None:
        factor = args.scale
    elif args.height is not None:
        factor = args.height / tallest
    elif args.width is not None:
        factor = args.width / widest
    else:
        fit_w, fit_h = _parse_size(args.fit)
        factor = min(fit_w / widest, fit_h / tallest)
    if factor <= 0:
        raise GfError("배율은 양수여야 한다.")
    canvas = _parse_size(args.canvas) if args.canvas else None
    reports = []
    for path, target, pixels in zip(paths, _targets(project, paths, args.out), loaded):
        small = resize.scale(pixels, factor, args.nearest)
        if canvas:
            small = resize.pad(small, canvas)
        save_rgba(small, target)
        reports.append({"file": rel(project, target), "from": [pixels.shape[1], pixels.shape[0]],
                        "size": [small.shape[1], small.shape[0]]})
    sizes = {tuple(r["size"]) for r in reports}
    return ok(files=[r["file"] for r in reports], cost_usd=0.0, factor=round(factor, 5),
              uniform_canvas=len(sizes) == 1, images=reports)


def cmd_palette_extract(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    colours = palette.extract([load_rgba(path) for path in paths], args.colors)
    target = inside(project, args.out)
    if target.suffix != ".json":
        raise GfError("--out 은 .json 파일이다 (같은 이름의 .png 견본이 함께 나온다).")
    saved = palette.save(colours, target, [rel(project, path) for path in paths])
    return ok(files=[rel(project, p) for p in saved], cost_usd=0.0, count=len(colours), colors=[chroma.to_hex(c) for c in colours])


def cmd_palette_apply(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    colours = palette.load(source(project, args.palette))
    reports = []
    for path, target in zip(paths, _targets(project, paths, args.out)):
        pixels = load_rgba(path)
        mapped = palette.apply(pixels, colours, args.dither)
        save_rgba(mapped, target)
        reports.append(
            {"file": rel(project, target), "colours_before": unique_colours(pixels), "colours_after": unique_colours(mapped)}
        )
    return ok(files=[r["file"] for r in reports], cost_usd=0.0, palette_size=len(colours), images=reports)


def _slot_names(args, slots: list[int]) -> list[str]:
    if not args.names:
        return [f"slot_{slot:02d}" for slot in slots]
    names = args.names.split(",")
    if len(names) != len(slots):
        raise GfError(f"--names 는 {len(slots)}개여야 한다 (칸 수와 같게).")
    return names


def cmd_frames(args) -> int:
    project = project_dir(args)
    video = source(project, args.video)
    out_dir = inside(project, args.out)
    info = frames.probe(video)
    span = (args.end if args.end is not None else info["duration"]) - (args.start or 0)
    if args.count and args.fps:
        raise GfError("--fps 와 --count 는 함께 쓸 수 없다.")
    fps = args.fps or (args.count / span if args.count else info["fps"])
    if not args.grid:
        saved = frames.extract(video, out_dir, fps, args.count, args.start, args.end)
        return ok(files=[rel(project, p) for p in saved], cost_usd=0.0, video=info, fps=round(fps, 3), count=len(saved))
    columns, rows = _parse_size(args.grid)
    slots = list(range(columns * rows)) if args.slot is None else args.slot
    folders = {}
    for slot, name in zip(slots, _slot_names(args, slots)):
        rect = frames.slot_rect(info["width"], info["height"], columns, rows, slot, args.inset)
        saved = frames.extract(video, out_dir / name, fps, args.count, args.start, args.end, rect)
        folders[name] = {"slot": slot, "rect": list(rect), "count": len(saved), "dir": rel(project, out_dir / name)}
    return ok(files=[f["dir"] for f in folders.values()], cost_usd=0.0, video=info, fps=round(fps, 3), slots=folders)


def cmd_align(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    loaded = [load_rgba(path) for path in paths]
    boxes = []
    for path, pixels in zip(paths, loaded):
        try:
            boxes.append(align.measure(pixels, args.anchor))
        except GfError as exc:
            raise GfError(f"{exc}: {path.name}") from exc
    size = _parse_size(args.size) if args.size else align.canvas_for(boxes, args.pad)
    targets = _targets(project, paths, args.out)
    offsets = []
    for target, pixels, box in zip(targets, loaded, boxes):
        placed, offset = align.place(pixels, box, size, args.pad)
        save_rgba(placed, target)
        offsets.append(offset)
    return ok(
        files=[rel(project, t) for t in targets],
        cost_usd=0.0,
        canvas=list(size),
        baseline_y=size[1] - args.pad,
        anchor_x=size[0] / 2,
        offsets=offsets,
    )


def cmd_loop(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    found = loop.find([load_rgba(path) for path in paths], args.min_length, args.max_length)
    out_dir = inside(project, args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, path in enumerate(paths[found["start"] : found["end"]]):
        saved.append(shutil.copyfile(path, out_dir / f"frame_{index:04d}.png"))
    return ok(files=[rel(project, p) for p in saved], cost_usd=0.0, total_frames=len(paths), **found)


def cmd_sheet(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    packed, rects = sheet.pack([load_rgba(path) for path in paths], args.columns, args.padding)
    out_dir = inside(project, args.out)
    png = save_rgba(packed, out_dir / f"{args.name}.png")
    data = sheet.manifest(png.name, args.name, args.fps, args.loop, rects)
    manifest_path = out_dir / f"{args.name}.json"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    godot_root = inside(project, args.godot_root)
    if not png.is_relative_to(godot_root):
        raise GfError(f"시트가 Godot 프로젝트 루트 {godot_root} 밖에 있어 res:// 경로를 만들 수 없다.")
    res_path = "res://" + png.relative_to(godot_root).as_posix()
    tres = out_dir / f"{args.name}.tres"
    tres.write_text(sheet.godot_sprite_frames(res_path, args.name, args.fps, args.loop, rects))
    return ok(
        files=[rel(project, p) for p in (png, manifest_path, tres)],
        cost_usd=0.0,
        frames=len(rects),
        sheet_size=[packed.shape[1], packed.shape[0]],
        frame_size=data["frame_size"],
        texture=res_path,
    )


def cmd_contact(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    labels = [f"{i}" if args.labels == "index" else f"{i} {p.stem}" for i, p in enumerate(paths)]
    target = inside(project, args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    contact.build(paths, labels, args.columns, args.thumb).save(target)
    index = {str(i): rel(project, p) for i, p in enumerate(paths)}
    return ok(files=[rel(project, target)], cost_usd=0.0, count=len(paths), index=index)


def cmd_inspect(args) -> int:
    project = project_dir(args)
    paths = images(project, args.inputs)
    if args.check and len(paths) != 1:
        raise GfError("--check 는 이미지 하나에만 쓴다.")
    reports, files = [], []
    for path in paths:
        pixels = load_rgba(path)
        reports.append({"file": rel(project, path), **inspect_image.report(pixels, args.max_colors)})
        if args.check:
            target = inside(project, args.check)
            target.parent.mkdir(parents=True, exist_ok=True)
            inspect_image.check_image(pixels, args.check_scale).save(target)
            files.append(rel(project, target))
    return ok(files=files, cost_usd=0.0, images=reports)


def _inputs(parser, out: str | None) -> None:
    parser.add_argument("inputs", nargs="+", help="이미지 파일 또는 폴더 (상대 경로는 게임 프로젝트 기준)")
    if out:
        parser.add_argument("--out", default=out, help="결과 폴더")


def cmd_audio_loop(args) -> int:
    project = project_dir(args)
    path = source(project, args.input)
    target = inside(project, args.out)
    samples, rate = audio_loop.decode(path)
    before = audio_loop.seam_report(samples, rate)
    looped, done = audio_loop.make_loop(samples, rate, args.fade)
    audio_loop.encode(looped, rate, target)
    # 코덱이 앞뒤에 무음을 붙이는 형식이 있어, 방금 쓴 파일을 다시 풀어서 잰다.
    written, written_rate = audio_loop.decode(target)
    after = audio_loop.seam_report(written, written_rate)
    fields = dict(files=[rel(project, target)], cost_usd=0.0, source=rel(project, path), **done, before=before, after=after)
    if not after["seamless"]:
        hint = " 손실 압축이 이음매를 흐트러뜨렸다. --out 을 .wav 로 준다." if target.suffix.lower() != ".wav" else ""
        return fail(f"다듬은 파일의 이음매가 기준을 넘는다: {' / '.join(after['problems'])}.{hint}", **fields)
    return ok(**fields)


def register(sub) -> None:
    p = sub.add_parser("post", help="생성물 후처리 (네트워크 없음)")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("chroma", help="단색 배경을 알파로 빼고 가장자리 번짐을 지운다")
    _inputs(q, "assets/raw/keyed")
    q.add_argument("--key", default="auto", help="배경색 #RRGGBB. auto 는 이미지 테두리 색을 쓴다")
    q.add_argument("--tolerance", type=float, default=60, help="이 거리(RGB)까지는 완전히 투명")
    q.add_argument("--soft", type=float, default=40, help="그 위로 이 거리만큼은 반투명으로 잇는다")
    q.add_argument("--erode", type=int, default=1, help="투명 영역에 닿은 테두리를 깎는 픽셀 수. 1x 픽셀 아트에는 0")
    q.add_argument("--despill", type=int, default=3, help="깎고 남은 가장자리에서 배경색 물을 빼는 폭(픽셀). 압축된 영상 프레임은 더 넓게")
    q.add_argument("--hard", action="store_true", help="알파를 0/255 로만 남긴다 (픽셀 아트용)")
    q.set_defaults(func=cmd_chroma)

    q = s.add_parser("pixel-snap", help="가짜 픽셀 아트를 격자에 맞춰 1x 픽셀 아트로 줄인다")
    _inputs(q, "assets/raw/pixel")
    q.add_argument("--cell", type=float, help="아트 픽셀 한 칸의 크기(px). 없으면 자동 감지")
    q.add_argument("--size", help="목표 1x 크기 가로x세로. 칸 크기를 이 값에서 계산한다 (비율이 다르면 늘어난다)")
    q.add_argument("--height", type=int, help="목표 1x 세로 크기(px). 가로는 비율대로 정해진다. 보통 --trim 과 함께 쓴다")
    q.add_argument("--trim", action="store_true", help="격자를 맞추기 전에 보이는 픽셀의 경계 상자로 자른다 (배경을 뺀 그림에)")
    q.add_argument("--max-cell", type=float, default=64, help="자동 감지할 칸 크기 상한")
    q.add_argument("--scale", type=int, help="미리보기 확대 배율 (기본: 칸 크기)")
    q.add_argument("--preview", help="확대 미리보기 폴더 (기본: captures/inspect/pixel/<결과 폴더 이름>). 결과 폴더와 섞지 않는다")
    q.add_argument("--no-preview", action="store_true", help="확대 미리보기를 만들지 않는다")
    q.set_defaults(func=cmd_pixel_snap)

    q = s.add_parser("resize", help="픽셀 아트가 아닌 그림을 같은 배율로 줄인다 (알파 보존, 고품질 재표본)")
    _inputs(q, "assets/raw/resized")
    q.add_argument("--height", type=int, help="가장 큰 입력의 세로가 이 값(px)이 되는 배율")
    q.add_argument("--width", type=int, help="가장 큰 입력의 가로가 이 값(px)이 되는 배율")
    q.add_argument("--fit", help="가장 큰 입력이 가로x세로 안에 들어가는 배율")
    q.add_argument("--scale", type=float, help="배율을 직접 준다 (예: 0.25)")
    q.add_argument("--canvas", help="결과를 가로x세로 캔버스의 아래 가운데에 놓는다 (프레임 크기 통일)")
    q.add_argument("--trim", action="store_true",
                   help="줄이기 전에 보이는 픽셀의 경계 상자로 자른다. --height 가 그림 전체가 아니라 대상의 세로가 된다 "
                        "(배경을 뺀 정지 그림에. 정렬한 애니메이션 프레임에는 쓰지 않는다)")
    q.add_argument("--inset", type=int, default=0,
                   help="줄이기 전에 네 가장자리를 이 픽셀 수만큼 잘라 낸다 (생성된 타일에 둘린 테두리 선을 없앨 때)")
    q.add_argument("--nearest", action="store_true", help="최근접 표본 (이미 픽셀 아트인 그림의 정수배 변환용)")
    q.set_defaults(func=cmd_resize)

    q = s.add_parser("palette", help="공용 팔레트를 뽑거나 적용한다")
    t = q.add_subparsers(dest="action", required=True)
    r = t.add_parser("extract", help="이미지들에서 N색 팔레트를 뽑아 JSON 과 PNG 견본으로 저장")
    _inputs(r, None)
    r.add_argument("--colors", type=int, default=16)
    r.add_argument("--out", default="design/palette.json")
    r.set_defaults(func=cmd_palette_extract)
    r = t.add_parser("apply", help="팔레트의 가장 가까운 색으로 바꾼다")
    _inputs(r, "assets/raw/paletted")
    r.add_argument("--palette", default="design/palette.json", help="팔레트 JSON, .hex, 또는 견본 이미지")
    r.add_argument("--dither", action="store_true", help="Floyd-Steinberg 디더링을 쓴다 (기본은 쓰지 않음)")
    r.set_defaults(func=cmd_palette_apply)

    q = s.add_parser("frames", help="영상에서 프레임을 뽑는다 (격자 칸별로 자르기 가능)")
    q.add_argument("video")
    q.add_argument("--out", default="assets/raw/frames")
    q.add_argument("--fps", type=float, help="초당 뽑을 장수 (기본: 영상의 fps)")
    q.add_argument("--count", type=int, help="구간 전체에서 고르게 뽑을 장수")
    q.add_argument("--start", type=float, help="시작 시각(초)")
    q.add_argument("--end", type=float, help="끝 시각(초)")
    q.add_argument("--grid", help="한 영상에 여러 캐릭터가 놓인 격자. 열x행 (예: 5x2)")
    q.add_argument("--slot", type=int, action="append", help="뽑을 칸 번호(0부터, 왼쪽 위에서 가로로). 없으면 전부")
    q.add_argument("--names", help="칸별 폴더 이름. 쉼표로 구분")
    q.add_argument("--inset", type=int, default=0, help="칸 가장자리를 안쪽으로 깎는 픽셀 수")
    q.set_defaults(func=cmd_frames)

    q = s.add_parser("align", help="프레임들의 발 기준선과 가로 기준점을 맞추고 캔버스를 통일한다")
    _inputs(q, "assets/raw/aligned")
    q.add_argument("--anchor", choices=["bbox", "mass"], default="bbox", help="가로 기준점: 경계 상자 중앙 또는 무게중심")
    q.add_argument("--pad", type=int, default=1, help="캔버스 여백(px)")
    q.add_argument("--size", help="캔버스 크기를 가로x세로로 고정")
    q.set_defaults(func=cmd_align)

    q = s.add_parser("loop", help="가장 매끄럽게 이어지는 반복 구간을 골라 낸다")
    _inputs(q, "assets/raw/loop")
    q.add_argument("--min-length", type=int, default=4, help="반복 구간의 최소 프레임 수")
    q.add_argument("--max-length", type=int, help="반복 구간의 최대 프레임 수")
    q.set_defaults(func=cmd_loop)

    q = s.add_parser("audio-loop", help="음악·환경음의 앞뒤 무음을 자르고 꼬리를 머리에 섞어 매끄럽게 반복되게 만든다")
    q.add_argument("input", help="오디오 파일 (게임 프로젝트 기준)")
    q.add_argument("--out", required=True, help="결과 파일. 확장자가 형식을 정한다 (.wav .mp3 .ogg .opus)")
    q.add_argument("--fade", type=float, help="겹쳐 섞을 길이(초). 없으면 꼬리와 머리의 박자가 가장 잘 맞는 길이(0.25~2초)를 고른다")
    q.set_defaults(func=cmd_audio_loop)

    q = s.add_parser("sheet", help="스프라이트 시트 PNG + JSON 매니페스트 + Godot SpriteFrames")
    _inputs(q, "assets/game/sprites")
    q.add_argument("--name", required=True, help="애니메이션 이름 (파일 이름으로도 쓴다)")
    q.add_argument("--fps", type=float, default=12)
    q.add_argument("--columns", type=int)
    q.add_argument("--padding", type=int, default=0, help="프레임 사이 간격(px)")
    q.add_argument("--no-loop", dest="loop", action="store_false", help="반복하지 않는 애니메이션")
    q.add_argument("--godot-root", default=".", help="project.godot 이 있는 폴더 (res:// 의 기준)")
    q.set_defaults(func=cmd_sheet)

    q = s.add_parser("contact", help="번호를 붙인 모음판 한 장을 만든다")
    q.add_argument("inputs", nargs="+")
    q.add_argument("--out", required=True, help="결과 PNG")
    q.add_argument("--columns", type=int)
    q.add_argument("--thumb", type=int, default=256, help="썸네일 한 변(px)")
    q.add_argument("--labels", choices=["index", "name"], default="index")
    q.set_defaults(func=cmd_contact)

    q = s.add_parser("inspect", help="크기·알파·색 수·픽셀 아트 여부를 숫자로 보고한다")
    q.add_argument("inputs", nargs="+")
    q.add_argument("--max-colors", type=int, default=64, help="픽셀 아트로 볼 색 수 상한")
    q.add_argument("--check", help="밝은/어두운 배경에 올린 확인용 PNG 를 이 경로에 만든다")
    q.add_argument("--check-scale", type=int, default=1, help="확인용 이미지 확대 배율")
    q.set_defaults(func=cmd_inspect)
