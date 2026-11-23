"""바다 쪽 에셋 공용: 마젠타 키, 조각 나누기, 크기 맞춤."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
import gfx


def key_magenta(arr: np.ndarray) -> np.ndarray:
    """마젠타 계열(밝기가 달라도)을 투명으로. 모델이 칸마다 배경 밝기를 다르게 칠하거나 옅은 칸 선을 그을 때 쓴다."""
    r, g, b = (arr[..., i].astype(np.int32) for i in range(3))
    bg = (r > 150) & (b > 150) & (g < np.minimum(r, b) * 0.62)
    out = arr.copy()
    out[bg] = 0
    out[..., 3] = np.where(bg, 0, 255)
    return out


def parts_of(raw: str, min_frac: float = 0.02) -> list[np.ndarray]:
    """원본을 키잉하고 큰 덩어리별로 나눈다. 줄(위→아래), 그 안에서 왼쪽→오른쪽 순서."""
    a = key_magenta(gfx.load(raw))
    h, w = a.shape[:2]
    small = a[::4, ::4, 3] > 0
    comps = [c for c in gfx.components(small, 1) if c.sum() >= 20]
    biggest = max(c.sum() for c in comps)
    big = [c for c in comps if c.sum() >= biggest * min_frac]
    cents = [(np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()) for c in big]
    masks = [c.copy() for c in big]
    for c in comps:
        if c.sum() < biggest * min_frac:
            cy, cx = np.nonzero(c)[0].mean(), np.nonzero(c)[1].mean()
            j = min(range(len(big)), key=lambda k: (cents[k][0] - cy) ** 2 + (cents[k][1] - cx) ** 2)
            masks[j] |= c
    boxes = [gfx.bbox(np.dstack([m] * 4).astype(np.uint8)) for m in masks]
    order = sorted(range(len(big)), key=lambda i: (boxes[i][1], boxes[i][0]))
    # 줄 묶기: 세로로 겹치는 것끼리 한 줄
    rows, cur = [], []
    for i in order:
        if cur and boxes[i][1] > max(boxes[j][3] for j in cur) - 4:
            rows.append(cur); cur = []
        cur.append(i)
    rows.append(cur)
    out = []
    for row in rows:
        for i in sorted(row, key=lambda j: boxes[j][0]):
            m = np.kron(masks[i], np.ones((4, 4), dtype=bool))
            full = np.zeros((h, w), dtype=bool)
            full[: min(h, m.shape[0]), : min(w, m.shape[1])] = m[:h, :w]
            p = a.copy(); p[~full] = 0
            out.append(gfx.trim(p))
    return out


def to_size(part: np.ndarray, *, width: int | None = None, height: int | None = None, work: str, name: str, colours=None) -> np.ndarray:
    """조각을 정한 가로(또는 세로)의 1x 로 줄이고 팔레트를 입힌다."""
    ph, pw = part.shape[:2]
    if height is None:
        height = max(1, round(width * ph / pw))
    f = gfx.save(part, f"{work}/{name}.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{work}/pixel", height=height, trim=True)
    return gfx.trim(gfx.quantize(gfx.load(snapped), colours))


def hexes(*cs):
    return np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in cs], dtype=np.int32)


COOL = hexes("#17121B", "#1B2139", "#2E3068", "#194A50", "#28706F", "#546166", "#426A96", "#439083", "#468DB4", "#799088", "#54A9A7", "#7BAEB9", "#5DC5CB", "#96B89D", "#76D7D9", "#B8D0BF", "#BAEADC", "#E5DDC8", "#E9F3E2")
