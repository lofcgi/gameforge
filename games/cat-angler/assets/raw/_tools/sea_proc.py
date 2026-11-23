"""절차적으로 그리는 바다 에셋: 하늘, 물속 띠, 수면 문양, 효과, 어군 표시, 소용돌이, 미끼, 배의 JSON.

색 띠와 물결 문양은 기준 화면에서도 기하학적 무늬라 계산으로 그리는 쪽이 정확하고 이음매가 없다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json, math
import numpy as np
import gfx

SEA = "assets/game/sea"


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def canvas(w, h, colour=None):
    a = np.zeros((h, w, 4), dtype=np.uint8)
    if colour:
        a[..., :3] = rgb(colour); a[..., 3] = 255
    return a


def px(a, x, y, colour):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        a[y, x] = (*rgb(colour), 255)


def bands(w, h, stops, seed=0, amp=5, dither=4):
    """위에서 아래로 색 띠를 쌓는다. 경계는 가로 w 주기로 이어지는 물결선이고 그 둘레 dither px 를 바둑판으로 섞는다."""
    a = canvas(w, h, stops[0][1])
    xs = np.arange(w)
    for i, (y0, colour) in enumerate(stops[1:], 1):
        ph = seed * 1.7 + i * 2.1
        wave = amp * np.sin(2 * math.pi * 2 * xs / w + ph) + amp * 0.5 * np.sin(2 * math.pi * 5 * xs / w + ph * 2) + amp * 0.3 * np.sin(2 * math.pi * 11 * xs / w + ph * 3)
        edge = (y0 + wave).round().astype(int)
        for x in range(w):
            e = edge[x]
            for y in range(max(0, e - dither), h):
                if y >= e + dither or (x + y) % 2 == 0 and y >= e - dither + ((x // 2 + y // 2) % 2) * 0:
                    # 경계 위쪽 절반은 성기게, 아래쪽 절반은 촘촘하게
                    if y < e:
                        if (x % 4 == (y % 2) * 2) or (y >= e - dither // 2 and (x + y) % 2 == 0):
                            a[y, x, :3] = rgb(colour)
                    elif y < e + dither:
                        if not ((x % 4 == (y % 2) * 2) and y >= e + dither // 2) or (x + y) % 2 == 0:
                            a[y, x, :3] = rgb(colour)
                    else:
                        a[y, x, :3] = rgb(colour)
    return a


LIGHTER = {"#54A9A7": "#5DC5CB", "#5DC5CB": "#76D7D9", "#468DB4": "#54A9A7", "#426A96": "#468DB4", "#2E3068": "#426A96"}


def rays(a, specs, depth):
    """수면에서 비스듬히 내려오는 빛줄기. 한 단계 밝은 색을 바둑판으로 섞고 깊어질수록 성기게 한다."""
    h, w = a.shape[:2]
    lut = {rgb(k): rgb(v) for k, v in LIGHTER.items()}
    for x0, width in specs:
        for y in range(min(depth, h)):
            t = y / depth
            for dx in range(int(width * (1 + t * 0.6))):
                x = (x0 + dx + int(y * 0.35)) % w
                dense = (x + y) % 2 == 0 if t < 0.5 else (x % 4 == (y % 2) * 2 and y % 2 == 0) if t > 0.8 else (x % 2 == 0 and y % 2 == 0)
                c = tuple(int(v) for v in a[y, x, :3])
                if dense and c in lut:
                    a[y, x, :3] = lut[c]
    return a


# --- 하늘 640x200 ---
sky = {
    "shallow": [(0, "#BAEADC"), (128, "#E9F3E2")],
    "open": [(0, "#7BAEB9"), (58, "#B8D0BF"), (140, "#E9F3E2")],
    "deep": [(0, "#2E3068"), (52, "#426A96"), (118, "#7BAEB9"), (172, "#B8D0BF")],
}
for zone, stops in sky.items():
    a = bands(640, 200, stops, seed=len(zone), amp=3, dither=3)
    if zone == "deep":
        rng = np.random.default_rng(7)
        for _ in range(26):
            px(a, int(rng.integers(0, 640)), int(rng.integers(2, 44)), "#E9F3E2" if rng.random() < 0.5 else "#7BAEB9")
    gfx.save(a, f"{SEA}/sky_{zone}.png")

# --- 물속 640x360 ---
under = {
    "shallow": ([(0, "#76D7D9"), (40, "#5DC5CB"), (84, "#54A9A7"), (176, "#468DB4")], [(60, 26), (250, 40), (430, 22), (560, 30)], 150),
    "open": ([(0, "#5DC5CB"), (26, "#54A9A7"), (72, "#468DB4"), (196, "#426A96"), (322, "#2E3068")], [(100, 34), (300, 50), (470, 26)], 260),
    "deep": ([(0, "#468DB4"), (30, "#426A96"), (104, "#2E3068"), (262, "#1B2139")], [(180, 30), (420, 40)], 150),
}
for zone, (stops, ray, depth) in under.items():
    a = bands(640, 360, stops, seed=len(zone) + 3, amp=6, dither=5)
    a = rays(a, ray, depth)
    a[-1, :, :3] = rgb(stops[-1][1])
    gfx.save(a, f"{SEA}/under_{zone}.png")

# --- 수면 문양 64x32: 반원을 비늘처럼 겹친 전통 물결 문양 ---
def scallop(a, cx, cy, r=16):
    rings = [(r, "#E5DDC8"), (r - 2, "#54A9A7"), (r - 5, "#E5DDC8"), (r - 6, "#439083"), (r - 9, "#E5DDC8"), (r - 10, "#28706F"), (r - 13, "#439083")]
    h, w = a.shape[:2]
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            for rr, colour in rings:
                if d <= rr:
                    c = colour
                else:
                    break
            else:
                pass
            if d <= r and 0 <= y < h:
                a[y, x % w] = (*rgb(c), 255)

pat = canvas(64, 32)
for cx in (0, 32, 64):
    scallop(pat, cx, 16)
for cx in (16, 48):
    scallop(pat, cx, 32)
gfx.save(pat, f"{SEA}/surface_pattern.png")

# --- 효과 ---
def ring(a, cx, cy, rx, ry, colour, dash=0, phase=0, half=None):
    n = max(16, int(8 * max(rx, ry)))
    for i in range(n):
        if dash and ((i + phase) // dash) % 2:
            continue
        t = 2 * math.pi * i / n
        if half == "top" and math.sin(t) > 0:
            continue
        px(a, int(round(cx + rx * math.cos(t))), int(round(cy + ry * math.sin(t))), colour)

# 물보라 6프레임 24x20: 가운데 기둥이 솟고 물방울이 퍼지며 떨어진다
splash = []
for f in range(6):
    a = canvas(24, 20)
    t = f / 5
    for k, (vx, vy) in enumerate([(-5, -15), (-3, -19), (-1, -22), (1, -22), (3, -19), (5, -15), (-7, -10), (7, -10)]):
        x = 12 + vx * t * 1.3
        y = 18 + vy * t + 22 * t * t
        if y < 19:
            c = "#E9F3E2" if k % 2 == 0 else "#BAEADC"
            px(a, int(round(x)), int(round(y)), c)
            if f < 4:
                px(a, int(round(x)), int(round(y)) + 1, "#76D7D9")
                px(a, int(round(x)) + (1 if vx > 0 else -1), int(round(y)), c)
    w = [2, 5, 8, 10, 11, 11][f]
    for x in range(12 - w, 12 + w + 1):
        if f < 5 or x % 2 == 0:
            px(a, x, 19, "#E9F3E2")
        if f < 3 and abs(x - 12) < w - 1:
            px(a, x, 18, "#BAEADC")
    splash.append(a)
gfx.write_sheet(splash, "splash", SEA, fps=12, loop=False)

bubble = []
for f in range(4):
    a = canvas(8, 8)
    if f < 3:
        r = [1.2, 2.2, 3.0][f]
        ring(a, 3.5, 3.5, r, r, "#BAEADC")
        px(a, 3 - (f > 0), 3 - (f > 0), "#E9F3E2")
    else:
        for x, y in [(0, 3), (7, 4), (3, 0), (4, 7), (1, 1), (6, 6)]:
            px(a, x, y, "#BAEADC")
    bubble.append(a)
gfx.write_sheet(bubble, "bubble", SEA, fps=8)

sparkle = []
for f, n in enumerate([1, 3, 4, 2]):
    a = canvas(9, 9)
    for d in range(n + 1):
        for x, y in [(4 - d, 4), (4 + d, 4), (4, 4 - d), (4, 4 + d)]:
            px(a, x, y, "#E9F3E2" if d < n else "#76D7D9")
    if n >= 3:
        for x, y in [(3, 3), (5, 5), (3, 5), (5, 3)]:
            px(a, x, y, "#BAEADC")
    sparkle.append(a)
gfx.write_sheet(sparkle, "sparkle", SEA, fps=8)

# 어군 표시: 잔물결 고리가 퍼지고 작은 물고기가 수면 위로 튄다. 코드가 그림 가운데를 수면선 4px 아래에 놓으므로 잔물결 줄은 가운데에서 4px 위다.
def school(w, h, rings_n, jumpers):
    frames = []
    for f in range(4):
        a = canvas(w, h)
        base = h // 2 - 4
        for k in range(rings_n):
            rx = (w / 2 - 2) * (k + 1) / rings_n * (0.82 + 0.06 * ((f + k) % 4))
            ring(a, w / 2 - 0.5, base, rx, 2, "#E9F3E2" if k % 2 == 0 else "#BAEADC", dash=3, phase=f * 2 + k)
        for j, (jx, ph) in enumerate(jumpers):
            t = ((f + ph) % 4) / 3
            y = base - 2 - int(round((base - 4) * 4 * t * (1 - t)))
            x = jx + int(round(t * 5))
            for dx in range(3):
                px(a, x + dx, y, "#B8D0BF")
            px(a, x + 2, y, "#17121B")
            px(a, x - 1, y - 1 if t < 0.5 else y + 1, "#439083")
            if t in (0.0, 1.0):
                px(a, x + 1, base - 1, "#E9F3E2")
        frames.append(a)
    return frames

gfx.write_sheet(school(32, 28, 2, [(10, 0)]), "school_small", SEA, fps=6)
gfx.write_sheet(school(48, 32, 3, [(12, 0), (28, 2)]), "school_mid", SEA, fps=6)
gfx.write_sheet(school(72, 40, 4, [(14, 0), (34, 1), (50, 3)]), "school_big", SEA, fps=6)

vortex = []
for f in range(4):
    a = canvas(96, 24)
    for k, (rx, ry, c) in enumerate([(46, 9, "#E9F3E2"), (36, 7, "#BAEADC"), (26, 5, "#E9F3E2"), (16, 3, "#76D7D9"), (7, 1.5, "#2E3068")]):
        ring(a, 47.5, 13, rx, ry, c, dash=5, phase=f * 3 * (1 + k % 2) + k * 2)
    for x in range(42, 54):
        px(a, x, 13, "#1B2139")
    for x in range(44, 52):
        px(a, x, 14, "#17121B")
    vortex.append(a)
gfx.write_sheet(vortex, "vortex", SEA, fps=8)

# --- 미끼 8x8 (손으로 찍은 점) ---
KEY = {".": None, "k": "#17121B", "g": "#439083", "G": "#96B89D", "l": "#BAEADC", "b": "#8C533C", "B": "#B4774F", "o": "#D79966", "O": "#DFB68B", "w": "#E9F3E2", "c": "#76D7D9", "t": "#28706F", "n": "#5E342B"}
BAITS = {
    "herb": ["..kkk...", ".kGGGk..", "kGlGGGk.", "kGGGgGk.", "kGGgGGk.", ".kgGGk..", "..kkk...", "........"],
    "bug": ["........", ".kk..kk.", "kBOkkBBk", "kBBBBBOk", ".kBBkBBk", "..kk.kk.", "........", "........"],
    "berry": ["...kt...", "..ktk...", ".koOok..", "kooOook.", "koooook.", "kBooook.", ".kBook..", "..kkk..."],
    "legend": ["...kk...", "..kwwk..", ".kwwcwk.", "kwwclcwk", "kwclccwk", ".kwccwk.", "..kwwk..", "...kk..."],
}
baits = []
for bid, rows in BAITS.items():
    a = canvas(8, 8)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if KEY[ch]:
                px(a, x, y, KEY[ch])
    gfx.save(a, f"{SEA}/bait_{bid}.png"); baits.append(a)

# --- 배의 JSON: 고양이 자리(발밑 가운데), 낚싯대 끝, 흘수선 ---
cat = json.loads((gfx.ROOT / "assets/game/chars/cat.json").read_text())
tip = cat["rod_tip"]["sit_fish"][0]
off = (tip[0] - cat["foot"][0], tip[1] - cat["foot"][1])
for name, seat, waterline in [("boat1", (86, 9), 23), ("boat2", (122, 108), 123), ("boat3", (172, 103), 124)]:
    data = {"seat": list(seat), "rod_tip": [seat[0] + off[0], seat[1] + off[1]], "waterline": waterline}
    (gfx.ROOT / f"assets/game/boats/{name}.json").write_text(json.dumps(data) + "\n")
    print(name, data)

gfx.contact(splash + bubble + sparkle + baits, "captures/assets/sea_fx.png", scale=5, cols=9, bg=((0x5D, 0xC5, 0xCB), (0x2E, 0x30, 0x68)))
gfx.contact(school(72, 40, 4, [(14, 0), (34, 1), (50, 3)]) + vortex, "captures/assets/sea_markers.png", scale=3, cols=4, bg=((0x5D, 0xC5, 0xCB), (0x2E, 0x30, 0x68)))
