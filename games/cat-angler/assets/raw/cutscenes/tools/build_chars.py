"""컷신 캐릭터 그림을 원본에서 다시 만든다 (assets/game/cutscenes/chars).

원본은 아트 픽셀 한 칸이 5.12px 또는 10.24px 인 1024px 그림이다. 칸대로 줄인 그림(native)에서
눈 깜빡임 같은 픽셀 손질을 하고, fine.py 로 정수배 확대해 화면 픽셀 굵기의 그림으로 만든다.

실행: uv run -q --project <harness>/tools python build_chars.py [--native <폴더>]
"""

import argparse
import sys
from pathlib import Path

import numpy as np

from gf.post import palette, pixel
from gf.post.io import load_rgba, save_rgba

import fine
from proc import PALETTE, key

RAW = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[3] / "game/cutscenes/chars"
LINES = ["#17121B", "#1B2139"]


def colour(text: str) -> int:
    value = int(text.lstrip("#"), 16)
    return value + 1


def sheet(name: str, cell: float, offset: tuple[float, float] = (0, 0)) -> np.ndarray:
    """원본 한 장을 아트 픽셀 격자로 줄인 색 번호 배열."""
    keyed = key(load_rgba(RAW / f"{name}.png"))
    return fine.index(palette.apply(pixel.snap(keyed, (cell, cell), offset), PALETTE))


def quarters(code: np.ndarray) -> list[np.ndarray]:
    h, w = code.shape
    return [code[r * h // 2 : (r + 1) * h // 2, c * w // 2 : (c + 1) * w // 2] for r in range(2) for c in range(2)]


def pad_to(code: np.ndarray, h: int, w: int) -> np.ndarray:
    out = np.zeros((h, w), dtype=code.dtype)
    out[: code.shape[0], : code.shape[1]] = code
    return out


def align(parts: list[np.ndarray], rows: slice = slice(None), feet: bool = False) -> list[np.ndarray]:
    """조각들을 첫 조각에 겹쳐(같은 픽셀이 가장 많게) 한 캔버스에 놓고, 모두의 둘레에 맞춰 자른다.

    feet 가 참이면 가로만 맞추고 세로는 각자의 발밑을 캔버스 바닥에 붙인다 (걷는 프레임).
    """
    margin = 24
    h = max(p.shape[0] for p in parts) + margin * 2
    w = max(p.shape[1] for p in parts) + margin * 2
    placed = []
    for part in parts:
        canvas = np.zeros((h, w), dtype=part.dtype)
        canvas[margin : margin + part.shape[0], margin : margin + part.shape[1]] = part
        if feet:
            bottom = np.flatnonzero(canvas.any(axis=1)).max()
            canvas = np.roll(canvas, h - margin - 1 - bottom, axis=0)
        placed.append(canvas)
    moved = [placed[0]]
    for canvas in placed[1:]:
        dy, dx = fine.best_shift(placed[0], canvas, 16, rows)
        moved.append(np.roll(np.roll(canvas, 0 if feet else dy, axis=0), dx, axis=1))
    filled = np.any([m > 0 for m in moved], axis=0)
    ys, xs = np.flatnonzero(filled.any(axis=1)), np.flatnonzero(filled.any(axis=0))
    return [m[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1] for m in moved]


def finish(code: np.ndarray, factor: int, radius: int, thin: int, floor: int, blob: int) -> np.ndarray:
    lines = [colour(c) for c in LINES]
    big = fine.smooth(code, factor) if factor > 1 else code
    if radius:
        big = fine.mode(big, radius)
    if thin:
        big = fine.thin(big, lines, thin, fine.blobs(code, lines, factor, blob), floor)
    return fine.unindex(big)


def write(name: str, code: np.ndarray, factor: int, radius: int, thin: int, native_dir: Path | None, floor: int = 1, blob: int = 2) -> None:
    """factor 배로 키우고(radius: 모서리 둥글림), 외곽선을 thin 번 깎아 floor px 까지 줄인다. blob 칸 넘게 뭉친 선 색은 면으로 보고 둔다."""
    out = finish(code, factor, radius, thin, floor, blob)
    save_rgba(out, OUT / f"{name}.png")
    if native_dir:
        save_rgba(fine.unindex(code), native_dir / f"{name}.png")
    print(name, out.shape[1], "x", out.shape[0])


def crop(code: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(code)
    return code[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]


def shift_rows(code: np.ndarray, rows: list[int], grow: bool) -> np.ndarray:
    """rows 의 줄을 한 번 더 넣거나(grow) 빼서 그 위쪽을 위/아래로 옮긴다. 캔버스 크기와 발밑은 그대로다."""
    keep = [y for y in range(code.shape[0]) if grow or y not in rows]
    if grow:
        keep = sorted(keep + rows)
    body = code[keep]
    out = np.zeros_like(code)
    if grow:
        out[:] = body[len(rows) :]
    else:
        out[len(rows) :] = body
    return out


def same_canvas(group: list[np.ndarray], pair: list[np.ndarray]) -> list[np.ndarray]:
    """pair = [group 의 첫 그림과 같은 그림, 다른 포즈]. 다른 포즈를 group 의 캔버스로 옮겨 붙여 돌려준다.

    캔버스는 가운데를 지키며 양쪽으로 똑같이 넓힌다 (코드가 발밑 가운데를 기준으로 놓기 때문이다).
    """
    def corner(code: np.ndarray) -> tuple[int, int]:
        ys, xs = np.nonzero(code)
        return int(ys.max()), int(xs.min())

    (by, bx), (py, px) = corner(group[0]), corner(pair[0])
    dy, dx = by - py, bx - px
    ys, xs = np.nonzero(pair[1])
    h, w = group[0].shape
    grow_x = max(0, -(int(xs.min()) + dx), int(xs.max()) + dx - (w - 1))
    grow_y = max(0, -(int(ys.min()) + dy))
    out = [np.pad(code, ((grow_y, 0), (grow_x, grow_x))) for code in group]
    moved = np.zeros_like(out[0])
    moved[ys + dy + grow_y, xs + dx + grow_x] = pair[1][ys, xs]
    return out + [moved]


def closed_eye(code: np.ndarray, box: tuple[int, int, int, int], skin: str, lid_row: int) -> None:
    """box(l, t, r, b, 끝 포함) 의 눈을 살색으로 덮고 lid_row 에 감은 눈 한 줄을 긋는다."""
    l, t, r, b = box
    code[t : b + 1, l : r + 1] = colour(skin)
    code[lid_row, l : r + 1] = colour(LINES[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", help="확대 전 그림도 이 폴더에 남긴다")
    args = parser.parse_args()
    native_dir = Path(args.native) if args.native else None
    if native_dir:
        native_dir.mkdir(parents=True, exist_ok=True)

    # 8컷의 고양이 (표정 4 + 눈 깜빡임). 깜빡임은 다시 받은 시트에서 눈 둘레만 옮긴다.
    cat_m = align(quarters(sheet("sprites/cat_medium", 10.24)) + [quarters(sheet("sprites/cat_medium_blink", 10.24))[0]])
    blink = cat_m[0].copy()
    blink[16:23, 15:41] = cat_m[4][16:23, 15:41]
    for name, code in zip(["bored", "glance", "sparkle", "smirk", "blink"], cat_m[:4] + [blink]):
        write(f"cat_m_{name}", code, 4, 2, 2, native_dir, floor=2)

    turtle_m = align(quarters(sheet("sprites/turtle_medium", 5.12)))
    for name, code in zip(["calm", "talk", "shock", "happy"], turtle_m):
        write(f"turtle_m_{name}", code, 2, 2, 1, native_dir, floor=2, blob=3)

    king = align(quarters(sheet("sprites/king_sheet", 5.12)))
    weak_blink, better_blink = king[2].copy(), king[3].copy()
    closed_eye(weak_blink, (43, 29, 51, 32), "#54A9A7", 32)
    closed_eye(weak_blink, (58, 29, 64, 32), "#54A9A7", 32)
    closed_eye(better_blink, (41, 29, 46, 34), "#54A9A7", 33)
    closed_eye(better_blink, (53, 29, 58, 34), "#54A9A7", 33)
    for name, code in zip(["sick", "cough", "weak", "better", "weak_blink", "better_blink"], king + [weak_blink, better_blink]):
        write(f"king_{name}", code, 2, 1, 1, native_dir)

    # 별주부: 서기·걷기는 머리를, 절은 발을 기준으로 선 자세에 맞춘다.
    small = quarters(sheet("sprites/turtle_small", 5.12))
    walk = quarters(sheet("sprites/turtle_walk", 5.12))
    turtle_l = align([small[0]] + walk, rows=slice(0, 72), feet=True)
    turtle_l = same_canvas(turtle_l, align([small[0], small[1]], rows=slice(-60, None), feet=True))
    # 걷는 시트의 그늘은 팔레트에서 회색으로 떨어진다. 선 자세와 같은 청록 그늘로 바꾼다.
    for code in turtle_l:
        code[code == colour("#546166")] = colour("#28706F")
        code[code == colour("#799088")] = colour("#439083")
    for name, code in zip(["stand", "walk_0", "walk_1", "walk_2", "walk_3", "bow"], turtle_l):
        write(f"turtle_l_{name}", code, 1, 1, 1, native_dir, blob=3)
    for name, code in zip(["swim_a", "swim_b"], align(small[2:])):
        write(f"turtle_l_{name}", code, 1, 1, 1, native_dir, blob=3)

    # 걷는 프레임과 서 있는 포즈는 같은 크기로 그린 두 시트에서 오고, 머리를 기준으로 한 캔버스에 맞춘다.
    cat_l = align(quarters(sheet("sprites/cat_walk", 10.24)) + quarters(sheet("sprites/cat_idle", 10.24)), rows=slice(0, 48), feet=True)
    # 시트의 윗줄(0·1)과 아랫줄(2·3)은 키가 달라 한 걸음에 한 번만 출렁인다. 디딜 때(0·2) 낮고 지날 때(1·3) 높게 줄을 넣고 뺀다.
    cat_l[1] = shift_rows(cat_l[1], [39, 41], grow=True)
    cat_l[2] = shift_rows(cat_l[2], [30, 32, 34], grow=False)
    # 걷는 프레임의 눈은 모델이 프레임마다 다르게 그려서(윙크, 십자) 선 자세의 얼굴을 옮겨 붙인다.
    stand_top = int(np.flatnonzero(cat_l[4].any(axis=1)).min())
    for i in range(4):
        dy = int(np.flatnonzero(cat_l[i].any(axis=1)).min()) - stand_top
        face, moved = (slice(13, 22), slice(11, 36)), (slice(13 + dy, 22 + dy), slice(11, 36))
        inside = (cat_l[i][moved] > 0) & (cat_l[4][face] > 0)
        cat_l[i][moved] = np.where(inside, cat_l[4][face], cat_l[i][moved])
    for i in (6, 7):
        cat_l[i] = shift_rows(cat_l[i], [39, 41, 43], grow=False)
    # 시트의 감은 눈은 선이 가늘어 격자에서 사라진다. 선 자세의 두 눈(2×2)을 한 줄로 바꿔 만든다.
    cat_l[5] = cat_l[4].copy()
    eyes = np.argwhere(np.isin(cat_l[4][14:20, 16:35], [colour(c) for c in LINES])) + [14, 16]
    top = int(eyes[:, 0].min())
    for y, x in eyes:
        cat_l[5][y, x] = cat_l[4][top - 1, x]
    for y, x in eyes:
        cat_l[5][top + 1, x - 1 : x + 2] = colour(LINES[0])
    for name, code in zip(["walk_0", "walk_1", "walk_2", "walk_3", "stand", "blink", "reach", "arms"], cat_l):
        write(f"cat_l_{name}", code, 2, 1, 1, native_dir)
    # 9컷의 맞잡는 손. 화면을 채우는 그림이라 여섯 배로 키운다. 왼쪽 절반이 고양이, 오른쪽 절반이 별주부다.
    hands = sheet("sprites/hands", 10.74, (0, 8))
    half = hands.shape[1] // 2
    write("hand_cat", hands[:, :half], 6, 3, 2, native_dir, floor=2)
    write("hand_turtle", hands[:, half:], 6, 3, 2, native_dir, floor=2)

if __name__ == "__main__":
    sys.exit(main())
