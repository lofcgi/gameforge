"""컷신 에셋 후처리. 하네스의 post 모듈(chroma, pixel, palette)을 그대로 쓰되,
한 장에 여러 포즈가 든 시트를 조각으로 나누고 같은 캔버스에 맞추는 일을 더한다.

  proc.py sprite <원본> <결과 접두어> --h 56 [--split] [--same] [--names a,b,c]
  proc.py bg <원본> <결과.png> --size 840x360 [--crop l,t,r,b(0~1)]

실행: uv run -q --project <harness>/tools python proc.py ...
"""

import argparse
import sys
from collections import deque
from pathlib import Path

import numpy as np

from gf.post import chroma, palette, pixel
from gf.post.io import load_rgba, save_rgba

ROOT = Path(__file__).resolve().parents[4]
PALETTE = palette.load(ROOT / "design/look/palette.json")
COOL = {"#D79966": "#7BAEB9", "#DFB68B": "#B8D0BF", "#B4774F": "#799088", "#8C533C": "#546166", "#5E342B": "#2E3068"}
KEY = np.array([255, 0, 255], dtype=np.float32)


def key(pixels: np.ndarray) -> np.ndarray:
    out = chroma.key_out(pixels, KEY, tolerance=120, soft=0, erode=0, despill=0, hard=True)
    rgb = pixels[..., :3].astype(np.int32)
    # 가장자리에 남는 분홍 물: 빨강·파랑이 초록보다 훨씬 큰 픽셀은 배경으로 본다.
    pink = (rgb[..., 0] - rgb[..., 1] > 70) & (rgb[..., 2] - rgb[..., 1] > 70)
    out[pink] = 0
    return out


def components(alpha: np.ndarray, step: int = 8, join: int = 2, min_cells: int = 30) -> list[tuple[int, int, int, int]]:
    """떨어진 덩어리의 경계 상자 (l, t, r, b). 읽는 순서(위→아래, 왼→오른)로 돌려준다."""
    h, w = alpha.shape
    gh, gw = h // step, w // step
    grid = alpha[: gh * step, : gw * step].reshape(gh, step, gw, step).max(axis=(1, 3)) > 0
    grid = chroma.dilate(grid, join)
    seen = np.zeros_like(grid)
    boxes = []
    for y in range(gh):
        for x in range(gw):
            if not grid[y, x] or seen[y, x]:
                continue
            queue = deque([(y, x)])
            seen[y, x] = True
            l = r = x
            t = b = y
            count = 0
            while queue:
                cy, cx = queue.popleft()
                count += 1
                l, r, t, b = min(l, cx), max(r, cx), min(t, cy), max(b, cy)
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < gh and 0 <= nx < gw and grid[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
            if count >= min_cells:
                boxes.append((max(0, (l - join) * step), max(0, (t - join) * step), min(w, (r + 1 + join) * step), min(h, (b + 1 + join) * step)))
    row = max(1, int(np.median([b[3] - b[1] for b in boxes]) * 0.6)) if boxes else 1
    boxes.sort(key=lambda b: (round((b[1] + b[3]) / 2 / row), b[0]))
    return boxes


def trim(pixels: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(pixels[..., 3])
    return pixels[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]


def finish(pixels: np.ndarray, cell: float) -> np.ndarray:
    small = pixel.snap(pixels, (cell, cell), (0, 0))
    return palette.apply(trim(small), PALETTE)


def sprite(args) -> None:
    keyed = key(load_rgba(Path(args.src)))
    for box in args.erase:
        l, t, r, b = (float(v) for v in box.split(","))
        h, w = keyed.shape[:2]
        keyed[int(t * h) : int(b * h), int(l * w) : int(r * w)] = 0
    if args.grid:
        cols, rows = (int(v) for v in args.grid.split("x"))
        h, w = keyed.shape[:2]
        parts = [trim(keyed[r * h // rows : (r + 1) * h // rows, c * w // cols : (c + 1) * w // cols]) for r in range(rows) for c in range(cols)]
    elif args.split:
        parts = [trim(keyed[t:b, l:r]) for l, t, r, b in components(keyed[..., 3])]
    else:
        parts = [trim(keyed)]
    names = args.names.split(",") if args.names else [str(i) for i in range(len(parts))]
    if args.same or args.cell:
        cell = args.cell or max(p.shape[0] for p in parts) / args.h
        cells = [cell] * len(parts)
    elif args.hs:
        cells = [p.shape[0] / int(h) for p, h in zip(parts, args.hs.split(","))]
    else:
        cells = [p.shape[0] / args.h for p in parts]
    outs = [finish(p, c) for p, c in zip(parts, cells)]
    if args.same:
        # 발밑 가운데를 기준으로 같은 캔버스에 놓는다.
        ch, cw = max(o.shape[0] for o in outs), max(o.shape[1] for o in outs)
        padded = []
        for o in outs:
            canvas = np.zeros((ch, cw, 4), dtype=np.uint8)
            x = (cw - o.shape[1]) // 2
            canvas[ch - o.shape[0] :, x : x + o.shape[1]] = o
            padded.append(canvas)
        outs = padded
    for i, o in enumerate(outs):
        name = names[i] if i < len(names) else f"extra{i}"
        suffix = "" if (len(outs) == 1 and not args.names) else f"_{name}"
        path = Path(f"{args.dst}{suffix}.png")
        save_rgba(o, path)
        print(path, o.shape[1], "x", o.shape[0], "cell", round(cells[i], 2))


def bg(args) -> None:
    pixels = load_rgba(Path(args.src))
    if args.crop:
        l, t, r, b = (float(v) for v in args.crop.split(","))
        h, w = pixels.shape[:2]
        pixels = pixels[int(t * h) : int(b * h), int(l * w) : int(r * w)]
    if args.keyed:
        pixels = key(pixels)
    w, h = (int(v) for v in args.size.split("x"))
    small = pixel.snap(pixels, (pixels.shape[1] / w, pixels.shape[0] / h), (0, 0))[:h, :w]
    out = palette.apply(small, PALETTE, dither=args.dither)
    if args.dither:
        out[..., 3] = small[..., 3]
    if args.cool:
        # 물속 배경에 넓게 깔린 따뜻한 색을 같은 밝기의 차가운 색으로 바꾼다 (아트 디렉션: 물속은 차가운 색).
        for warm, cold in COOL.items():
            mask = (out[..., :3] == np.array(chroma.parse_colour(warm), dtype=np.uint8)).all(axis=-1)
            out[mask, :3] = np.array(chroma.parse_colour(cold), dtype=np.uint8)
    save_rgba(out, Path(args.dst))
    print(args.dst, out.shape[1], "x", out.shape[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sprite")
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("--h", type=int, default=56)
    s.add_argument("--cell", type=float)
    s.add_argument("--hs", help="조각마다 다른 세로 크기 (쉼표로)")
    s.add_argument("--erase", action="append", default=[], help="자르기 전에 지울 영역 l,t,r,b (0~1). 여러 번")
    s.add_argument("--split", action="store_true")
    s.add_argument("--grid", help="열x행 격자로 나눈다 (조각이 서로 닿은 시트)")
    s.add_argument("--same", action="store_true")
    s.add_argument("--names")
    s.set_defaults(func=sprite)
    b = sub.add_parser("bg")
    b.add_argument("src")
    b.add_argument("dst")
    b.add_argument("--size", required=True)
    b.add_argument("--crop")
    b.add_argument("--keyed", action="store_true")
    b.add_argument("--dither", action="store_true")
    b.add_argument("--cool", action="store_true")
    b.set_defaults(func=bg)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
