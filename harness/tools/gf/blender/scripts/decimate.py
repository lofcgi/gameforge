import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).parent))
import _common as common

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("target")
parser.add_argument("--triangles", type=int, required=True)
args = parser.parse_args(common.script_args())

common.load(args.source)
before = common.stats()
ratio = min(1.0, args.triangles / before["triangles"])
if ratio < 1.0:
    for obj in common.meshes():
        # 면들이 떨어진 채로 줄이면 구멍이 난다.
        common.weld(obj, 1e-6)
        bpy.context.view_layer.objects.active = obj
        # Collapse 방식은 UV 와 정점 가중치를 보간해 유지한다.
        modifier = obj.modifiers.new("gf_decimate", "DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = ratio
        bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
common.export_glb(args.target)
common.write_result({"before": before, "after": common.stats(), "ratio": round(ratio, 5)})
