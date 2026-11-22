"""Blender 안에서 도는 스크립트들의 공용 함수. gf 패키지는 Blender 의 Python 에 없으므로 쓰지 않는다."""

import json
import os
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector


def script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def write_result(data: dict) -> None:
    Path(os.environ["GF_RESULT"]).write_text(json.dumps(data))


def load(path: str) -> None:
    """빈 장면에 모델 파일 하나를 불러온다."""
    suffix = Path(path).suffix.lower()
    if suffix == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if suffix in (".glb", ".gltf"):
        # 뼈 모양 표시용 메시(아이코스피어)가 장면에 들어오면 삼각형 수와 크기 계산을 흐린다.
        bpy.ops.import_scene.gltf(filepath=path, disable_bone_shape=True)
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif suffix == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    else:
        raise SystemExit(f"지원하지 않는 형식이다: {suffix} (glb, gltf, fbx, obj, blend)")


def export_glb(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True)


def meshes() -> list:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def is_skinned(obj) -> bool:
    return any(modifier.type == "ARMATURE" for modifier in obj.modifiers)


def triangles(obj) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def bounds() -> tuple[Vector, Vector]:
    """모든 메시 정점의 월드 좌표 경계 (Blender 좌표: Z 가 위).

    뼈대에 묶인 메시는 원본 정점이 아니라 뼈대가 변형한 결과로 잰다. 리깅 모델은 원본 정점의
    단위가 달라(예: cm) 원본으로 재면 크기가 틀린다.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes():
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        local = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", local)
        evaluated.to_mesh_clear()
        matrix = np.array(evaluated.matrix_world)
        points.append(local.reshape(-1, 3) @ matrix[:3, :3].T + matrix[:3, 3])
    if not points or not sum(len(p) for p in points):
        raise SystemExit("장면에 메시가 없다.")
    merged = np.concatenate(points)
    return Vector(merged.min(axis=0).tolist()), Vector(merged.max(axis=0).tolist())


def _gltf(vector: Vector) -> list[float]:
    """Blender(Z 위, -Y 정면) 좌표를 GLB(Y 위, +Z 정면) 좌표로."""
    return [round(vector.x, 5), round(vector.z, 5), round(-vector.y, 5)]


def stats() -> dict:
    """GLB 좌표계(Y 위) 기준의 수치. 엔진에 들어갔을 때의 값과 같다."""
    low, high = bounds()
    size = high - low
    materials = sorted({slot.material.name for obj in meshes() for slot in obj.material_slots if slot.material})
    return {
        "warnings": [],
        "objects": len(meshes()),
        "triangles": sum(triangles(obj) for obj in meshes()),
        "vertices": sum(len(obj.data.vertices) for obj in meshes()),
        "bounds": {"min": _gltf(Vector((low.x, high.y, low.z))), "max": _gltf(Vector((high.x, low.y, high.z)))},
        "size": [round(size.x, 5), round(size.z, 5), round(size.y, 5)],
        "height": round(size.z, 5),
        "up": "Y",
        "materials": materials,
        "has_uv": all(len(obj.data.uv_layers) > 0 for obj in meshes()),
        "has_armature": any(obj.type == "ARMATURE" for obj in bpy.context.scene.objects),
        "animations": sorted(action.name for action in bpy.data.actions),
    }


def roots() -> list:
    return [obj for obj in bpy.context.scene.objects if obj.parent is None]


def transform_roots(matrix: Matrix) -> None:
    for obj in roots():
        obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()


def base_to_origin() -> None:
    """바닥 중심(가로 중앙, 가장 낮은 점)을 원점에 둔다. 엔진에서 발이 바닥에 닿는 기준이다."""
    low, high = bounds()
    transform_roots(Matrix.Translation((-(low.x + high.x) / 2, -(low.y + high.y) / 2, -low.z)))


def bake_transforms() -> int:
    """뼈대에 묶이지 않은 메시의 위치·회전·크기를 정점에 굽는다. 묶인 메시는 건드리면 스키닝이 깨진다."""
    targets = [obj for obj in meshes() if not is_skinned(obj)]
    if not targets:
        return 0
    bpy.ops.object.select_all(action="DESELECT")
    for obj in targets:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = targets[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for obj in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and not o.children]:
        bpy.data.objects.remove(obj)
    return len(targets)


def weld(obj, distance: float, fix_normals: bool = False) -> int:
    """겹친 정점을 합친다 (UV 는 면 모서리마다 따로 있어 유지된다). 합친 정점 수를 돌려준다.

    GLB 는 법선·UV 경계에서 정점을 갈라 저장하므로 불러온 메시는 면들이 서로 떨어져 있을 수 있다.
    """
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    before = len(mesh.verts)
    bmesh.ops.remove_doubles(mesh, verts=mesh.verts, dist=distance)
    if fix_normals:
        bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    merged = before - len(mesh.verts)
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    return merged
