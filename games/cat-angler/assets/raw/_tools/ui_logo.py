"""타이틀 로고. 글자는 Galmuri11 Bold 를 12px 로 찍어 4배로 키우고(모델은 한글을 틀리게 그린다),
아래에 겹친 반원 물결 띠, 왼쪽 위에 고양이 머리(게임 스프라이트의 머리를 2배)를 얹는다."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import gfx

H = lambda c: (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255)
TEXT, S = "고양이 낚시꾼", 4
font = ImageFont.truetype(str(gfx.ROOT / "assets/game/fonts/Galmuri11-Bold.ttf"), 12)
box = font.getbbox(TEXT)
im = Image.new("L", (box[2] + 2, box[3] + 2), 0)
ImageDraw.Draw(im).text((1, 1), TEXT, font=font, fill=255)
m = np.array(im) > 127
ys, xs = np.nonzero(m)
m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
big = np.kron(m, np.ones((S, S), dtype=bool))
th, tw = big.shape


def grow(mask, r):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if abs(dx) + abs(dy) <= r + r // 2:
                out |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


W, HH = 384, 150
canvas = np.zeros((HH, W, 4), dtype=np.uint8)
tx, ty = (W - tw) // 2 + 8, 58
full = np.zeros((HH, W), dtype=bool)
full[ty:ty + th, tx:tx + tw] = big
outline = grow(full, 4)
shadow = np.roll(outline, 4, 0)
canvas[shadow] = H("#17121B")
canvas[outline] = H("#5E342B")
canvas[full] = H("#E9F3E2")
# 글자 아래 절반은 한 단계 어두운 종이색, 맨 윗줄 한 칸은 물색 반짝임
low = full.copy(); low[: ty + th * 5 // 8] = False
canvas[low] = H("#E5DDC8")
# 물결 띠: 반지름 12 의 겹친 반원이 두 줄로 어긋나게
band_y, R = ty + th + 14, 12
rings = [H("#E5DDC8"), H("#28706F"), H("#54A9A7"), H("#439083"), H("#E5DDC8"), H("#28706F"), H("#54A9A7"), H("#439083"), H("#E5DDC8"), H("#28706F"), H("#54A9A7"), H("#439083")]
for row, off in ((1, R), (0, 0)):
    cy = band_y + R + row * 0 + (0 if row else 8)
    for cx in range(40 + off, W - 40, 2 * R):
        for y in range(-R, 1):
            for x in range(-R, R + 1):
                d = (x * x + y * y) ** 0.5
                if d <= R and 0 <= cy + y < HH:
                    canvas[cy + y, cx + x] = rings[min(11, int(R - d))]
# 띠 아래를 곧게 자르고 어두운 줄로 닫는다
base = band_y + R + 8
canvas[base + 1:] = 0
xs = np.nonzero(canvas[base, :, 3])[0]
canvas[base, xs.min():xs.max() + 1] = H("#194A50")
# 고양이 머리
head = gfx.load("assets/raw/parts/cat/stand.png")[:27]
head = gfx.trim(head)
head2 = np.kron(head, np.ones((2, 2, 1), dtype=np.uint8))
canvas = gfx.over(canvas, head2, tx - 34, ty - 50)
out = gfx.quantize(canvas)
out = gfx.trim(out)
gfx.save(out, "assets/game/ui/logo.png")
bg = np.zeros_like(out); bg[..., :3] = (186, 234, 220); bg[..., 3] = 255
gfx.save(gfx.over(bg, out), "captures/assets/ui_logo.png")
print(out.shape)
