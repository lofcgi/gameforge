"""실내 4곳을 640x360 으로 줄이고 팔레트를 입힌다. 좌표 JSON 은 눈금 그림에서 재서 아래 META 에 적었다."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
import numpy as np
from PIL import Image
import gfx
from land_lib import RAW, resize_nearest, zoom_grid

META = {
    "in_bait": {"keeper": [290, 264], "cat": [170, 264], "bench": [350, 224, 248, 24],
                "baskets": [[370, 168], [427, 168], [483, 168], [538, 168]], "out": [570, 236]},
    "in_market": {"keeper": [250, 264], "cat": [130, 264], "table": [334, 224, 252, 46], "scale": [546, 180]},
    "in_yard": {"keeper": [230, 262], "cat": [110, 262], "dock": [492, 240], "preview": [420, 102, 98, 64]},
    "in_tackle": {"keeper": [250, 264], "cat": [130, 264], "rods": [[461, 130], [531, 130], [601, 130]]},
}
# 바닥선이 대사 창(아래 96px)에 가리는 방은 그림을 올리고 맨 아랫줄을 이어 붙였다
SHIFT_UP = {"in_bait": 36, "in_market": 8, "in_tackle": 10, "in_yard": 28}
if __name__ == "__main__":
    tiles = []
    for n in ["in_bait", "in_market", "in_yard", "in_tackle"]:
        a = resize_nearest(f"{RAW}/{n}2.png", (640, 360))  # 2 = 캐릭터 크기 안내 그림을 주고 다시 생성한 판
        up = SHIFT_UP.get(n, 0)
        if up:
            a = np.concatenate([a[up:], np.repeat(a[-1:], up, axis=0)], axis=0)
        if n == "in_tackle":
            # 그려진 고리 간격(57px)이 규격(70 이상)보다 좁아 고리를 판 색으로 지우고 낚싯대 자리를 따로 정했다
            a[50:72, 450:613] = a[100, 530]
        a[..., 3] = 255
        gfx.save(a, f"assets/game/places/{n}.png")
        zoom_grid(a, f"captures/assets/land__{n}_grid.png", scale=1, step=40)
        tiles.append(Image.open(gfx.ROOT / f"captures/assets/land__{n}_grid.png"))
        if n in META:
            (gfx.ROOT / f"assets/game/places/{n}.json").write_text(json.dumps(META[n], ensure_ascii=False, indent=1) + "\n")
    o = Image.new("RGB", (1284, 724))
    for i, t in enumerate(tiles):
        o.paste(t, ((i % 2) * 644, (i // 2) * 364))
    o.save(gfx.ROOT / "captures/assets/land__interiors_grid.png")
