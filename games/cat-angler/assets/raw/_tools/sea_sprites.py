"""배, 물고기, 소품, 장소, 먼·중간 배경, 바닥 띠를 원본에서 만든다."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json, math
import numpy as np
import gfx
from sea_lib import parts_of, to_size, key_magenta, COOL, hexes

FAR_SOFT = hexes("#799088", "#7BAEB9", "#96B89D", "#B8D0BF", "#BAEADC", "#E5DDC8", "#E9F3E2")
# 섬: 회색을 빼서 풀밭이 회색으로 죽지 않게 한다
LAND = hexes("#17121B", "#1B2139", "#194A50", "#5E342B", "#28706F", "#8C533C", "#439083", "#B4774F", "#54A9A7", "#D79966", "#96B89D", "#DFB68B", "#B8D0BF", "#E5DDC8", "#E9F3E2")

W = "assets/raw/work/sea"
SEA = "assets/game/sea"
checks = {}

# --- 배 ---
for name, width in [("boat1", 120), ("boat2", 168), ("boat3", 224)]:
    p = parts_of(f"assets/raw/sea/{name}.png")[0]
    a = to_size(p, width=width, work=W, name=name)
    gfx.save(a, f"assets/game/boats/{name}.png")
    checks[name] = a
    print(name, a.shape[1], a.shape[0])

# --- 물고기 ---
# (원본 시트, 조각 번호) → 가로 크기. 헤엄은 꼬리 쪽 열을 위아래로 밀어 만든다(절차적).
FISH = {
    "anchovy": ("fishC", 0, 30), "scad": ("fishC", 1, 38), "flounder": ("fishC", 2, 48),
    "mackerel": ("fishA", 3, 44), "wrasse": ("fishA", 4, 36), "rockfish": ("fishA", 5, 46),
    "bream": ("fishB", 0, 50), "amberjack": ("fishB", 1, 72), "moray": ("fishC", 3, 76),
    "hairtail": ("fishB", 4, 72), "angler": ("fishB", 5, 60), "oarfish": ("fishB", 6, 96),
    "legend": ("legend", 0, 176),
}
sheets = {k: parts_of(f"assets/raw/sea/{k}.png") for k in ["fishA", "fishB", "fishC", "legend"]}
print({k: len(v) for k, v in sheets.items()})


def swim(a: np.ndarray, amp: int) -> list[np.ndarray]:
    """오른쪽을 보는 물고기의 꼬리(왼쪽 45%)를 열 단위로 위아래로 민다. 4프레임: 가운데, 위, 가운데, 아래."""
    h, w = a.shape[:2]
    pad = amp + 1
    frames = []
    for phase in (0, 1, 0, -1):
        f = np.zeros((h + pad * 2, w, 4), dtype=np.uint8)
        for x in range(w):
            t = max(0.0, 1 - x / (w * 0.45))
            dy = int(round(phase * amp * t * t)) if phase else 0
            # 가운데 프레임 둘을 다르게: 두 번째는 몸통이 1px 눌린 듯 꼬리 끝만 반 칸 늦게 따라온다
            f[pad + dy : pad + dy + h, x] = a[:, x]
        frames.append(f)
    return frames


def shadow(a: np.ndarray) -> np.ndarray:
    """실루엣판. 심해의 물색(#17121B~#1B2139)보다 한 단계 밝은 남보라 몸에 테두리만 푸르게 남겨 어둠 속에서도 형체가 읽히게 한다."""
    out = a.copy()
    m = a[..., 3] > 0
    pad = np.pad(m, 1)
    edge = m & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    out[m, :3] = (0x2E, 0x30, 0x68)
    out[edge, :3] = (0x42, 0x6A, 0x96)
    return out


fish_checks = []
for fid, (sheet, idx, width) in FISH.items():
    part = sheets[sheet][idx]
    a = to_size(part, width=width, work=W, name=fid, colours=COOL)
    amp = 1 if width <= 44 else (2 if width < 120 else 4)
    frames = swim(a, amp)
    gfx.write_sheet(frames, f"{fid}_swim", "assets/game/fish", fps=6)
    # 도감 그림: 같은 원본을 88x56 안에 들어가는 가장 큰 크기로
    ph, pw = part.shape[:2]
    cw = min(88, int(56 * pw / ph))
    card = to_size(part, width=cw, work=W, name=fid + "_card", colours=COOL)
    gfx.save(gfx.place(card, (96, 64), (48, 32 + card.shape[0] // 2)), f"assets/game/fish/{fid}_card.png")
    if fid == "legend":
        gfx.write_sheet([shadow(f) for f in frames], "legend_shadow_swim", "assets/game/fish", fps=6)
        gfx.contact(frames + [shadow(frames[0])], "captures/assets/fish_legend.png", scale=2, cols=3, bg=((0x2E, 0x30, 0x68), (0x46, 0x8D, 0xB4)))
    else:
        fish_checks.append(frames[1])
    print(fid, a.shape[1], a.shape[0])
gfx.contact(fish_checks, "captures/assets/fish_all.png", scale=3, cols=6, bg=((0x5D, 0xC5, 0xCB), (0x2E, 0x30, 0x68)))

# --- 소품: 상자, 병, 바늘, 갈매기 3자세 ---
pp = parts_of("assets/raw/sea/props.png")
print("props", len(pp))
crate = to_size(pp[0], width=22, work=W, name="crate"); gfx.save(crate, f"{SEA}/crate.png")
bottle = to_size(pp[1], width=16, work=W, name="bottle"); gfx.save(bottle, f"{SEA}/bottle.png")
hook = to_size(pp[2], height=10, work=W, name="hook"); gfx.save(hook, f"{SEA}/hook.png")
birds = [to_size(pp[i], width=w, work=W, name=f"bird{i}") for i, w in ((3, 16), (4, 20), (5, 18))]
bf = [gfx.place(b, (24, 22), (12, 11 + b.shape[0] // 2)) for b in birds]
gfx.write_sheet([bf[0], bf[1], bf[2], bf[1]], "bird", SEA, fps=6)
crest = to_size(parts_of("assets/raw/sea/crest.png")[0], width=64, work=W, name="crest"); gfx.save(crest, f"{SEA}/wave_crest.png")
gfx.contact([crate, bottle, hook, crest] + bf, "captures/assets/sea_props.png", scale=4, cols=7)

# --- 장소 ---
place_checks = []
for name, width in [("reef", 240), ("wreck", 256), ("pavilion", 192), ("island_far", 320)]:
    p = parts_of(f"assets/raw/sea/{name}.png", min_frac=0.3)[0]
    a = to_size(p, width=width, work=W, name=name, colours=LAND if name == "island_far" else COOL)
    gfx.save(a, f"{SEA}/{name}.png"); place_checks.append(a); print(name, a.shape[1], a.shape[0])
for i, p in enumerate(parts_of("assets/raw/sea/ruins.png", min_frac=0.2)[:3]):
    a = to_size(p, height=96 if i < 2 else 64, work=W, name=f"ruin{i}", colours=COOL)
    gfx.save(a, f"{SEA}/ruin_{i + 1}.png"); place_checks.append(a); print("ruin", i + 1, a.shape[1], a.shape[0])
gfx.contact(place_checks, "captures/assets/sea_places.png", scale=1, cols=4, bg=((0x46, 0x8D, 0xB4), (0x2E, 0x30, 0x68)))

# --- 중간 배경: 섬 세 개를 따로 줄여 640 너비에 띄엄띄엄 놓는다(끝이 비어 있어 그대로 이어진다) ---
for zone, hs in [("shallow", 66), ("open", 78), ("deep", 84)]:
    ps = parts_of(f"assets/raw/sea/mid_{zone}.png", min_frac=0.15)[:3]
    canvas = np.zeros((88, 640, 4), dtype=np.uint8)
    for p, x, k in zip(ps, (90, 330, 540), (1.0, 0.8, 0.9)):
        a = to_size(p, height=int(hs * k), work=W, name=f"mid_{zone}_{x}", colours=None if zone == "shallow" else COOL)
        canvas = gfx.over(canvas, a, x - a.shape[1] // 2, 88 - a.shape[0])
    gfx.save(canvas, f"{SEA}/mid_{zone}.png")

def smooth(a):
    """3x3 안에서 가장 많은 색으로 바꾼다. 모델이 넣은 잔 얼룩을 지워 색 면으로 만든다."""
    h, w = a.shape[:2]
    out = a.copy()
    key = (a[..., 0].astype(np.int64) << 24) | (a[..., 1].astype(np.int64) << 16) | (a[..., 2].astype(np.int64) << 8) | a[..., 3]
    pad = np.pad(key, 1, mode="edge")
    stack = np.stack([pad[dy:dy + h, dx:dx + w] for dy in range(3) for dx in range(3)], -1)
    for y in range(h):
        for x in range(w):
            vals, counts = np.unique(stack[y, x], return_counts=True)
            v = int(vals[counts.argmax()])
            if counts.max() >= 5:
                out[y, x] = ((v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255)
    return out


# --- 먼 배경: 640x160 으로 줄이고 좌우를 뒤집어 붙여 1280 너비로 이어지게 한다 ---
from PIL import Image
for zone in ["shallow", "open", "deep"]:
    a = key_magenta(gfx.load(f"assets/raw/sea/far_{zone}.png"))
    f = gfx.save(a, f"{W}/far_{zone}.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{W}/pixel", size="640x160")
    # 얕은 바다의 먼 산은 어두운 외곽선 없이 옅은 색 덩어리로만 둔다(한쪽에만 남은 검은 선이 지저분했다)
    q = gfx.quantize(gfx.load(snapped), FAR_SOFT if zone == "shallow" else COOL)
    b = gfx.bbox(q); q = q[b[1]:b[3]]
    if zone == "shallow":
        q = smooth(smooth(q))
    mirrored = q[:, ::-1].copy()
    if zone == "deep":
        # 달은 하나만: 뒤집은 쪽에서는 달이 있는 자리(밝은 크림색 덩어리)를 지운다
        cream = (mirrored[..., :3].sum(-1) > 620) & (mirrored[..., 3] > 0)
        for c in gfx.components(cream, 1):
            ys, xs = np.nonzero(c)
            if 20 <= c.sum() <= 200 and xs.max() - xs.min() < 16:
                mirrored[c] = 0
    gfx.save(np.concatenate([q, mirrored], axis=1), f"{SEA}/far_{zone}.png")
    print("far", zone, q.shape)

# --- 바닥 띠: 높이 64, 윗선을 위에서 10px 근처에 맞추고 좌우를 뒤집어 붙인다 ---
def bed(zone, crop, width):
    a = key_magenta(gfx.load(f"assets/raw/sea/bed_{zone}.png"))
    h, w = a.shape[:2]
    a = a[:, int(w * crop[0]) : int(w * crop[1])]
    solid = (a[..., 3] > 0).mean(1)
    top = int(np.argmax(solid > 0.9))          # 바닥이 꽉 차기 시작하는 줄
    cell = (h - top) / 54.0                    # 그 아래를 54px 로
    y0 = max(0, int(top - 10 * cell))
    a = a[y0:]
    f = gfx.save(a, f"{W}/bed_{zone}.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{W}/pixel", size=f"{width}x64")
    q = gfx.quantize(gfx.load(snapped), None if zone == "shallow" else COOL)
    # 맨 윗줄 16px 아래는 빈틈없이 채운다
    for x in range(q.shape[1]):
        col = q[:, x]
        op = np.nonzero(col[16:, 3])[0]
        if len(op) and (col[16:, 3] == 0).any():
            first = 16 + op[0]
            col[16:first] = col[first]
    out = np.concatenate([q, q[:, ::-1]], axis=1)
    gfx.save(out, f"{SEA}/bed_{zone}.png")
    return out

beds = [bed("shallow", (0, 1), 512), bed("open", (0.08, 0.92), 512), bed("deep", (0.02, 0.48), 256)]
gfx.contact([b[:, :512] for b in beds], "captures/assets/sea_beds.png", scale=2, cols=1, bg=((0x54, 0xA9, 0xA7), (0x2E, 0x30, 0x68)))
gfx.contact(list(checks.values()), "captures/assets/boats.png", scale=3, cols=2)
