"""고양이의 모든 동작 시트를 만든다. 캔버스 80x60, 발밑 가운데 (40, 59).

방법: 자세는 기준 스프라이트를 참조로 한 이미지 편집으로 받고(시트 3장), 숨쉬기·눈 깜박임·떨림·뛰기는 여기서 픽셀을 옮겨 만든다.
걷기 프레임의 머리는 기준 자세의 머리를 그대로 옮겨 얼굴이 프레임마다 달라지지 않게 한다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
import numpy as np
import gfx

CANVAS, FOOT = (80, 60), (40, 59)
NAVY = (0x2E, 0x30, 0x68)
DARK = (0x17, 0x12, 0x1B)
FUR = (0xD7, 0x99, 0x66)
HEAD_ROWS = 27  # 기준 자세에서 모자와 얼굴이 차지하는 줄 수(꼬리는 그 아래에서 시작한다)

P = {n: gfx.load(f"assets/raw/parts/cat/{n}.png") for n in ["stand", "sit", "reel", "strain", "cheer", "sad", "pick"] + [f"walk{i}" for i in range(6)]}


def is_colour(a, c):
    return (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)


def vest_x(a):
    return float(np.nonzero(is_colour(a, NAVY))[1].mean())


def head_down(a, rows=HEAD_ROWS, by=1):
    """위쪽 rows 줄(머리)을 by 만큼 내린다. 숨쉬기."""
    out = a.copy()
    head = a[:rows].copy()
    out[:by] = 0
    block = out[by:rows + by]
    m = head[..., 3] > 0
    block[m] = head[m]
    return out


def blink(a):
    """얼굴 안의 눈(어두운 색의 작은 덩어리)을 둘레 털 색으로 덮고 가운데 줄에 감은 눈 선을 긋는다."""
    out = a.copy()
    dark = is_colour(a, DARK)
    for comp in gfx.components(dark, 0):
        ys, xs = np.nonzero(comp)
        if 3 <= comp.sum() <= 14 and ys.min() >= 12 and ys.max() <= 24 and xs.max() - xs.min() <= 3 and ys.max() - ys.min() >= 1:
            ring = a[ys.min() - 1 : ys.max() + 2, xs.min() - 1 : xs.max() + 2].reshape(-1, 4)
            ring = [tuple(int(v) for v in p) for p in ring if p[3] > 0 and tuple(int(v) for v in p[:3]) != DARK]
            fill = max(set(ring), key=ring.count)
            out[comp] = fill
            mid = (ys.min() + ys.max() + 1) // 2
            out[mid, xs.min() - 1 : xs.max() + 2] = (*DARK, 255)
    return out


def paste_head(frame, base):
    """frame 의 머리 자리에 base 의 머리를 옮긴다. 가장 잘 겹치는 자리를 찾는다."""
    head = base[:HEAD_ROWS]
    best = None
    for dy in range(-2, 3):
        for dx in range(-4, 5):
            canvas = np.zeros_like(frame)
            canvas = gfx.over(canvas, head, dx, dy)
            both = (canvas[..., 3] > 0) & (frame[..., 3] > 0)
            score = ((canvas[..., :3] == frame[..., :3]).all(-1) & both).sum()
            if best is None or score > best[0]:
                best = (score, dx, dy)
    _, dx, dy = best
    out = frame.copy()
    out[: HEAD_ROWS + dy] = 0 if dy >= 0 else out[: HEAD_ROWS + dy]
    # 머리 줄은 비우고 base 머리를 놓되, 그 줄에 있던 frame 의 꼬리·팔(머리 바깥)은 되살린다
    region = frame[: HEAD_ROWS + dy].copy()
    out = gfx.over(out, head, dx, dy)
    hm = np.zeros(frame.shape[:2], dtype=bool)
    hx0, hx1 = max(0, dx), min(frame.shape[1], dx + head.shape[1])
    keep = np.ones(region.shape[:2], dtype=bool)
    keep[:, hx0:hx1] = False
    out[: region.shape[0]][keep & (region[..., 3] > 0)] = region[keep & (region[..., 3] > 0)]
    return out


def put(a, dx=0, dy=0, anchor=None):
    return gfx.place(a, CANVAS, (FOOT[0] + dx, FOOT[1] + dy), vest_x(a) if anchor is None else anchor)


stand, sit, reel, strain, cheer, sad, pick = (P[k] for k in ["stand", "sit", "reel", "strain", "cheer", "sad", "pick"])
walk = [paste_head(P[f"walk{i}"], stand) for i in range(6)]

anims = {
    "idle": ([put(stand), put(head_down(stand)), put(stand), put(blink(stand))], 4),
    "walk": ([put(f) for f in walk], 9),
    "pick": ([put(stand), put(pick), put(pick, dy=0, dx=1)], 6),
    "sit_fish": ([put(sit), put(head_down(sit)), put(sit), put(blink(sit))], 4),
    "reel": ([put(reel), put(head_down(reel)), put(sit), put(head_down(sit))], 8),
    "strain": ([put(strain), put(strain, dx=-1), put(strain), put(strain, dx=1)], 12),
    "cheer": ([put(stand), put(cheer, dy=-2), put(cheer, dy=-4), put(cheer, dy=-2)], 8),
    "sad": ([put(sad), put(head_down(sad, rows=30))], 2),
}


def rod_tip(frame, bent):
    ys, xs = np.nonzero(frame[..., 3])
    i = xs.argmax() if bent else (xs - ys).argmax()
    return [int(xs[i]), int(ys[i])]


meta = {"canvas": list(CANVAS), "foot": list(FOOT), "rod_tip": {}}
allf = []
for name, (frames, fps) in anims.items():
    gfx.write_sheet(frames, f"cat_{name}", "assets/game/chars", fps=fps)
    allf += frames
    if name in ("sit_fish", "reel", "strain"):
        meta["rod_tip"][name] = [rod_tip(f, name == "strain") for f in frames]
(gfx.ROOT / "assets/game/chars/cat.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
gfx.contact(allf, "captures/assets/cat_anims.png", scale=3, cols=8)
print(meta)
