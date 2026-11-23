"""육지 에셋 공용 도우미 (gfx 를 고치지 않고 여기에 둔다)."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
from PIL import Image, ImageDraw
import gfx

RAW = "assets/raw/land"


def resize_nearest(path, size) -> np.ndarray:
    """큰 배경을 1x 로 줄이고 팔레트를 입힌다."""
    im = Image.open(gfx.ROOT / path).convert("RGBA").resize(size, Image.NEAREST)
    return gfx.quantize(np.array(im))


def sprite(raw, height, work, crop=None, colours=None) -> np.ndarray:
    """마젠타 배경 그림 하나 → 크로마 → (원본 crop) → trim+세로 맞춤 → 팔레트."""
    src = raw
    if crop:
        im = Image.open(gfx.ROOT / raw).crop(crop)
        src = f"{work}/crop_{raw.split('/')[-1]}"
        (gfx.ROOT / work).mkdir(parents=True, exist_ok=True)
        im.save(gfx.ROOT / src)
    keyed = gfx.chroma(src, f"{work}/keyed")
    snapped, _ = gfx.snap(keyed, f"{work}/pixel", height=height, trim=True)
    return gfx.trim(gfx.quantize(gfx.load(snapped), colours))


def clean_specks(a: np.ndarray, min_px=6) -> np.ndarray:
    """본체에서 떨어진 작은 조각(크로마 찌꺼기)을 지운다."""
    out = a.copy()
    for c in gfx.components(a[..., 3] > 0, 1):
        if c.sum() < min_px:
            out[c] = 0
    return out


def zoom_grid(arr, path, scale=2, step=20, region=None):
    """좌표를 재려고 눈금을 그린 확대 그림."""
    if region:
        x0, y0, x1, y1 = region
        arr = arr[y0:y1, x0:x1]
    else:
        x0 = y0 = 0
    bg = np.zeros_like(arr); bg[..., :3] = (255, 0, 255); bg[..., 3] = 255
    im = Image.fromarray(np.kron(gfx.over(bg, arr), np.ones((scale, scale, 1), dtype=np.uint8)), "RGBA")
    d = ImageDraw.Draw(im)
    for x in range((-x0) % step, arr.shape[1], step):
        d.line([(x * scale, 0), (x * scale, im.size[1])], fill=(255, 255, 0, 255))
        d.text((x * scale + 1, 0), str(x + x0), fill=(255, 255, 255))
    for y in range((-y0) % step, arr.shape[0], step):
        d.line([(0, y * scale), (im.size[0], y * scale)], fill=(255, 255, 0, 255))
        d.text((0, y * scale), str(y + y0), fill=(255, 255, 255))
    p = gfx.ROOT / path; p.parent.mkdir(parents=True, exist_ok=True); im.save(p)
