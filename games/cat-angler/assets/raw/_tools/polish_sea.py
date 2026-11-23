"""다듬기 단계의 바다 장식: 바닥 장식(해초·산호·바위·빛나는 것), 물속 먼 윤곽, 빛줄기, 배경 잔고기, 해파리.

실행: uv run -q --project <harness>/tools python assets/raw/_tools/polish_sea.py  (게임 폴더에서)
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
from PIL import Image
import gfx

SEA = "assets/game/sea"
WORK = "assets/raw/polish/work"


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def deco():
    shallow = ["weed_1", "weed_2", "weed_3", "coral_1", "coral_2", "rock_1", "rock_2", "shell_1"]
    deep = ["kelp_1", "kelp_2", "rock_3", "rock_4", "glow_1", "glow_2", "pearl_1", "lantern_1"]
    made = []
    for raw, names, ref_h in [("assets/raw/polish/deco_shallow.png", shallow, 17), ("assets/raw/polish/deco_deep.png", deep, 40)]:
        frames = gfx.sheet_to_frames(raw, 4, 2, ref_height=ref_h, ref_index=0, work=f"{WORK}/{names[0]}")
        for name, frame in zip(names, frames):
            gfx.save(frame, f"{SEA}/{name}.png")
            made.append(frame)
            print(name, frame.shape[1], frame.shape[0])
    gfx.contact(made, "captures/assets/sea_deco.png", scale=3, bg=((84, 169, 167), (46, 48, 104)), cols=8)


def far_shapes():
    """단색 윤곽 띠 → 640 너비. 구간마다 그 깊이의 물색보다 한 단계 짙은(심해는 옅은) 한 가지 색으로 칠한다."""
    src = np.array(Image.open("assets/raw/polish/under_far.png").convert("RGB")).astype(int)
    magenta = (src[..., 0] > 150) & (src[..., 1] < 110) & (src[..., 2] > 150)
    solid = (~magenta).astype(np.uint8) * 255
    # 아래쪽의 꽉 찬 바닥은 12px 만 남긴다(게임의 바닥 그림이 그 위를 덮는다).
    w, h = 640, round(640 * solid.shape[0] / solid.shape[1])
    small = np.array(Image.fromarray(solid).resize((w, h), Image.BOX)) >= 128
    full_rows = np.nonzero(small.all(axis=1))[0]
    cut = min(h, int(full_rows.min()) + 12) if len(full_rows) else h
    small = small[:cut]
    top = int(np.nonzero(small.any(axis=1))[0].min())
    small = small[top:]
    # deco_far: 바닥에 앉는 가까운 겹. deco_far2: 수면 가까이에서도 보이는 먼 겹(짙은 물 위에 한 단계 옅은 색으로 아득하게 비친다).
    for name, zone, colour, flip, roll in [("deco_far", "shallow", "#28706F", False, 0), ("deco_far", "open", "#2E3068", True, 0),
            ("deco_far", "deep", "#2E3068", False, 230), ("deco_far2", "shallow", "#426A96", True, 300), ("deco_far2", "open", "#426A96", False, 410),
            ("deco_far2", "deep", "#2E3068", True, 120)]:
        mask = small[:, ::-1] if flip else small
        mask = np.roll(mask, roll, axis=1)
        out = np.zeros(mask.shape + (4,), dtype=np.uint8)
        out[mask] = (*rgb(colour), 255)
        gfx.save(out, f"{SEA}/{name}_{zone}.png")
        print("deco_far", zone, out.shape[1], out.shape[0])


def ray():
    """비스듬한 빛줄기: 한 가지 옅은 색의 띠. 가장자리는 계단, 아래 끝은 성긴 점으로 흩어진다. 게임이 옅게 겹쳐 그린다."""
    w, h, width = 100, 150, 26
    out = np.zeros((h, w, 4), dtype=np.uint8)
    colour = rgb("#E9F3E2")
    for y in range(h):
        t = y / h
        x0 = int(58 - (y // 2 * 2) * 0.36)
        span = int(width * (1 + t * 0.5))
        for dx in range(span):
            x = x0 + dx
            on = True
            if t > 0.8:
                on = (x + y) % 2 == 0
            if t > 0.92:
                on = x % 4 == y % 4
            if on and 0 <= x < w:
                out[y, x] = (*colour, 255)
    gfx.save(out, f"{SEA}/ray.png")


def minnow():
    """배경 잔고기: 흰 윤곽 두 프레임(색은 게임이 구간에 맞춰 입힌다)."""
    rows = [
        ["#....#####...", "##..#######..", "############.", ".############", "############.", "##..#######..", "#....#####..."],
        [".....#####...", "#...#######..", "############.", ".############", "############.", "#...#######..", ".....#####..."],
    ]
    frames = []
    for grid in rows:
        f = np.zeros((7, 13, 4), dtype=np.uint8)
        for y, line in enumerate(grid):
            for x, ch in enumerate(line):
                if ch == "#":
                    f[y, x] = (255, 255, 255, 255)
        frames.append(f)
    gfx.write_sheet(frames, "minnow", SEA, fps=4)


def jelly():
    a = gfx.load("assets/game/cutscenes/props/p_jelly_a.png")
    b = gfx.load("assets/game/cutscenes/props/p_jelly_b.png")
    w, h = max(a.shape[1], b.shape[1]), max(a.shape[0], b.shape[0])
    frames = [gfx.place(f, (w, h + 2), (w // 2, h + (0 if i == 0 else 2))) for i, f in enumerate([a, b])]
    gfx.write_sheet(frames, "jelly", SEA, fps=2)


def under():
    """물속 겹: 깊어질수록 짙어지는 색 띠. 두 배로 당겨 보는 화면(세로 180)에 띠가 서너 개 걸리게 간격을 좁혔다.
    경계는 물결선이고 그 위아래 2px 만 바둑판으로 섞는다. 빛줄기는 굽지 않는다(게임이 sea/ray.png 를 움직인다)."""
    import math
    table = {
        "shallow": [(0, "#76D7D9"), (8, "#5DC5CB"), (20, "#54A9A7"), (30, "#468DB4"), (58, "#426A96"), (92, "#2E3068")],
        "open": [(0, "#5DC5CB"), (8, "#54A9A7"), (18, "#468DB4"), (44, "#426A96"), (76, "#2E3068"), (300, "#1B2139")],
        "deep": [(0, "#468DB4"), (12, "#426A96"), (30, "#2E3068"), (120, "#1B2139")],
    }
    w, h = 640, 360
    xs = np.arange(w)
    for zone, stops in table.items():
        out = np.zeros((h, w, 4), dtype=np.uint8)
        out[..., :3] = rgb(stops[0][1]); out[..., 3] = 255
        for i, (y0, colour) in enumerate(stops[1:], 1):
            ph = len(zone) * 1.3 + i * 2.1
            amp = 3 + i
            wave = amp * np.sin(2 * math.pi * 2 * xs / w + ph) + amp * 0.5 * np.sin(2 * math.pi * 5 * xs / w + ph * 2)
            edge = (y0 + wave).round().astype(int)
            for x in range(w):
                e = max(1, edge[x])
                out[e + 2:, x, :3] = rgb(colour)
                for y in range(e - 2, e + 2):
                    if 0 <= y < h and (x // 2 + y // 2) % 2 == 0:
                        out[y, x, :3] = rgb(colour)
        gfx.save(out, f"{SEA}/under_{zone}.png")


def flatten_far():
    """먼 산의 얼룩(생성물의 잔무늬)을 지운다: 둘레 5x5 에서 가장 많은 색으로 바꾸기를 두 번."""
    for zone in ["shallow"]:
        a = gfx.load(f"{SEA}/far_{zone}.png")
        for _ in range(2):
            src = a.copy()
            h, w = src.shape[:2]
            keys = (src[..., 0].astype(np.int64) << 24) | (src[..., 1].astype(np.int64) << 16) | (src[..., 2].astype(np.int64) << 8) | src[..., 3]
            pad = np.pad(keys, 2, mode="edge")
            stack = np.stack([pad[dy:dy + h, dx:dx + w] for dy in range(5) for dx in range(5)], axis=-1)
            stack.sort(axis=-1)
            best = stack[..., 0].copy(); best_n = np.zeros((h, w), dtype=int)
            run_val = stack[..., 0].copy(); run_n = np.ones((h, w), dtype=int)
            for k in range(1, 25):
                same = stack[..., k] == run_val
                run_n = np.where(same, run_n + 1, 1)
                run_val = stack[..., k]
                better = run_n > best_n
                best = np.where(better, run_val, best); best_n = np.where(better, run_n, best_n)
            a = np.stack([(best >> 24) & 255, (best >> 16) & 255, (best >> 8) & 255, best & 255], axis=-1).astype(np.uint8)
        gfx.save(a, f"{SEA}/far_{zone}.png")


def anchovy():
    """멸치의 등을 한 단계 짙게 해 밝은 물색에서 묻히지 않게 한다(몸통 연두 가운데 위쪽 절반)."""
    a = gfx.load("assets/game/fish/anchovy_swim.png")
    body, back = rgb("#96B89D"), rgb("#439083")
    for x in range(a.shape[1]):
        ys = np.nonzero(a[:, x, 3])[0]
        if len(ys) == 0:
            continue
        mid = (ys.min() + ys.max()) / 2
        for y in ys:
            if tuple(a[y, x, :3]) == body and y <= mid:
                a[y, x, :3] = back
    gfx.save(a, "assets/game/fish/anchovy_swim.png")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["deco", "far_shapes", "ray", "minnow", "jelly"]:
        globals()[name]()
