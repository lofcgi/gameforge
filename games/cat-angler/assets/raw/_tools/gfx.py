"""에셋 후처리 공용 도구. gf post 명령을 감싸고, 격자 시트 자르기·기준점 맞추기·절차적 프레임을 맡는다.

실행: uv run -q --project <harness>/tools python assets/raw/_tools/<스크립트>.py  (게임 폴더에서)
"""
from __future__ import annotations

import json
import subprocess
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HARNESS = ROOT.parents[1] / "harness" / "tools"
PALETTE = [tuple(int(c[i : i + 2], 16) for i in (1, 3, 5)) for c in json.loads((ROOT / "design/look/palette.json").read_text())["colors"]]
PAL = np.array(PALETTE, dtype=np.int32)


def gf(*args: str) -> dict:
    out = subprocess.run(
        ["uv", "run", "-q", "--project", str(HARNESS), "gf", "--project", str(ROOT), *args],
        capture_output=True, text=True, cwd=ROOT,
    )
    line = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        raise RuntimeError(f"gf {' '.join(args)}: {out.stdout[-400:]} {out.stderr[-400:]}")
    if not data.get("ok"):
        raise RuntimeError(f"gf {' '.join(args)}: {data.get('error')}")
    return data


def load(path) -> np.ndarray:
    return np.array(Image.open(ROOT / path if not Path(path).is_absolute() else path).convert("RGBA"))


def save(arr: np.ndarray, path) -> Path:
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(p)
    return p


def quantize(arr: np.ndarray, colours: np.ndarray | None = None) -> np.ndarray:
    """알파를 0/255 로 만들고 RGB 를 팔레트의 가장 가까운 색으로 바꾼다."""
    pal = PAL if colours is None else colours
    out = arr.copy()
    rgb = out[..., :3].astype(np.int32)
    d = ((rgb[..., None, :] - pal[None, None, :, :]) ** 2).sum(-1)
    out[..., :3] = pal[d.argmin(-1)]
    a = out[..., 3] >= 128
    out[..., 3] = np.where(a, 255, 0)
    out[~a] = 0
    return out


def chroma(src: str, out_dir: str, key: str = "#FF00FF") -> str:
    return gf("post", "chroma", src, "--key", key, "--hard", "--out", out_dir)["files"][0]


def snap(src: str, out_dir: str, *, cell: float | None = None, height: int | None = None, size: str | None = None, trim: bool = False) -> tuple[str, float]:
    args = ["post", "pixel-snap", src, "--out", out_dir, "--no-preview"]
    if cell:
        args += ["--cell", f"{cell:.4f}"]
    if height:
        args += ["--height", str(height)]
    if size:
        args += ["--size", size]
    if trim:
        args += ["--trim"]
    d = gf(*args)
    return d["files"][0], d["images"][0]["cell"][0]


def bbox(arr: np.ndarray):
    ys, xs = np.nonzero(arr[..., 3])
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def trim(arr: np.ndarray) -> np.ndarray:
    b = bbox(arr)
    return arr[b[1] : b[3], b[0] : b[2]]


def components(mask: np.ndarray, reach: int = 1) -> list[np.ndarray]:
    """붙어 있는 덩어리별 불리언 마스크. reach 칸 안쪽이면 같은 덩어리로 본다."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        comp = np.zeros_like(mask, dtype=bool)
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            comp[y, x] = True
            # reach 0 은 상하좌우 4방향만 잇는다
            steps = [(-1, 0), (1, 0), (0, -1), (0, 1)] if reach == 0 else [(dy, dx) for dy in range(-reach, reach + 1) for dx in range(-reach, reach + 1)]
            for dy, dx in steps:
                if True:
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
        out.append(comp)
    return out


def slice_grid(arr: np.ndarray, cols: int, rows: int, min_px: int = 8, reach: int = 1) -> list[np.ndarray | None]:
    """1x 시트를 칸별 그림으로 나눈다. 덩어리의 무게중심이 든 칸에 그 덩어리를 통째로 준다(칸 경계를 넘는 꼬리도 따라간다)."""
    h, w = arr.shape[:2]
    comps = [c for c in components(arr[..., 3] > 0, reach) if c.sum() >= min_px]
    biggest = max(c.sum() for c in comps)
    big = [c for c in comps if c.sum() >= biggest * 0.15]
    cells: list[np.ndarray] = [np.zeros((h, w), dtype=bool) for _ in range(cols * rows)]
    if len(big) == cols * rows:
        # 큰 덩어리 수가 칸 수와 같으면 간격이 고르지 않아도 줄·열 순서로 짝짓는다. 작은 조각은 가장 가까운 큰 덩어리에 붙인다.
        cents = [(np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()) for c in big]
        order = sorted(range(len(big)), key=lambda i: (min(rows - 1, int(cents[i][0] / (h / rows))), cents[i][1]))
        for slot, i in enumerate(order):
            cells[slot] |= big[i]
        for c in comps:
            if c.sum() < biggest * 0.15:
                cy, cx = np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()
                j = min(range(len(order)), key=lambda k: (cents[order[k]][0] - cy) ** 2 + (cents[order[k]][1] - cx) ** 2)
                cells[j] |= c
    else:
        for comp in comps:
            ys, xs = np.nonzero(comp)
            c = min(cols - 1, int(xs.mean() / (w / cols)))
            r = min(rows - 1, int(ys.mean() / (h / rows)))
            cells[r * cols + c] |= comp
    out = []
    for m in cells:
        if not m.any():
            out.append(None)
            continue
        a = arr.copy()
        a[~m] = 0
        out.append(trim(a))
    return out


def split_full(keyed_path: str, cols: int, rows: int) -> list[np.ndarray | None]:
    """원본 해상도의 시트를 칸별 그림으로 나눈다. 1x 로 줄인 뒤에는 이웃 그림이 붙을 수 있어 줄이기 전에 가른다."""
    a = load(keyed_path)
    h, w = a.shape[:2]
    small = a[::4, ::4].copy()
    small[..., 0] = 0
    idx = np.arange(small.shape[0] * small.shape[1]).reshape(small.shape[:2])
    # 조각의 원래 자리를 따라가려고 R·G·B 대신 위치 번호를 실어 보낸다
    tag = np.zeros(small.shape[:2] + (4,), dtype=np.int64)
    tag[..., 0] = idx
    tag[..., 3] = small[..., 3]
    out = []
    for part_mask in _grid_masks(small[..., 3] > 0, cols, rows):
        if part_mask is None:
            out.append(None)
            continue
        big = np.kron(part_mask, np.ones((4, 4), dtype=bool))[:h, :w]
        if big.shape != (h, w):
            full = np.zeros((h, w), dtype=bool)
            full[: big.shape[0], : big.shape[1]] = big
            big = full
        part = a.copy()
        part[~big] = 0
        out.append(trim(part))
    return out


def _grid_masks(mask: np.ndarray, cols: int, rows: int, min_px: int = 30):
    h, w = mask.shape
    comps = [c for c in components(mask, 1) if c.sum() >= min_px]
    biggest = max(c.sum() for c in comps)
    big = [c for c in comps if c.sum() >= biggest * 0.15]
    cells = [np.zeros((h, w), dtype=bool) for _ in range(cols * rows)]
    cents = [(np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()) for c in big]
    if len(big) == cols * rows:
        order = sorted(range(len(big)), key=lambda i: (min(rows - 1, int(cents[i][0] / (h / rows))), cents[i][1]))
    else:
        order = None
    for c in comps:
        cy, cx = np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()
        if order is not None:
            j = min(range(len(order)), key=lambda k: (cents[order[k]][0] - cy) ** 2 + (cents[order[k]][1] - cx) ** 2)
        else:
            j = min(rows - 1, int(cy / (h / rows))) * cols + min(cols - 1, int(cx / (w / cols)))
        cells[j] |= c
    return [m if m.any() else None for m in cells]


def sheet_to_frames(raw: str, cols: int, rows: int, *, ref_height: int, ref_index: int = 0, work: str, key: str = "#FF00FF", cell: float | None = None, colours: np.ndarray | None = None) -> list[np.ndarray | None]:
    """원본 격자 시트 → 크로마 → 칸별로 가름 → 기준 칸의 세로가 ref_height 가 되는 한 가지 칸 크기로 모두 맞춤 → 팔레트."""
    keyed = chroma(raw, f"{work}/keyed", key)
    parts = split_full(keyed, cols, rows)
    cell = cell or parts[ref_index].shape[0] / ref_height
    out = []
    for i, p in enumerate(parts):
        if p is None:
            out.append(None)
            continue
        f = save(p, f"{work}/parts/p{i:02d}.png")
        snapped, _ = snap(str(f.relative_to(ROOT)), f"{work}/pixel", cell=cell)
        out.append(trim(quantize(load(snapped), colours)))
    return out


def place(sprite: np.ndarray, canvas: tuple[int, int], foot: tuple[int, int], anchor_x: float | None = None) -> np.ndarray:
    """sprite 의 아래 끝을 foot.y 에, anchor_x(스프라이트 안의 x, 기본은 가운데)를 foot.x 에 놓는다."""
    w, h = canvas
    out = np.zeros((h, w, 4), dtype=np.uint8)
    sh, sw = sprite.shape[:2]
    ax = sw / 2 if anchor_x is None else anchor_x
    x0 = int(round(foot[0] - ax))
    y0 = foot[1] - sh
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    cw = min(sw - sx0, w - dx0)
    ch = min(sh - sy0, h - dy0)
    if cw > 0 and ch > 0:
        out[dy0 : dy0 + ch, dx0 : dx0 + cw] = sprite[sy0 : sy0 + ch, sx0 : sx0 + cw]
    return out


def shift(arr: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(arr)
    h, w = arr.shape[:2]
    src = arr[max(0, -dy) : h - max(0, dy), max(0, -dx) : w - max(0, dx)]
    out[max(0, dy) : max(0, dy) + src.shape[0], max(0, dx) : max(0, dx) + src.shape[1]] = src
    return out


def over(dst: np.ndarray, src: np.ndarray, x: int = 0, y: int = 0) -> np.ndarray:
    """알파가 0/255 인 src 를 dst 위 (x, y) 에 올린다. 범위를 벗어난 부분은 자른다."""
    out = dst.copy()
    h, w = dst.shape[:2]
    sh, sw = src.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(w, x + sw), min(h, y + sh)
    if x1 <= x0 or y1 <= y0:
        return out
    s = src[y0 - y : y1 - y, x0 - x : x1 - x]
    m = s[..., 3] > 0
    out[y0:y1, x0:x1][m] = s[m]
    return out


def write_sheet(frames: list[np.ndarray], name: str, out_dir: str, fps: int = 8, loop: bool = True) -> None:
    """프레임들을 gf post sheet 로 시트 PNG + JSON + .tres 로 만든다."""
    tmp = ROOT / "assets/raw/frames_final" / name
    if tmp.exists():
        for f in tmp.glob("*.png"):
            f.unlink()
    for i, f in enumerate(frames):
        save(f, tmp / f"{name}_{i:02d}.png")
    args = ["post", "sheet", str(tmp.relative_to(ROOT)), "--name", name, "--fps", str(fps), "--out", out_dir, "--columns", str(len(frames))]
    if not loop:
        args.append("--no-loop")
    gf(*args)


def contact(frames: list[np.ndarray], path: str, scale: int = 4, bg=((233, 243, 226), (93, 197, 203)), cols: int | None = None) -> None:
    """프레임들을 밝은 배경과 물색 배경 위에 나란히 올린 확인용 그림(위 1x, 아래 확대)."""
    cols = cols or len(frames)
    rows = (len(frames) + cols - 1) // cols
    fw = max(f.shape[1] for f in frames) + 2
    fh = max(f.shape[0] for f in frames) + 2
    W, H = cols * fw, rows * fh
    strips = []
    for colour in bg:
        s = np.zeros((H, W, 4), dtype=np.uint8)
        s[..., :3] = colour
        s[..., 3] = 255
        for i, f in enumerate(frames):
            s = over(s, f, (i % cols) * fw + 1, (i // cols) * fh + 1)
        strips.append(s)
    one = np.concatenate(strips, axis=0)
    big = np.kron(one, np.ones((scale, scale, 1), dtype=np.uint8))
    pad = np.zeros((one.shape[0], big.shape[1], 4), dtype=np.uint8)
    pad[..., 3] = 255
    pad[..., :3] = 40
    pad[:, : one.shape[1]] = one
    save(np.concatenate([pad, big], axis=0), path)
