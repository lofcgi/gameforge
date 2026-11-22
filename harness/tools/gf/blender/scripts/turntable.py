import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import _common as common

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("out_dir")
parser.add_argument("--name", required=True)
parser.add_argument("--count", type=int, required=True)
parser.add_argument("--size", type=int, required=True)
parser.add_argument("--elevation", type=float, required=True)
args = parser.parse_args(common.script_args())

common.load(args.source)
scene = bpy.context.scene
# Blender 4.2~4.5 는 EEVEE 를 BLENDER_EEVEE_NEXT 라고 부른다.
available = [item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items]
scene.render.engine = next(name for name in available if name.startswith("BLENDER_EEVEE"))
scene.render.resolution_x = scene.render.resolution_y = args.size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
# 배경은 투명하게 두고 색은 텍스처 그대로 보이게 한다 (기본 뷰 변환은 채도를 낮춘다).
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("gf_world")
world.use_nodes = True
background = world.node_tree.nodes["Background"]
background.inputs["Color"].default_value = (1, 1, 1, 1)
background.inputs["Strength"].default_value = 0.45
scene.world = world

low, high = common.bounds()
centre = (low + high) / 2
radius = (high - low).length / 2

camera = bpy.data.objects.new("gf_camera", bpy.data.cameras.new("gf_camera"))
sun = bpy.data.objects.new("gf_sun", bpy.data.lights.new("gf_sun", "SUN"))
sun.data.energy = 3.0
scene.collection.objects.link(camera)
scene.collection.objects.link(sun)
scene.camera = camera
distance = radius / math.sin(camera.data.angle / 2) * 1.02
camera.data.clip_start = distance / 100
camera.data.clip_end = distance * 10

elevation = math.radians(args.elevation)
files = []
for index in range(args.count):
    # 0번은 정면(Blender 의 -Y 쪽에서 본 모습)이고 위에서 볼 때 반시계 방향으로 돈다.
    angle = 2 * math.pi * index / args.count
    offset = Vector((math.sin(angle) * math.cos(elevation), -math.cos(angle) * math.cos(elevation), math.sin(elevation)))
    camera.location = centre + offset * distance
    camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()
    # 빛은 카메라 왼쪽 위에서 비춰 어느 각도에서도 형태가 읽히게 한다.
    key = offset + Vector((-offset.y, offset.x, 0)) * 0.5 + Vector((0, 0, 0.6))
    sun.rotation_euler = (-key).to_track_quat("-Z", "Y").to_euler()
    path = str(Path(args.out_dir) / f"{args.name}_{index:02d}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    files.append(path)

common.write_result({"files": files, "engine": scene.render.engine, "stats": common.stats()})
