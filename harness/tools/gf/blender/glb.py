"""Blender 없이 GLB 를 읽는다 (trimesh + GLB 헤더의 JSON)."""

import json
import struct
from pathlib import Path

import trimesh

from gf.core.output import GfError


def read_json(path: Path) -> dict:
    """GLB 의 첫 청크(JSON)를 읽는다. 뼈대와 애니메이션 유무는 여기에만 있다."""
    with path.open("rb") as handle:
        magic, _version, _length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF":
            raise GfError(f"GLB 파일이 아니다: {path}")
        chunk_length, chunk_type = struct.unpack("<I4s", handle.read(8))
        if chunk_type != b"JSON":
            raise GfError(f"GLB 의 첫 청크가 JSON 이 아니다: {path}")
        return json.loads(handle.read(chunk_length))


def stats(path: Path) -> dict:
    if path.suffix.lower() != ".glb":
        raise GfError(f"trimesh 백엔드는 .glb 만 읽는다: {path.name}. 다른 형식은 Blender 가 필요하다.")
    document = read_json(path)
    scene = trimesh.load(path, force="scene", process=False)
    merged = scene.to_geometry() if hasattr(scene, "to_geometry") else scene.dump(concatenate=True)
    low, high = (merged.bounds[0], merged.bounds[1])
    size = high - low
    warnings = []
    if document.get("skins"):
        warnings.append("뼈대가 있는 모델이다. trimesh 는 뼈대의 변형을 적용하지 않아 크기가 실제와 다를 수 있다. Blender 백엔드로 확인한다.")
    return {
        "warnings": warnings,
        "objects": len(scene.graph.nodes_geometry),
        "triangles": len(merged.faces),
        "vertices": len(merged.vertices),
        "bounds": {"min": [round(float(v), 5) for v in low], "max": [round(float(v), 5) for v in high]},
        "size": [round(float(v), 5) for v in size],
        "height": round(float(size[1]), 5),
        "up": "Y",
        "materials": sorted(m.get("name", f"material_{i}") for i, m in enumerate(document.get("materials", []))),
        "has_uv": all("TEXCOORD_0" in p["attributes"] for m in document.get("meshes", []) for p in m["primitives"]),
        "has_armature": bool(document.get("skins")),
        "animations": sorted(a.get("name", f"animation_{i}") for i, a in enumerate(document.get("animations", []))),
    }
