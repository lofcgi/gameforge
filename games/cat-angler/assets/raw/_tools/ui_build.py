"""UI 부품을 만든다. 생성한 시트(assets/raw/ui/ui_parts.png, ui_icons.png, codex_book.png)를 잘라 규격 크기로 맞추고,
9-slice 로 늘려도 이어지도록 가장자리의 가운데 띠를 한 가지 색 줄로 고른다. 모서리 장식과 테두리 색은 생성물 그대로다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
from collections import Counter
import numpy as np
import gfx

OUT = "assets/game/ui"
WORK = "assets/raw/work/ui"
UI = ["#17121B", "#5E342B", "#8C533C", "#B4774F", "#D79966", "#DFB68B", "#E5DDC8", "#E9F3E2", "#28706F", "#439083", "#54A9A7", "#194A50", "#B8D0BF"]
UI_PAL = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in UI], dtype=np.int32)


def hexc(c):
    return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255)


def mode(px):
    return Counter(map(tuple, px.reshape(-1, 4))).most_common(1)[0][0]


def fit(part, w, h, name):
    """자른 원본 조각을 w x h 로 맞춘다(부품은 네모라 늘려도 된다)."""
    f = gfx.save(part, f"{WORK}/{name}_src.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{WORK}/pixel", size=f"{w}x{h}")
    return gfx.quantize(gfx.load(snapped), UI_PAL)


def uniform(a, m, flat_centre=True):
    """9-slice 가 늘리는 띠(위·아래·왼쪽·오른쪽 가장자리의 가운데 부분)를 줄마다 한 색으로 만든다."""
    out = a.copy()
    h, w = a.shape[:2]
    for y in list(range(m)) + list(range(h - m, h)):
        out[y, m:w - m] = mode(a[y, m:w - m])
    for x in list(range(m)) + list(range(w - m, w)):
        out[m:h - m, x] = mode(a[m:h - m, x])
    if flat_centre:
        out[m:h - m, m:w - m] = mode(a[m:h - m, m:w - m])
    return out


def nine(src, m, w, h):
    """src 를 가장자리 m 의 9-slice 로 w x h 에 다시 그린다."""
    sh, sw = src.shape[:2]
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[:, :] = src[sh // 2, sw // 2]
    out[:m] = src[:m, sw // 2][:, None]
    out[h - m:] = src[sh - m:, sw // 2][:, None]
    out[:, :m] = src[sh // 2, :m][None]
    out[:, w - m:] = src[sh // 2, sw - m:][None]
    out[:m, :m] = src[:m, :m]
    out[:m, w - m:] = src[:m, sw - m:]
    out[h - m:, :m] = src[sh - m:, :m]
    out[h - m:, w - m:] = src[sh - m:, sw - m:]
    return out


def swap(a, table):
    out = a.copy()
    for src, dst in table.items():
        s = hexc(src)
        m = (a[..., :3] == s[:3]).all(-1) & (a[..., 3] > 0)
        out[m] = hexc(dst)
    return out


def body_only(part):
    """말풍선의 꼬리를 뗀다: 너비가 본체의 70% 아래로 줄어드는 줄부터 버린다."""
    widths = (part[..., 3] > 0).sum(1)
    full = widths.max()
    last = max(y for y in range(len(widths)) if widths[y] >= full * 0.7)
    return gfx.trim(part[: last + 1])


def scallop_corner(a, corners=("tl", "tr", "bl", "br"), reach=8):
    """모서리의 물결 장식을 또렷한 겹친 반원 띠로 다시 그린다(생성물의 장식은 이 크기에서 얼룩이 된다).
    테두리 안쪽 모서리를 중심으로 청록 두 색과 종이색이 번갈아 나오는 사분원."""
    h, w = a.shape[:2]
    paper = mode(a[h // 2 - 2:h // 2 + 2, w // 2 - 2:w // 2 + 2])
    t = next(i for i in range(h // 2) if tuple(a[h // 2, i]) == paper)  # 테두리 두께
    rings = [hexc("#28706F"), hexc("#54A9A7"), paper, hexc("#439083"), hexc("#54A9A7"), paper, hexc("#28706F"), hexc("#54A9A7")]
    tile = np.zeros((reach, reach, 4), dtype=np.uint8)
    tile[:] = paper
    for y in range(reach):
        for x in range(reach):
            d = (x * x + y * y) ** 0.5
            if d < reach - 0.5:
                tile[y, x] = rings[int(d)]
    out = a.copy()
    for c in corners:
        tl = tile[::-1] if c[0] == "b" else tile
        tl = tl[:, ::-1] if c[1] == "r" else tl
        y0 = h - t - reach if c[0] == "b" else t
        x0 = w - t - reach if c[1] == "r" else t
        block = out[y0:y0 + reach, x0:x0 + reach]
        inside = (block[..., 3] > 0)
        block[inside] = tl[inside]
    return out


def clean_inside(a, m):
    """테두리 안쪽에 남은 생성물의 장식 얼룩을 종이색으로 지운다(테두리 색은 건드리지 않는다)."""
    out = a.copy()
    h, w = a.shape[:2]
    paper = mode(a[h // 2 - 2:h // 2 + 2, w // 2 - 2:w // 2 + 2])
    teal = {hexc(c)[:3] for c in ("#28706F", "#439083", "#54A9A7", "#194A50", "#B8D0BF")}
    for y in range(h):
        for x in range(w):
            if tuple(a[y, x, :3]) in teal and a[y, x, 3]:
                out[y, x] = paper
    # 테두리(두께 4) 안쪽은 전부 종이색: 장식의 밝은 가장자리 점까지 지운다
    out[4:h - 4, 4:w - 4] = paper
    # 테두리의 가장 안쪽 줄이 모서리와 가운데에서 색이 달랐다. 줄 전체를 그 줄에서 가장 많은 색으로 고른다
    out[3, 4:w - 4] = mode(out[3, 4:w - 4]); out[h - 4, 4:w - 4] = mode(out[h - 4, 4:w - 4])
    out[4:h - 4, 3] = mode(out[4:h - 4, 3]); out[4:h - 4, w - 4] = mode(out[4:h - 4, w - 4])
    return out


def mirror_bubble(a, m=12):
    """말풍선: 꼬리를 뗀 자리와 장식 자리를 없애려고 오른쪽 위 모서리를 네 모서리에 뒤집어 쓴다."""
    out = a.copy()
    h, w = a.shape[:2]
    tr = a[:m, w - m:]
    out[:m, :m] = tr[:, ::-1]
    out[h - m:, w - m:] = tr[::-1]
    out[h - m:, :m] = tr[::-1, ::-1]
    out[h - m:, m:w - m] = a[:m, m:w - m][::-1]
    out[m:h - m, :m] = a[m:h - m, w - m:][:, ::-1]
    return out


def build_parts():
    keyed = gfx.chroma("assets/raw/ui/ui_parts.png", f"{WORK}/keyed")
    panel, bubble, button, slot = gfx.split_full(keyed, 2, 2)
    made = {}
    made["panel"] = scallop_corner(clean_inside(uniform(fit(panel, 48, 48, "panel"), 12), 12))
    # 말풍선: 생성한 말풍선은 테두리가 종이색과 거의 같아 물색 위에서 가장자리가 사라졌다. 창 틀을 밝은 종이색으로 바꾸고 장식은 왼쪽 위에만 둔다
    plain = swap(clean_inside(uniform(fit(panel, 48, 48, "panel"), 12), 12), {"#E5DDC8": "#E9F3E2"})
    made["bubble"] = scallop_corner(plain, corners=("tl",))
    made["button"] = uniform(fit(button, 32, 24, "button"), 8)
    made["slot"] = uniform(fit(slot, 28, 28, "slot"), 6)
    # 고른 상태: 바탕을 한 단계 밝히고 테두리를 청록으로 바꾼다
    made["button_focus"] = swap(made["button"], {"#B4774F": "#DFB68B", "#D79966": "#E5DDC8", "#DFB68B": "#E9F3E2", "#8C533C": "#28706F", "#5E342B": "#194A50"})
    made["slot_focus"] = swap(made["slot"], {"#8C533C": "#28706F", "#5E342B": "#194A50", "#B4774F": "#54A9A7", "#DFB68B": "#E9F3E2", "#E5DDC8": "#E9F3E2"})
    # 게이지 틀은 칸(slot)의 테두리를 그대로 가져와 규격 크기로 다시 짠다. 안쪽은 어두운 바탕
    inner = hexc("#5E342B")
    g = nine(made["slot"], 4, 64, 12)
    g[4:-4, 4:-4] = inner
    made["gauge_frame"] = g
    t = nine(made["slot"], 6, 24, 168)
    t[6:-6, 6:-6] = inner
    made["tension_frame"] = t
    fill = np.zeros((4, 4, 4), dtype=np.uint8)
    fill[:] = hexc("#54A9A7"); fill[0] = hexc("#76D7D9"); fill[3] = hexc("#439083")
    made["gauge_fill"] = fill
    tf = np.zeros((4, 4, 4), dtype=np.uint8)
    tf[:] = hexc("#E9F3E2"); tf[:, 3] = hexc("#E5DDC8")
    made["tension_fill"] = tf
    # 깊이 눈금: 창 틀의 종이색과 테두리색으로 세로 띠를 짠다. 32px 마다 긴 눈금, 8px 마다 짧은 눈금
    paper, edge = mode(made["panel"][12:-12, 12:-12]), hexc("#8C533C")
    r = np.zeros((32, 24, 4), dtype=np.uint8)
    r[:, 2:22] = paper
    r[:, 2] = edge; r[:, 21] = edge; r[:, 1] = hexc("#5E342B"); r[:, 22] = hexc("#5E342B")
    r[:, 3] = hexc("#E9F3E2")
    for y in range(0, 32, 8):
        r[y, 12 if y else 6:21] = edge
    r[1, 6:21] = hexc("#B4774F")
    made["depth_ruler"] = r
    return made


def build_icons():
    keyed = gfx.chroma("assets/raw/ui/ui_icons.png", f"{WORK}/keyed")
    names = ["icon_durability", "icon_hold", "icon_coin", "icon_anchor", "icon_bait", "arrow"]
    made = {}
    for name, part in zip(names, gfx.split_full(keyed, 3, 2)):
        f = gfx.save(part, f"{WORK}/{name}_src.png")
        ph, pw = part.shape[:2]
        # 긴 변이 16 이 되게 줄인다
        snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{WORK}/pixel", cell=max(ph, pw) / 16)
        s = gfx.trim(gfx.quantize(gfx.load(snapped)))[:16, :16]
        made[name] = gfx.place(s, (16, 16), (8, 8 + (s.shape[0] + 1) // 2))
    return made


def build_codex():
    snapped, _ = gfx.snap("assets/raw/ui/codex_book.png", f"{WORK}/pixel", size="640x360")
    a = gfx.load(snapped)
    a[..., 3] = 255
    a = gfx.quantize(a)
    # 쪽 자리: 화면 가운데 줄에서 종이색(밝은 색)이 이어지는 두 구간을 찾고, 세로도 같은 방법으로 잰다
    light = (a[..., :3].astype(int).sum(-1) > 600)
    cols = light[100:260].mean(0) > 0.9
    runs, start = [], None
    for x in range(640):
        if cols[x] and start is None:
            start = x
        if (not cols[x] or x == 639) and start is not None:
            if x - start > 120:
                runs.append((start, x))
            start = None
    rects = []
    for x0, x1 in runs[:2]:
        rows = light[:, x0 + 20:x1 - 20].mean(1) > 0.9
        ys = np.nonzero(rows)[0]
        rects.append([int(x0 + 10), int(ys.min() + 14), int(x1 - x0 - 20), int(ys.max() - ys.min() - 28)])
    return a, rects


if __name__ == "__main__":
    made = build_parts() | build_icons()
    for name, a in made.items():
        gfx.save(a, f"{OUT}/{name}.png")
    book, rects = build_codex()
    gfx.save(book, f"{OUT}/codex_book.png")
    if len(rects) == 2:
        pass
    # 쪽 자리는 그림에서 쟀다(자동 측정값은 모서리 장식과 책갈피 끈에 걸려 좌우가 달랐다). 장식과 끈을 피한 안쪽이다
    (gfx.ROOT / OUT / "codex_book.json").write_text(json.dumps({"left": [58, 50, 250, 268], "right": [372, 50, 212, 268]}) + "\n")
    order = ["panel", "bubble", "button", "button_focus", "slot", "slot_focus", "gauge_frame", "gauge_fill", "tension_frame", "tension_fill", "depth_ruler", "icon_durability", "icon_hold", "icon_coin", "icon_anchor", "icon_bait", "arrow"]
    gfx.contact([made[n] for n in order[:6]], "captures/assets/ui_parts.png", scale=5, cols=6, bg=((93, 197, 203),))
