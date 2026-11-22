import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _common as common

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("target")
parser.add_argument("--merge-distance", type=float, required=True)
args = parser.parse_args(common.script_args())

common.load(args.source)
before = common.stats()
merged = sum(common.weld(obj, args.merge_distance, fix_normals=True) for obj in common.meshes())
common.base_to_origin()
baked = common.bake_transforms()
common.export_glb(args.target)
common.write_result(
    {
        "before": before,
        "after": common.stats(),
        "merged_vertices": merged,
        "baked_meshes": baked,
        "skinned_meshes_left_unbaked": len(common.meshes()) - baked,
    }
)
