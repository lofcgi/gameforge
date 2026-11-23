"""별주부·용왕 스프라이트 시트와 고양이·별주부·용왕 초상화를 만든다.

자세는 컷신 쪽 디자인(assets/raw/cutscenes/designs)을 참조로 한 이미지 편집으로 받고, 숨쉬기는 여기서 윗부분을 1px 내려 만든다.
"""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
import gfx

WORK = "assets/raw/work/story"


def breathe(a, rows):
    out = a.copy()
    top = a[:rows].copy()
    out[:1] = 0
    block = out[1:rows + 1]
    m = top[..., 3] > 0
    block[m] = top[m]
    return out


def base_x(a, rows=4):
    xs = np.nonzero(a[-rows:, :, 3])[1]
    return (xs.min() + xs.max() + 1) / 2


def turtle():
    stand, wa, wb, bow = gfx.sheet_to_frames("assets/raw/story/turtle_poses.png", 2, 2, ref_height=44, work=f"{WORK}/turtle")
    put = lambda a: gfx.place(a, (48, 48), (24, 47), base_x(a, 3))
    b = breathe(stand, 22)
    gfx.write_sheet([put(stand), put(b), put(stand), put(b)], "turtle_idle", "assets/game/chars", fps=3)
    gfx.write_sheet([put(wa), put(stand), put(wb), put(stand)], "turtle_walk", "assets/game/chars", fps=7)
    gfx.write_sheet([put(stand), put(bow)], "turtle_bow", "assets/game/chars", fps=3, loop=False)
    return [put(stand), put(b), put(wa), put(wb), put(bow)]


def king():
    keyed = gfx.chroma("assets/raw/story/king_poses2.png", f"{WORK}/king/keyed")
    widest = max(p.shape[1] for p in gfx.split_full(keyed, 2, 2))
    ill1, ill2, ok1, ok2 = gfx.sheet_to_frames("assets/raw/story/king_poses2.png", 2, 2, ref_height=0, cell=widest / 94, work=f"{WORK}/king")
    put = lambda a: gfx.place(a[-96:], (96, 96), (48, 95), base_x(a, 6))
    gfx.write_sheet([put(ill1), put(breathe(ill1, 40)), put(ill2), put(breathe(ill1, 40))], "king_idle", "assets/game/chars", fps=2)
    gfx.write_sheet([put(ok1), put(breathe(ok1, 40)), put(ok2), put(breathe(ok2, 40))], "king_better", "assets/game/chars", fps=3)
    return [put(ill1), put(ill2), put(ok1), put(ok2)]


def portrait(raw, name, crop=None):
    """초상화: 배경을 빼고 긴 변을 96 으로 맞춰 아래 가운데에 놓는다."""
    keyed = gfx.load(gfx.chroma(raw, f"{WORK}/portrait/keyed"))
    if crop:
        keyed = keyed[crop[1]:crop[3], crop[0]:crop[2]]
    part = gfx.trim(keyed)
    f = gfx.save(part, f"{WORK}/portrait/{name}_src.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{WORK}/portrait/pixel", cell=max(part.shape[:2]) / 96)
    a = gfx.trim(gfx.quantize(gfx.load(snapped)))[:96, :96]
    out = gfx.place(a, (96, 96), (48, 96))
    gfx.save(out, f"assets/game/portraits/{name}.png")
    return out


if __name__ == "__main__":
    t, k = turtle(), king()
    p = [portrait("assets/raw/story/portrait_cat.png", "cat"),
         portrait("assets/raw/story/portrait_turtle.png", "turtle", crop=(230, 90, 800, 660)),
         portrait("assets/raw/story/portrait_king.png", "king")]
    gfx.contact(t + k + p, "captures/assets/story_chars.png", scale=2, cols=6, bg=((233, 243, 226), (46, 48, 104)))
