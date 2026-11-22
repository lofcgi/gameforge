"""목표 지점에 세우는 등불 기둥. 원점은 바닥 중심, 화살표 팻말이 정면(Blender -Y = GLB +Z)을 본다."""
import json
import os
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]
HEIGHT = 2.6

bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb, glow=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = 0.8
    if glow:
        shader.inputs["Emission Color"].default_value = (*rgb, 1.0)
        shader.inputs["Emission Strength"].default_value = glow
    return mat


def box(name, size, location, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    return obj


wood = material("wood", (0.33, 0.20, 0.10))
stone = material("stone", (0.35, 0.38, 0.42))
light = material("light", (1.0, 0.78, 0.25), glow=3.0)
teal = material("teal", (0.10, 0.55, 0.55))

box("base", (0.7, 0.7, 0.25), (0, 0, 0.125), stone)
box("post", (0.18, 0.18, HEIGHT - 0.6), (0, 0, 0.25 + (HEIGHT - 0.6) / 2), wood)
box("cap", (0.5, 0.5, 0.1), (0, 0, HEIGHT - 0.3), wood)
box("lamp", (0.36, 0.36, 0.36), (0, 0, HEIGHT - 0.52), light)
box("sign", (0.7, 0.06, 0.3), (0, -0.12, 1.5), teal)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True)

if os.environ.get("GF_RESULT"):
    with open(os.environ["GF_RESULT"], "w") as handle:
        json.dump({"files": [out]}, handle)
