import argparse
import math
import sys
from pathlib import Path

from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).parent))
import _common as common

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("target")
parser.add_argument("--height", type=float, required=True)
parser.add_argument("--turn", type=float, required=True)
args = parser.parse_args(common.script_args())

common.load(args.source)
before = common.stats()
if before["height"] <= 0:
    raise SystemExit("모델의 높이가 0 이라 크기를 맞출 수 없다.")
scale = args.height / before["height"]
# 위쪽 축(Blender 의 Z) 둘레로 돌린다. 내보낼 때 Blender 의 -Y 가 GLB 의 +Z 가 되고,
# 하네스의 규약에서 GLB 의 +Z 가 모델의 정면이다 (templates/README.md 7절). +X 를 보는 모델은 -90 으로 맞춘다.
common.transform_roots(Matrix.Rotation(math.radians(args.turn), 4, "Z") @ Matrix.Scale(scale, 4))
common.base_to_origin()
baked = common.bake_transforms()
common.export_glb(args.target)
common.write_result({"before": before, "after": common.stats(), "scale": round(scale, 6), "baked_meshes": baked})
