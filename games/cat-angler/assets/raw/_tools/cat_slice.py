"""고양이 자세 시트 3장을 1x 조각으로 나눠 assets/raw/parts/cat 에 둔다."""
import sys; sys.path.insert(0, "assets/raw/_tools")
import numpy as np
import gfx

# 고양이에 쓰는 색만 남긴다. 회색·연두가 입과 수염 자리에 박히는 것을 막는다.
CAT = ["#17121B", "#1B2139", "#2E3068", "#5E342B", "#8C533C", "#B4774F", "#D79966", "#DFB68B", "#E5DDC8", "#E9F3E2", "#28706F", "#439083"]
CAT_PAL = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in CAT], dtype=np.int32)

sheets = {
    "fish": ("assets/raw/cat/cat_poses_fish.png", 2, 2, ["stand", "sit", "reel", "strain"]),
    "land": ("assets/raw/cat/cat_poses_land.png", 2, 2, ["stand2", "cheer", "sad", "pick"]),
    "walk": ("assets/raw/cat/cat_walk_strip.png", 6, 1, [f"walk{i}" for i in range(6)]),
}
if __name__ == "__main__":
    for key, (raw, c, r, names) in sheets.items():
        # 걷기 시트에는 선 자세 칸이 없다. 걷는 자세의 키는 선 자세와 같다고 본다.
        frames = gfx.sheet_to_frames(raw, c, r, ref_height=52, work=f"assets/raw/work/cat_{key}", colours=CAT_PAL)
        for n, f in zip(names, frames):
            gfx.save(f, f"assets/raw/parts/cat/{n}.png")
