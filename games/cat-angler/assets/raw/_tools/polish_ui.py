"""다듬기 단계의 UI 조각: 깊이 자(대나무), 내구도 아이콘, 말풍선 꼬리. 손으로 찍은 점 그림이다.

실행: uv run -q --project <harness>/tools python assets/raw/_tools/polish_ui.py  (게임 폴더에서)
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
import gfx

UI = "assets/game/ui"
KEY = {".": None, "k": "#5E342B", "w": "#8C533C", "l": "#B4774F", "s": "#DFB68B", "c": "#E5DDC8", "h": "#E9F3E2", "t": "#28706F", "m": "#439083",
       "i": "#17121B", "o": "#D79966"}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def grid(rows):
    out = np.zeros((len(rows), len(rows[0]), 4), dtype=np.uint8)
    for y, line in enumerate(rows):
        assert len(line) == len(rows[0]), (y, line)
        for x, ch in enumerate(line):
            if KEY[ch]:
                out[y, x] = (*rgb(KEY[ch]), 255)
    return out


def depth_ruler():
    """24x32 타일: 세로로 이어지는 대나무 자. 마디가 32px 마다 온다. 눈금과 숫자는 게임이 그 위에 찍는다."""
    out = np.zeros((32, 24, 4), dtype=np.uint8)
    out[..., :3] = rgb("#E5DDC8"); out[..., 3] = 255
    out[:, 21:24, :3] = rgb("#DFB68B")
    out[:, 23, :3] = rgb("#B4774F")
    out[:, 15:17, :3] = rgb("#E9F3E2")
    out[30, :, :3] = rgb("#DFB68B")
    out[31, :, :3] = rgb("#B4774F")
    out[0, :, :3] = rgb("#E9F3E2")
    gfx.save(out, f"{UI}/depth_ruler.png")


def icon_durability():
    """16x16: 돛 달린 배. 내구도 막대 앞에 놓여 '배의 상태'로 읽히게 한다."""
    gfx.save(grid([
        "................",
        ".......k........",
        ".......kcc......",
        ".......kccc.....",
        ".......kcccc....",
        ".......kccccc...",
        ".......kcccccc..",
        ".......k........",
        ".kk....k.....kk.",
        ".kllllllllllllk.",
        ".kwllllllllllwk.",
        "..kwwwwwwwwwwk..",
        "...kwwwwwwwwk...",
        "....kkkkkkkk....",
        "................",
        "................",
    ]), f"{UI}/icon_durability.png")


def bubble_tail():
    """10x12: 대사 창 왼쪽에 붙어 초상화를 가리키는 꼬리. 창의 테두리 색과 바탕색을 쓴다."""
    gfx.save(grid([
        ".........w",
        ".......wwh",
        ".....wwhhh",
        "...wwhhhhh",
        ".wwhhhhhhh",
        "wwhhhhhhhh",
        ".wwhhhhhhh",
        "...wwhhhhh",
        ".....wwhhh",
        ".......wwh",
        ".........w",
        "..........",
    ]), f"{UI}/bubble_tail.png")


def logo():
    """로고 아래의 잔 물결 띠(게임의 문양과 크기가 달랐다)를 걷어 내고, 종이색 밑줄 가운데에 게임과 같은 크기의 물결 문양 한 칸을 단다.
    글자와 고양이 머리는 그대로 둔다(원본: assets/raw/polish/logo_before.png)."""
    src = gfx.load("assets/raw/polish/logo_before.png")
    rows = src[..., 3].any(axis=1)
    gap = max(y for y in range(src.shape[0] - 1) if not rows[y] and rows[y + 1:].any())
    text = gfx.trim(src[:gap])
    half = gfx.load("assets/game/sea/surface_pattern.png")[:17, 16:48]
    scallop = np.kron(half, np.ones((2, 2, 1), dtype=np.uint8))
    w = text.shape[1]
    h = text.shape[0] + 2 + scallop.shape[0]
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out = gfx.over(out, text, 0, 0)
    letters = np.nonzero(text[-6:, :, 3].any(axis=0))[0]
    x0, x1 = int(letters.min()) + 8, int(letters.max()) - 8
    by = text.shape[0] + 2 + scallop.shape[0] - 8
    out[by:by + 8, x0:x1] = (*rgb("#5E342B"), 255)
    out[by + 2:by + 4, x0 + 2:x1 - 2] = (*rgb("#E9F3E2"), 255)
    out[by + 4:by + 6, x0 + 2:x1 - 2] = (*rgb("#E5DDC8"), 255)
    out = gfx.over(out, scallop, (x0 + x1) // 2 - scallop.shape[1] // 2, text.shape[0] + 2)
    gfx.save(out, f"{UI}/logo.png")
    print("logo", out.shape)


if __name__ == "__main__":
    for name in sys.argv[1:] or ["depth_ruler", "icon_durability", "bubble_tail"]:
        globals()[name]()
