# Blender 빌드 스크립트 쓰는 법

모델 하나 = 스크립트 하나. 스크립트가 모델의 원본이다. GLB 는 언제든 다시 만들 수 있는 결과물이다.

## 실행

```sh
$GF blender run tools/models/crate.py -- assets/game/models/crate.glb
```

- Blender 가 화면 없이(`-b --factory-startup`) 스크립트를 실행한다. `--` 뒤의 인자는 스크립트의 `sys.argv` 에서 `--` 뒤로 들어온다.
- 작업 폴더는 게임 폴더다. 상대 경로는 게임 폴더 기준이다.
- 스크립트가 환경변수 `GF_RESULT` 가 가리키는 파일에 JSON 을 쓰면 그 내용이 명령 결과의 `result` 와 `files` 로 나온다. 쓰지 않아도 실행은 된다.
- 스크립트가 예외로 끝나면 명령이 실패하고 Blender 출력의 끝부분이 오류에 나온다.

## 틀

```python
import json
import os
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]

# 빈 장면에서 시작한다
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1.0)
    return mat


def box(name, size, location, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    return obj


wood = material("wood", (0.45, 0.30, 0.16))
box("body", (1.0, 1.0, 1.0), (0, 0, 0.5), wood)      # Blender 는 Z 가 위. 바닥이 z=0 이 되게 놓는다

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True)

if os.environ.get("GF_RESULT"):
    with open(os.environ["GF_RESULT"], "w") as handle:
        json.dump({"files": [out]}, handle)
```

## 규칙

- 치수는 미터. 원점은 바닥 중심(발밑). Blender 안에서는 Z 가 위이고, GLB 로 내보내면 Y 가 위가 된다. **정면은 Blender 의 -Y 쪽**으로 만든다(GLB 에서 +Z 가 되고, 하네스의 규약이 "GLB 정면 = +Z"다). 턴테이블 0번에 정면이 보이면 맞다.
- 색은 `design/palette.json` 의 값만 쓴다. 스크립트 위쪽에 상수로 모아 둔다.
- 숫자(크기, 개수, 시드)는 스크립트 위쪽 상수로 뺀다. 변형(큰 상자, 작은 상자)은 인자로 받는다.
- 난수는 `random.seed(<고정값>)` 뒤에 쓴다. 다시 만들어도 같은 모델이 나와야 한다.
- 삼각형 예산을 지킨다: 곡면의 분할 수(`segments`, `vertices`)를 낮게 시작한다. 만든 뒤 `$GF blender info <glb>` 로 센다.
- 만든 GLB 를 손으로 고치지 않는다. 고칠 것이 있으면 스크립트를 고쳐 다시 만든다.
- 생성 모델을 스크립트에서 불러와 손보는 것도 된다(`bpy.ops.import_scene.gltf(filepath=...)`). 단순한 정리·감량·크기 맞춤은 `blender clean/decimate/rescale` 을 쓴다.

## 확인

```sh
$GF blender info assets/game/models/crate.glb
$GF blender turntable assets/game/models/crate.glb --out captures/turntable --count 4 --size 512 --elevation 20
```

모음판을 Read 로 보고, 게임에 넣은 뒤에는 게임 카메라의 스크린샷으로 다시 본다.
