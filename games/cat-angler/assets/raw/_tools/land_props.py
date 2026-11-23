"""마을 소품 시트를 덩어리별로 나눠 assets/raw/parts/land/prop_N.png 로 둔다."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
import gfx
from land_lib import RAW, clean_specks

WORK = "assets/raw/work/land_props"
CELL = 9.4
keyed = gfx.chroma(f"{RAW}/town_props.png", f"{WORK}/keyed")
a = gfx.load(keyed)
small = a[::4, ::4, 3] > 0
comps = [c for c in gfx.components(small, 1) if c.sum() > 150]
comps.sort(key=lambda c: (np.nonzero(c)[1].min() // 60, np.nonzero(c)[0].min()))
out = []
for i, c in enumerate(comps):
    big = np.kron(c, np.ones((4, 4), dtype=bool))[: a.shape[0], : a.shape[1]]
    part = a.copy(); part[~big] = 0
    f = gfx.save(gfx.trim(part), f"{WORK}/parts/p{i}.png")
    snapped, _ = gfx.snap(str(f.relative_to(gfx.ROOT)), f"{WORK}/pixel", cell=CELL)
    s = clean_specks(gfx.trim(gfx.quantize(gfx.load(snapped))))
    gfx.save(s, f"assets/raw/parts/land/prop_{i}.png")
    print(i, s.shape[1], s.shape[0])
    out.append(s)
gfx.contact(out, "captures/assets/land__props.png", scale=2)
