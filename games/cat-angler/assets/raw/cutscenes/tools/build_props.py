"""전설의 그림자 두 장과 큰 물보라를 만든다.

legend_shadow: 게임의 전설 어종 그림(assets/game/fish/legend_swim.png, 4프레임)의 윤곽을 두 배로 키워(fine.py)
한 색으로 칠하고 눈과 옆줄의 빛만 넣는다. 여는 컷신에서 보는 그림자가 게임에서 낚는 바로 그 물고기다.
legend_b: 다음 전설(1배로 만들어 둔 sprites/legend_b_1x.png)을 두 배로 키운다. 화면에 다 들어오지 않을 만큼 크다.

실행: uv run -q --project <harness>/tools python build_props.py
"""

from pathlib import Path

import numpy as np

from gf.post.io import load_rgba, save_rgba

import fine

GAME = Path(__file__).resolve().parents[3] / "game"
INK, TEAL, CYAN, MINT = (0x17, 0x12, 0x1B), (0x28, 0x70, 0x6F), (0x76, 0xD7, 0xD9), (0xBA, 0xEA, 0xDC)
FRAME = 176
EYE = (157, 48)


def main() -> None:
    sheet = load_rgba(GAME / "fish/legend_swim.png")
    frames = []
    for i in range(sheet.shape[1] // FRAME):
        solid = (sheet[:, i * FRAME : (i + 1) * FRAME, 3] > 0).astype(np.int64)
        big = fine.mode(fine.smooth(solid, 2), 2) > 0
        out = np.zeros((*big.shape, 4), dtype=np.uint8)
        out[big] = (*INK, 255)
        # 옆줄: 몸통 가운데를 따라 점선으로 빛난다.
        for x in range(96, 290, 6):
            ys = np.flatnonzero(big[:, x])
            y = int(ys.min() * 0.52 + ys.max() * 0.48)
            out[y, x] = (*(CYAN if (x // 6) % 3 == 0 else TEAL), 255)
        ex, ey = EYE[0] * 2, EYE[1] * 2
        out[ey - 2 : ey + 3, ex - 2 : ex + 3] = (*CYAN, 255)
        out[ey - 1 : ey + 2, ex - 1 : ex + 2] = (*MINT, 255)
        for cx, cy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            out[ey + cy, ex + cx] = (*INK, 255)
        frames.append(out)
    save_rgba(np.concatenate(frames, axis=1), GAME / "cutscenes/props/legend_shadow.png")
    # 8컷의 큰 물보라: 1배 물보라(props/p_splash.png)를 두 배로 키운다.
    splash = fine.index(load_rgba(GAME / "cutscenes/props/p_splash.png"))
    save_rgba(fine.unindex(fine.mode(fine.smooth(splash, 2), 1)), GAME / "cutscenes/props/p_splash_big.png")
    next_legend = fine.index(load_rgba(Path(__file__).resolve().parents[1] / "sprites/legend_b_1x.png"))
    save_rgba(fine.unindex(fine.mode(fine.smooth(next_legend, 2), 1)), GAME / "cutscenes/props/legend_b.png")


if __name__ == "__main__":
    main()
