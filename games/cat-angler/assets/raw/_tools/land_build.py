"""가게 주인(스프라이트·초상화), 채집지, 섬, 타이틀, 아이템 아이콘을 만든다.

방법: 주인 4명은 고양이 기준 스프라이트를 스타일 참조로 한 시트 한 장, 초상화는 그 시트를 참조로 한 시트 한 장.
대기·말하기 프레임은 머리 줄을 1px 옮기고 눈을 감기는 절차적 프레임이다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
import numpy as np
import gfx
from land_lib import RAW, resize_nearest, clean_specks, zoom_grid

WORK = "assets/raw/work/land"
DARK = (0x17, 0x12, 0x1B)
IDS = ["bait", "market", "yard", "tackle"]  # 너구리, 수달, 비버, 왜가리


def fit(part: np.ndarray, box: int, name: str, sub: str) -> np.ndarray:
    """원본 해상도 조각을 긴 변이 box 가 되게 1x 로 줄인다."""
    f = gfx.save(part, f"{WORK}/{sub}/{name}.png")
    cell = max(part.shape[0], part.shape[1]) / box
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{WORK}/{sub}_px", cell=cell)
    return clean_specks(gfx.trim(gfx.quantize(gfx.load(snapped))), 3)


def canvas(sp, size, bottom=True):
    w, h = size
    sp = sp[: h, : w] if (sp.shape[0] > h or sp.shape[1] > w) else sp
    out = np.zeros((h, w, 4), dtype=np.uint8)
    x = (w - sp.shape[1]) // 2
    y = h - sp.shape[0] if bottom else (h - sp.shape[0]) // 2
    return gfx.over(out, sp, x, y)


def head_shift(a, rows, by):
    out = a.copy()
    head = a[:rows].copy()
    out[:rows] = 0
    if by >= 0:
        return gfx.over(out, head, 0, by)
    # 위로 올릴 때는 비는 줄이 생기지 않게 경계 줄을 그대로 둔다
    out = a.copy()
    out[: rows + by] = a[-by:rows]
    return out


# 눈 자리(스프라이트 좌표 x0, y0, x1, y1). 1x 그림에서 어두운 픽셀 위치를 뽑아 적었다.
EYES = {
    "bait": [(23, 15, 24, 17), (33, 15, 34, 17)],
    "market": [(23, 9, 24, 11), (33, 9, 35, 11)],
    "yard": [(27, 12, 28, 15)],
    "tackle": [(21, 14, 21, 15)],
}


def blink(base, kid, ox, oy):
    """눈을 맨 아랫줄만 남기고 바로 위 픽셀의 색으로 덮는다."""
    out = base.copy()
    for x0, y0, x1, y1 in EYES[kid]:
        fill = base[oy + y0 - 1, ox + x0].copy()
        out[oy + y0 : oy + y1, ox + x0 : ox + x1 + 1] = fill
    return out, len(EYES[kid])


def keepers():
    frames = gfx.sheet_to_frames(f"{RAW}/keepers.png", 2, 2, ref_height=50, work=f"{WORK}/keepers")
    ports = gfx.split_full(gfx.chroma(f"{RAW}/keeper_portraits.png", f"{WORK}/portraits/keyed"), 2, 2)
    allf, allp = [], []
    for kid, sp, po in zip(IDS, frames, ports):
        sp = clean_specks(sp)
        print(kid, sp.shape[1], sp.shape[0])
        gfx.save(sp, f"assets/raw/parts/land/keeper_{kid}.png")
        base = canvas(sp, (48, 56))
        top = 56 - sp.shape[0]
        rows = top + int(sp.shape[0] * 0.55)
        blinked, n = blink(base, kid, (48 - sp.shape[1]) // 2, top)
        print("  blink eyes", n)
        idle = [base, head_shift(base, rows, 1), base, blinked]
        talk = [base, head_shift(base, rows, -1)]
        gfx.write_sheet(idle, f"keeper_{kid}_idle", "assets/game/chars", fps=4)
        gfx.write_sheet(talk, f"keeper_{kid}_talk", "assets/game/chars", fps=6)
        allf += idle + talk
        p = canvas(fit(po, 96, kid, "portraits"), (96, 96))
        gfx.save(p, f"assets/game/portraits/keeper_{kid}.png")
        allp.append(p)
    gfx.contact(allf, "captures/assets/land_keepers.png", scale=3, cols=6)
    gfx.contact(allp, "captures/assets/land_portraits.png", scale=2, cols=4)


def backgrounds():
    f = resize_nearest(f"{RAW}/forage.png", (960, 407))[47:]
    f[..., 3] = 255
    gfx.save(f, "assets/game/places/forage.png")
    zoom_grid(f, "captures/assets/land__forage_grid.png", scale=1, step=40)
    for n in ("island", "title"):
        a = resize_nearest(f"{RAW}/{n}.png", (640, 360)); a[..., 3] = 255
        gfx.save(a, f"assets/game/places/{n}.png")
    zoom_grid(gfx.load("assets/game/places/island.png"), "captures/assets/land__island_grid.png", scale=1, step=40)


def items():
    out = []
    icons = gfx.split_full(gfx.chroma(f"{RAW}/icons.png", f"{WORK}/icons/keyed"), 3, 3)
    for name, part in zip(["herb", "bug", "berry", "flower", "bait_herb", "bait_bug", "bait_berry", "bait_legend", "coin"], icons):
        s = canvas(fit(part, 16, name, "icons"), (16, 16), bottom=False)
        gfx.save(s, f"assets/game/items/{name}.png"); out.append(s)
    plants = gfx.split_full(gfx.chroma(f"{RAW}/plants.png", f"{WORK}/plants/keyed"), 4, 1)
    for name, part in zip(["herb", "bug", "berry", "flower"], plants):
        s = canvas(fit(part, 24, name, "plants"), (24, 24))
        gfx.save(s, f"assets/game/items/{name}_plant.png"); out.append(s)
    rods = gfx.split_full(gfx.chroma(f"{RAW}/rods_icon.png", f"{WORK}/rods_icon/keyed"), 3, 1)
    for i, part in enumerate(rods, 1):
        s = canvas(fit(part, 32, f"rod{i}", "rods_icon"), (32, 32), bottom=False)
        gfx.save(s, f"assets/game/items/rod{i}.png"); out.append(s)
    walls = gfx.split_full(gfx.chroma(f"{RAW}/rods_wall.png", f"{WORK}/rods_wall/keyed"), 3, 1)
    for i, part in enumerate(walls, 1):
        s = canvas(fit(part, 128, f"rod{i}_wall", "rods_wall"), (24, 128), bottom=False)
        gfx.save(s, f"assets/game/items/rod{i}_wall.png"); out.append(s)
    gfx.contact(out[:16], "captures/assets/land_items.png", scale=5, cols=8)
    gfx.contact(out[16:], "captures/assets/land_rods_wall.png", scale=2, cols=3)


if __name__ == "__main__":
    for step in sys.argv[1:] or ["keepers", "backgrounds", "items"]:
        globals()[step]()
