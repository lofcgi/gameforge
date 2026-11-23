"""고양이의 대기 동작에 꼬리 흔들림과 귀 움찔을 더한다(서 있을 때 cat_idle, 낚싯대를 들고 앉았을 때 cat_sit_fish).

새로 그리지 않고 채택한 프레임의 픽셀을 옮긴다. 꼬리는 몸에서 떨어져 있는 왼쪽 덩어리를 줄마다 조금씩 밀어(끝으로 갈수록 크게) 흔들고,
귀는 왼쪽 귀 끝의 한 줄을 접어 한 칸 낮춘다. 원본 시트는 assets/raw/polish/cat_before/ 에 있다.

실행: uv run -q --project <harness>/tools python assets/raw/_tools/polish_cat.py  (게임 폴더에서)
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json, math
import numpy as np
import gfx

BEFORE = "assets/raw/polish/cat_before"
FRAMES = 16
W = 80


def frames_of(name):
    sheet = gfx.load(f"{BEFORE}/{name}.png")
    return [sheet[:, i * W:(i + 1) * W].copy() for i in range(sheet.shape[1] // W)]


def tail_rows(frame):
    """몸과 떨어져 있는 꼬리의 줄: {y: (x0, x1)}. 줄의 맨 왼쪽 덩어리 뒤에 빈칸이 있고 그 뒤에 몸이 있으면 꼬리다."""
    out = {}
    for y in range(30, 56):
        xs = np.nonzero(frame[y, :, 3])[0]
        if len(xs) == 0:
            continue
        x0 = int(xs[0])
        x1 = x0
        while x1 + 1 < W and frame[y, x1 + 1, 3]:
            x1 += 1
        if x1 < xs[-1] and x1 - x0 < 14 and x0 < 30:
            out[y] = (x0, x1)
    return out


def sway(frame, amp):
    """꼬리 끝(위쪽 줄)을 amp 칸까지 민다. 몸에 붙는 아래쪽 줄은 움직이지 않아 이어진 채로 휜다."""
    rows = tail_rows(frame)
    if not rows or amp == 0:
        return frame
    top, bottom = min(rows), max(rows)
    out = frame.copy()
    for y, (x0, x1) in rows.items():
        shift = int(round(amp * (bottom - y) / max(1, bottom - top)))
        if shift == 0:
            continue
        seg = frame[y, x0:x1 + 1].copy()
        out[y, x0:x1 + 1] = 0
        out[y, x0 + shift:x1 + 1 + shift] = seg
    return out


def ear_flick(frame):
    """왼쪽 귀 끝을 한 줄 접는다: 귀 맨 위 세 줄을 한 칸 내리고 넷째 줄을 덮는다."""
    ys, xs = np.nonzero(frame[..., 3])
    top = int(ys.min())
    tip = int(xs[ys == top].min())
    x0, x1 = tip - 3, tip + 3
    out = frame.copy()
    out[top + 1:top + 4, x0:x1] = frame[top:top + 3, x0:x1]
    out[top, x0:x1] = 0
    return out


def build(name, fps):
    stand, breathe, _, blink = frames_of(name)
    made = []
    for i in range(FRAMES):
        base = blink if i == 10 else (breathe if i in (4, 5, 6, 7, 12, 13, 14, 15) else stand)
        if i in (2, 3):
            base = ear_flick(base)
        made.append(sway(base, int(round(2 * math.sin(2 * math.pi * i / FRAMES)))))
    gfx.write_sheet(made, name, "assets/game/chars", fps=fps)
    return made


if __name__ == "__main__":
    allf = build("cat_idle", 6) + build("cat_sit_fish", 6)
    meta = json.loads((gfx.ROOT / f"{BEFORE}/cat.json").read_text())
    meta["rod_tip"]["sit_fish"] = [meta["rod_tip"]["sit_fish"][0]] * FRAMES
    (gfx.ROOT / "assets/game/chars/cat.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    gfx.contact(allf, "captures/assets/cat_idle_polish.png", scale=3, cols=8)
