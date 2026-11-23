"""채집지와 섬의 좌표 JSON. 값은 눈금 그림(captures/assets/land__fi_grid.png)에서 쟀다."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
Y = 303  # 재료 그림의 아래 가운데: 모랫길 위(풀밭 그림에 묻히지 않게 길 위에 둔다)
forage = {
    "herb": [[150, Y], [400, Y], [590, Y], [790, Y]],
    "bug": [[230, Y], [450, Y], [660, Y], [870, Y]],
    "berry": [[90, Y], [330, Y], [520, Y], [720, Y]],
    "ground_y": 310, "left": 16, "right": 944,
}
island = {"flower": [[560, 306]], "dock": 124, "ground_y": 310, "left": 112, "right": 624}
(ROOT / "assets/game/places/forage.json").write_text(json.dumps(forage, indent=1) + "\n")
(ROOT / "assets/game/places/island.json").write_text(json.dumps(island, indent=1) + "\n")
