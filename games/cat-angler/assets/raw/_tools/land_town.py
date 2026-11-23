"""항구 마을(town.png, town_fg.png, town.json)과 부두(sea/pier.png)를 조립한다.

방법: 건물 4채·소품·부두는 마젠타 배경에 따로 생성한 스프라이트, 하늘·바다 배경과 땅 띠는 생성한 그림을 1x 로 줄여 이어 붙였다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
import numpy as np
import gfx
from land_lib import RAW, resize_nearest, sprite, clean_specks, zoom_grid

W, H, GROUND_TOP = 1600, 360, 300
WORK = "assets/raw/work/land_town"
# 건물: (원본, 1x 세로, 원본에서 자를 영역(돌 받침을 뺀다), 왼쪽 x)
BUILD = {
    "bait": ("b_bait.png", 137, None, 56),
    "market": ("b_market.png", 137, None, 360),
    "yard": ("b_yard.png", 195, (0, 0, 1200, 762), 668),
    "tackle": ("b_tackle.png", 163, (0, 0, 1200, 772), 950),
}
GROUND_END = 1290

back = resize_nearest(f"{RAW}/town_backdrop.png", (640, 357))
back = np.concatenate([back, np.repeat(back[-1:], 3, axis=0)], axis=0)
town = np.concatenate([back, back[:, ::-1], back[:, :320]], axis=1)

ground = resize_nearest(f"{RAW}/town_ground.png", (256, 64))[:60]
strip = np.concatenate([ground] * 6, axis=1)[:, :GROUND_END]
town[GROUND_TOP:, :GROUND_END] = strip
town[GROUND_TOP:, GROUND_END - 1] = (0x17, 0x12, 0x1B, 255)

pier = clean_specks(sprite(f"{RAW}/pier.png", 117, WORK))
gfx.save(pier, "assets/raw/parts/land/pier.png")
doors = {}
parts = {}
for name, (raw, h, crop, x) in BUILD.items():
    s = clean_specks(sprite(f"{RAW}/{raw}", h, WORK, crop))
    parts[name] = (s, x)
    gfx.save(s, f"assets/raw/parts/land/b_{name}.png")
    town = gfx.over(town, s, x, GROUND_TOP - s.shape[0] + 1)
    print(name, s.shape[1], s.shape[0], "x", x, "..", x + s.shape[1])

GROUND_Y = 302   # 발이 닿는 줄(자갈 윗줄에서 2px 안쪽)
PIER_FRONT = 66  # 부두 그림에서 갑판 앞 가장자리의 줄. 고양이는 난간 앞, 이 줄을 걷는다
town = gfx.over(town, pier, W - pier.shape[1], GROUND_Y - PIER_FRONT)
gfx.save(town, "assets/game/places/town.png")
gfx.save(pier, "assets/game/sea/pier.png")

# 앞 겹: 캐릭터보다 앞(아래쪽)에 놓이는 소품. 문 앞은 비워 둔다.
prop = [gfx.load(f"assets/raw/parts/land/prop_{i}.png") for i in range(7)]
FENCE, CRATE, BOLLARD, BARREL, LAMP_S, LAMP_T, BASKET = prop
fg = np.zeros((H, W, 4), dtype=np.uint8)
BASE = 313
for sp, x in [(FENCE, 0), (FENCE, 29), (FENCE, 58), (LAMP_T, 300), (BARREL, 322), (FENCE, 590), (FENCE, 619), (CRATE, 650),
              (LAMP_S, 905), (BARREL, 924), (BASKET, 1150), (FENCE, 1180), (FENCE, 1209), (LAMP_T, 1250), (BOLLARD, 1262)]:
    fg = gfx.over(fg, sp, x, BASE - sp.shape[0])
gfx.save(fg, "assets/game/places/town_fg.png")

# 문의 가로 가운데는 확대 눈금 그림(captures/assets/land__doors.png)에서 쟀다
meta = {"doors": {"bait": 197, "market": 522, "yard": 825, "tackle": 1068}, "pier": 1540, "ground_y": GROUND_Y, "left": 24, "right": 1584}
(gfx.ROOT / "assets/game/places/town.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
(gfx.ROOT / "assets/game/sea/pier.json").write_text(json.dumps({"deck_y": PIER_FRONT, "waterline": pier.shape[0] - 24, "size": [pier.shape[1], pier.shape[0]]}, indent=1) + "\n")

# 확인용: 앞 겹과 고양이를 올려 본다
cat = gfx.load("assets/raw/parts/cat/stand.png")
chk = gfx.over(town, cat, 197 - 21, GROUND_Y - cat.shape[0] + 1)
chk = gfx.over(chk, cat, 700, GROUND_Y - cat.shape[0] + 1)
chk = gfx.over(chk, cat, 1450, GROUND_Y - cat.shape[0] + 1)
chk = gfx.over(chk, fg)
gfx.save(chk, "captures/assets/land_town_check.png")
gfx.save(chk[:, 0:800], "captures/assets/land__town_l.png"); gfx.save(chk[:, 800:], "captures/assets/land__town_r.png")
