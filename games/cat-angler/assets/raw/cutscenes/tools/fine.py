"""굵은 아트 픽셀로 그려진 원본을 화면 픽셀 굵기(1배)의 그림으로 다시 만든다.

원본의 격자대로 아트 픽셀 하나를 한 칸으로 되돌린 뒤(native), 가장자리를 따라 계단을 채우는
확대(scale2x/scale3x)를 정수배로 하고, 굵어진 외곽선을 안쪽에서 깎아 가늘게 만든다.
색은 팔레트의 색만 쓰고 알파는 0/255 다.
"""

import numpy as np



def index(image: np.ndarray) -> np.ndarray:
    """픽셀마다 색 번호 하나 (투명은 0)."""
    rgb = image[..., :3].astype(np.int64)
    code = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    return np.where(image[..., 3] > 0, code + 1, 0)


def unindex(code: np.ndarray) -> np.ndarray:
    out = np.zeros((*code.shape, 4), dtype=np.uint8)
    value = np.maximum(code - 1, 0)
    out[..., 0] = (value >> 16) & 255
    out[..., 1] = (value >> 8) & 255
    out[..., 2] = value & 255
    out[..., 3] = np.where(code > 0, 255, 0)
    return out


def _shift(a: np.ndarray, dy: int, dx: int) -> np.ndarray:
    padded = np.pad(a, 1, mode="edge")
    return padded[1 + dy : 1 + dy + a.shape[0], 1 + dx : 1 + dx + a.shape[1]]


def scale2x(e: np.ndarray) -> np.ndarray:
    b, d, f, h = _shift(e, -1, 0), _shift(e, 0, -1), _shift(e, 0, 1), _shift(e, 1, 0)
    ok = (b != h) & (d != f)
    out = np.zeros((e.shape[0] * 2, e.shape[1] * 2), dtype=e.dtype)
    out[0::2, 0::2] = np.where(ok & (d == b), d, e)
    out[0::2, 1::2] = np.where(ok & (b == f), f, e)
    out[1::2, 0::2] = np.where(ok & (d == h), d, e)
    out[1::2, 1::2] = np.where(ok & (h == f), f, e)
    return out


def scale3x(e: np.ndarray) -> np.ndarray:
    a, b, c = _shift(e, -1, -1), _shift(e, -1, 0), _shift(e, -1, 1)
    d, f = _shift(e, 0, -1), _shift(e, 0, 1)
    g, h, i = _shift(e, 1, -1), _shift(e, 1, 0), _shift(e, 1, 1)
    ok = (b != h) & (d != f)
    out = np.zeros((e.shape[0] * 3, e.shape[1] * 3), dtype=e.dtype)
    out[0::3, 0::3] = np.where(ok & (d == b), d, e)
    out[0::3, 1::3] = np.where(ok & (((d == b) & (e != c)) | ((b == f) & (e != a))), b, e)
    out[0::3, 2::3] = np.where(ok & (b == f), f, e)
    out[1::3, 0::3] = np.where(ok & (((d == b) & (e != g)) | ((d == h) & (e != a))), d, e)
    out[1::3, 1::3] = e
    out[1::3, 2::3] = np.where(ok & (((b == f) & (e != i)) | ((h == f) & (e != c))), f, e)
    out[2::3, 0::3] = np.where(ok & (d == h), d, e)
    out[2::3, 1::3] = np.where(ok & (((d == h) & (e != i)) | ((h == f) & (e != g))), h, e)
    out[2::3, 2::3] = np.where(ok & (h == f), f, e)
    return out


def smooth(code: np.ndarray, factor: int) -> np.ndarray:
    """정수배 확대. 2·3 의 곱으로 나눠 차례로 한다."""
    for step in {2: [2], 3: [3], 4: [2, 2], 6: [3, 2]}[factor]:
        code = scale2x(code) if step == 2 else scale3x(code)
    return code


def thin(code: np.ndarray, lines: list[int], rounds: int, keep: np.ndarray, floor: int = 1) -> np.ndarray:
    """외곽선(lines 의 색들)을 안쪽에서 깎아 floor px 까지 가늘게 한다.

    선이 아닌 이웃 색(투명은 아님)에 닿은 선 픽셀이 그 색이 된다. 바깥 윤곽은 그대로라 실루엣은
    변하지 않는다. 굵기가 floor 이하인 곳과 keep(눈동자처럼 선 색으로 칠한 면)은 건드리지 않는다.
    """
    for _ in range(rounds):
        for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            is_line = np.isin(code, lines)
            thick = np.minimum(_run_length(is_line, 1), _run_length(is_line, 0))
            neighbour = _shift(code, dy, dx)
            take = is_line & ~keep & ~np.isin(neighbour, lines) & (neighbour != 0) & (thick > floor)
            code = np.where(take, neighbour, code)
    return code


def blobs(code: np.ndarray, lines: list[int], factor: int, thick: int) -> np.ndarray:
    """선 색이 가로세로 모두 thick 칸 넘게 뭉친 곳(눈동자, 그림자)을 factor 배로 키운 마스크."""
    is_line = np.isin(code, lines)
    mask = np.minimum(_run_length(is_line, 1), _run_length(is_line, 0)) >= thick
    return np.kron(mask, np.ones((factor, factor), dtype=bool))


def _run_length(mask: np.ndarray, axis: int) -> np.ndarray:
    """mask 가 참인 픽셀마다 그 픽셀이 속한 연속 구간의 길이 (axis 방향)."""
    m = mask if axis == 1 else mask.T
    out = np.zeros(m.shape, dtype=np.int32)
    for y in range(m.shape[0]):
        row = m[y]
        edges = np.flatnonzero(np.diff(np.concatenate(([0], row.view(np.int8), [0]))))
        for start, end in zip(edges[0::2], edges[1::2]):
            out[y, start:end] = end - start
    return out if axis == 1 else out.T


def mode(code: np.ndarray, radius: int, rounds: int = 1) -> np.ndarray:
    """둥근 창 안에서 가장 많은 색으로 바꾼다. 확대 뒤에 남은 계단 모서리를 둥글린다 (제 색은 반 표를 더 받는다)."""
    ys, xs = np.mgrid[-radius : radius + 1, -radius : radius + 1]
    disk = (ys * ys + xs * xs) <= radius * radius + 1
    h, w = code.shape
    for _ in range(rounds):
        best = np.full(code.shape, -1.0, dtype=np.float32)
        out = code.copy()
        for value in np.unique(code):
            own = (code == value).astype(np.float32)
            padded = np.pad(own, radius, mode="edge")
            count = own * 0.5
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if disk[dy + radius, dx + radius]:
                        count = count + padded[radius + dy : radius + dy + h, radius + dx : radius + dx + w]
            take = count > best
            best[take] = count[take]
            out[take] = value
        code = out
    return code


def best_shift(base: np.ndarray, other: np.ndarray, reach: int, rows: slice = slice(None)) -> tuple[int, int]:
    """other 를 (dy, dx) 만큼 옮겼을 때 base 와 같은 픽셀이 가장 많은 이동량. 둘은 같은 크기의 색 번호 배열."""
    best, found = -1, (0, 0)
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            moved = np.roll(np.roll(other, dy, axis=0), dx, axis=1)
            same = int(((moved[rows] == base[rows]) & (base[rows] > 0)).sum())
            if same > best or (same == best and abs(dy) + abs(dx) < abs(found[0]) + abs(found[1])):
                best, found = same, (dy, dx)
    return found
