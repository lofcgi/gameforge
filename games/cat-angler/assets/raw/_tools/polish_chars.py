"""다듬기 단계의 캐릭터·소품: 가게 주인의 말하는 입, 곧게 편 갈치·산갈치의 헤엄, 단순한 상자, 섬꽃 아이콘.

실행: uv run -q --project <harness>/tools python assets/raw/_tools/polish_chars.py [keepers longfish crate flower]  (게임 폴더에서)
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import math
import numpy as np
import gfx
from land_build import IDS, canvas, clean_specks, head_shift

WORK = "assets/raw/polish/work"
MOUTH = {"market": (28, 20, 39, 28), "yard": (30, 19, 42, 30)}


def keepers():
    """입을 벌린 그림(기준 시트를 최소한으로 편집해 받은 것)에서 입 둘레만 기준 프레임에 옮겨 붙인다. 나머지 픽셀은 대기 동작과 같다."""
    frames = gfx.sheet_to_frames("assets/raw/polish/keepers_talk.png", 2, 2, ref_height=50, work=f"{WORK}/keepers_talk")
    shown = []
    for kid, sp in zip(IDS, frames):
        base = canvas(gfx.load(f"assets/raw/parts/land/keeper_{kid}.png"), (48, 56))
        new = canvas(clean_specks(sp), (48, 56))
        best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                moved = gfx.shift(new, dx, dy)
                same = ((moved == base).all(-1) & (base[..., 3] > 0)).sum()
                if best is None or same > best[0]:
                    best = (same, dx, dy, moved)
        _, dx, dy, moved = best
        ys = np.nonzero(base[..., 3].any(axis=1))[0]
        top, height = int(ys.min()), int(ys.max() - ys.min() + 1)
        head = np.zeros(base.shape[:2], dtype=bool)
        head[top + int(height * 0.12):top + int(height * 0.5)] = True
        diff = (moved != base).any(-1) & head
        comps = sorted(gfx.components(diff, 2), key=lambda c: -c.sum())
        if not comps:
            raise RuntimeError(f"{kid}: 입이 달라진 곳을 찾지 못했다")
        ys, xs = np.nonzero(comps[0])
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        if kid in MOUTH:
            # 편집본의 머리 음영이 통째로 달라진 주인은 입 둘레만 손으로 정한 상자로 옮긴다(머리 전체를 옮기면 말할 때 얼굴이 깜박인다).
            x0, y0, x1, y1 = MOUTH[kid]
        opened = base.copy()
        opened[y0:y1, x0:x1] = moved[y0:y1, x0:x1]
        print(kid, "맞춤", (dx, dy), "입 상자", (int(x0), int(y0), int(x1), int(y1)), "다른 픽셀", int(comps[0].sum()))
        rows = top + int(height * 0.55)
        talk = [base, opened, head_shift(base, rows, -1), opened]
        gfx.write_sheet(talk, f"keeper_{kid}_talk", "assets/game/chars", fps=8)
        shown += talk
    gfx.contact(shown, "captures/assets/keepers_talk.png", scale=4, cols=4, bg=((233, 243, 226), (229, 221, 200)))


def wave(sprite, frames, amp, waves):
    """곧은 몸을 열마다 위아래로 밀어 물결치게 한다. 머리(오른쪽)는 거의 움직이지 않고 꼬리로 갈수록 크게 흔들린다."""
    h, w = sprite.shape[:2]
    out = []
    for i in range(frames):
        f = np.zeros((h + 2 * amp, w, 4), dtype=np.uint8)
        for x in range(w):
            t = 1.0 - x / (w - 1)
            dy = int(round(amp * (0.15 + 0.85 * t) * math.sin(2 * math.pi * (waves * t - i / frames))))
            col = sprite[:, x]
            f[amp + dy:amp + dy + h, x] = col
        out.append(f)
    return out


def longfish():
    made = []
    for fid, index, height, amp, waves in [("hairtail", 0, 12, 4, 1.6), ("oarfish", 1, 36, 5, 1.3)]:
        frames = gfx.sheet_to_frames("assets/raw/polish/longfish.png", 1, 2, ref_height=height, ref_index=index, work=f"{WORK}/longfish_{fid}")
        sprite = frames[index]
        print(fid, sprite.shape[1], sprite.shape[0])
        swim = wave(sprite, 6, amp, waves)
        gfx.write_sheet(swim, f"{fid}_swim", "assets/game/fish", fps=8)
        made += swim
    gfx.contact(made, "captures/assets/longfish_swim.png", scale=2, cols=3, bg=((66, 106, 150), (46, 48, 104)))


def crate():
    keyed = gfx.chroma("assets/raw/polish/crate.png", f"{WORK}/crate/keyed")
    snapped, _ = gfx.snap(keyed, f"{WORK}/crate/pixel", height=20, trim=True)
    a = gfx.trim(gfx.quantize(gfx.load(snapped)))
    gfx.save(a, "assets/game/sea/crate.png")
    print("crate", a.shape[1], a.shape[0])


def flower():
    """섬꽃 아이콘을 땅에 난 모습(초승달 모양 꽃)에서 딴다: 꽃송이 쪽 16x16."""
    plant = gfx.load("assets/game/items/flower_plant.png")
    ys, xs = np.nonzero(plant[..., 3])
    y0 = int(ys.min())
    cx = int(round(xs[ys < y0 + 12].mean()))
    x0 = max(0, min(plant.shape[1] - 16, cx - 8))
    icon = plant[y0:y0 + 16, x0:x0 + 16].copy()
    gfx.save(gfx.place(gfx.trim(icon), (16, 16), (8, 16)), "assets/game/items/flower.png")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["keepers", "longfish", "crate", "flower"]:
        globals()[name]()
