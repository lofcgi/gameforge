"""spec 의 겹 규칙대로 바다 화면을 합성해 본다(게임 캡처 전의 확인용)."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import json
import numpy as np
import gfx

def tile(img, w):
    reps = -(-w // img.shape[1])
    return np.concatenate([img] * reps, axis=1)[:, :w]

def scene(zone, boat, horizon=198, bed_depth=120, cam=0, out=None, fish=()):
    S = "assets/game/sea/"
    a = np.zeros((360, 640, 4), dtype=np.uint8); a[..., 3] = 255
    sky = gfx.load(S + f"sky_{zone}.png"); a = gfx.over(a, sky, 0, horizon - 200 - cam)
    for layer, dx in (("far", 40), ("mid", 150)):
        im = gfx.load(S + f"{layer}_{zone}.png"); im = np.roll(im, dx, axis=1)
        a = gfx.over(a, tile(im, 640), 0, horizon - im.shape[0] - cam)
    pat = tile(gfx.load(S + "surface_pattern.png"), 640)
    a = gfx.over(a, pat, 0, horizon - 32 - cam)
    b = gfx.load(f"assets/game/boats/{boat}.png"); bj = json.loads(open(gfx.ROOT / f"assets/game/boats/{boat}.json").read())
    bx, by = 320 - b.shape[1] // 2, horizon - bj["waterline"] - cam
    cat = gfx.load("assets/game/chars/cat_sit_fish.png")[:, :80]
    a = gfx.over(a, b, bx, by)
    a = gfx.over(a, cat, bx + bj["seat"][0] - 40, by + bj["seat"][1] - 59)
    und = gfx.load(S + f"under_{zone}.png"); a = gfx.over(a, und, 0, horizon - cam)
    tipx, tipy = bx + bj["rod_tip"][0], by + bj["rod_tip"][1]
    for y in range(max(0, tipy), min(360, horizon - cam + bed_depth - 30)):
        a[y, tipx, :3] = (0xE5, 0xDD, 0xC8)
    bed = tile(gfx.load(S + f"bed_{zone}.png"), 640)
    a = gfx.over(a, bed, 0, horizon - cam + bed_depth - 10)
    yb = horizon - cam + bed_depth + 54
    if yb < 360:
        a[yb:, :, :3] = bed[-1, 0, :3]
    for name, x, y in fish:
        f = gfx.load(f"assets/game/fish/{name}_swim.png"); fw = f.shape[1] // 4
        a = gfx.over(a, f[:, :fw], x, y - cam)
    gfx.save(a, out)

if __name__ == "__main__":
    scene("shallow", "boat1", out="captures/assets/preview_shallow.png", fish=[("anchovy", 90, 215), ("anchovy", 120, 222), ("scad", 420, 250), ("scad", 200, 262), ("flounder", 470, 300), ("anchovy", 520, 228)])
    scene("open", "boat2", bed_depth=320, cam=150, out="captures/assets/preview_open.png", fish=[("mackerel", 90, 235), ("bream", 420, 360), ("amberjack", 150, 420), ("moray", 430, 470)])
    scene("deep", "boat3", bed_depth=600, cam=420, out="captures/assets/preview_deep.png", fish=[("hairtail", 90, 480), ("angler", 420, 640), ("oarfish", 150, 700), ("legend", 380, 690)])
