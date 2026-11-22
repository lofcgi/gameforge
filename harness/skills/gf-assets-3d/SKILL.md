---
name: gf-assets-3d
description: 게임용 3D 모델, GLB, 메시, 텍스처, 셰이더, 리깅, 3D 캐릭터·소품·환경을 만들어 달라거나 "모델이 너무 무겁다/방향이 틀리다/크기가 안 맞는다"를 고쳐 달라는 요청에는, 코드를 짜거나 생성 명령을 바로 부르기 전에 먼저 이 스킬을 쓴다. gameforge 의 assets 단계, 3D 스타일(style=3d-code 또는 3d-gen): 코드 생성 경로(셰이더, 절차 지오메트리, Blender Python 빌드 스크립트)와 생성 모델 경로(A-포즈·4면 컨셉 이미지 → 3D 모델 → Blender 정리·감량·크기 맞춤·턴테이블 → 선택적 리깅)로 모델을 만들어 게임에 넣는다.
---

# 3D 에셋: 인물이 필요한가, 카메라가 얼마나 가까운가로 길을 고른다

| 길 | 잘 되는 것 | 약한 것 |
|---|---|---|
| **A. 코드 생성** (`3d-code`) | 풍경, 추상, 기계, 탈것, 건물, 이펙트. 에셋 파일 0개로도 된다 | 인물, 유기적인 형태 |
| **B. 생성 모델** (`3d-gen`) | 스타일이 뚜렷한 캐릭터·소품을 **멀리서** 볼 때 | 가까이서 보면 "AI 티", 삼각형이 과다, 엄격한 폴리 예산 |

두 길을 섞어도 된다(환경은 코드, 주인공만 생성). **3D 인물 애니메이션은 가장 약한 고리다.** 걷기 하나에도 여러 번 반려가 난다. 필요하면 카메라를 멀리 두고, 프리셋 걷기·달리기로 만족하거나, 인물을 탈것·로봇·생물로 바꾸는 안을 사용자에게 먼저 제안한다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 준비

`design/art-direction.md` 의 삼각형 예산, 단위(1 = 1 m), 카메라 거리를 확인한다. 모델 목록(이름, 키, 화면에서의 크기, 움직이는가)을 사용자에게 보여 주고 주인공 **하나**를 게임 안 스크린샷까지 통과시킨 뒤 나머지를 만든다.

## A. 코드 생성

"생성된 장면이 아니라 생성기를 고친다." 결과 파일을 손으로 만지지 않고, 만드는 코드를 고쳐 다시 만든다.

- **엔진 안에서**: 도형 조합, 절차 지오메트리, 셰이더로 그린다. web-3d 는 `three/webgpu` 렌더러이므로 셰이더는 TSL(`three/tsl`)로 쓴다. GLSL `ShaderMaterial` 은 동작하지 않는다. Godot 은 `.gdshader` 와 `ArrayMesh`/CSG.
- **Blender 빌드 스크립트**: 모델 하나당 Python 스크립트 하나를 `tools/models/<이름>.py`(게임 폴더 안)에 두고 GLB 를 내보낸다. 작성 규칙과 예시는 `${CLAUDE_SKILL_DIR}/blender-build.md`.

  ```sh
  $GF blender run tools/models/<이름>.py -- assets/game/models/<이름>.glb
  $GF blender info assets/game/models/<이름>.glb
  $GF blender turntable assets/game/models/<이름>.glb --out captures/turntable --count 4
  ```

턴테이블 모음판(결과의 `sheet`)을 Read 로 보고 형태·비율·색을 확인한다. 고칠 것은 스크립트에서 고친다.

## B. 생성 모델

텍스트에서 바로 3D 를 만들지 않는다. **컨셉 이미지에서 출발**한다.

```sh
# 1. 컨셉: 전신, A-포즈(팔을 살짝 벌림), 정면, 단색 배경, 그림자·바닥 없음. 기준 화면을 참조로
$GF gen edit "a new character in the art style of the reference image: <대상>, full body, neutral A-pose, front view, centered, flat solid pure green #00FF00 background, no shadow, no ground, no text" \
  --image design/look/frame.png --aspect 1:1 --resolution 1K --out assets/raw/concept --name <이름>

# 2. 이미지 → 3D. 비용을 미리 계산할 수 없는 모델이라 --estimate-usd 가 없으면 호출이 거부된다 (실측 약 $0.5)
$GF gen model3d assets/raw/concept/<이름>.png --face-limit 8000 --no-pbr \
  --estimate-usd 0.5 --max-usd 1.0 --out assets/raw/models --name <이름>

# 3. 무엇이 나왔는지 숫자로 본다 (삼각형, 크기, 재질, 뼈대)
$GF blender info assets/raw/models/<결과 GLB>

# 4. 정리 → 감량 → 크기와 방향
$GF blender clean assets/raw/models/<결과 GLB> --out assets/raw/models/<이름>_clean.glb
$GF blender decimate assets/raw/models/<이름>_clean.glb --triangles 3000 --out assets/raw/models/<이름>_low.glb
$GF blender rescale assets/raw/models/<이름>_low.glb --height 1.2 --turn -90 --out assets/game/models/<이름>.glb

# 5. 턴테이블로 본다
$GF blender turntable assets/game/models/<이름>.glb --out captures/turntable --count 4
```

- 1단계: 컨셉을 사용자에게 보여 주고 승인받은 뒤 3D 로 넘긴다(3D 가 더 비싸다). 뒤·옆모습이 중요하면 같은 캐릭터의 4면 시트(front, side, back)를 `gen edit --image <정면>` 으로 만들어 뒤가 어떻게 생겼는지 사람이 먼저 정한다. 소품은 A-포즈 대신 3/4 시점 단일 물체로.
- 2단계: 결과 `files` 에 GLB 와 미리보기 이미지가 나온다. 파일 이름은 결과에서 읽는다(예: `<이름>_model_mesh.glb`). `--pbr`, `--quad` 는 꼭 필요할 때만(비용·용량이 는다).
- 4단계 `decimate`: 실측으로 8,072 → 2,999 삼각형에서 텍스처가 유지됐다. 목표는 art-direction 의 예산. 감량 뒤 턴테이블에서 형태가 무너졌으면 목표를 올린다.
- 4단계 `rescale --turn -90`: **생성 모델은 +X 를 보고 나온다(실측 2회).** `--turn -90` 이 정면을 +Z 로 돌린다. 키는 `--height`(미터)로, 원점은 발밑 중심으로 맞춰진다. `--height` 는 템플릿의 충돌 캡슐 키(기본 1.8)에 맞춘다.
- **방향 규약은 하나다: GLB 의 정면은 +Z, 턴테이블 0번이 정면.** 두 3D 템플릿이 모델의 +Z 를 이동 방향으로 돌린다(하네스의 `templates/README.md` 7절). 0번에 얼굴이 보이면 게임에서도 맞다. 0번이 옆이나 뒤면 `--turn` 을 90° 단위로 바꿔 다시 내보낸다. 게임 코드에서 돌려 맞추지 않는다. 2026-11-22 에 Godot 과 three.js 양쪽에서 앞·뒤·좌·우 이동 스크린샷으로 확인했다.

턴테이블 모음판을 Read 로 본다: 0번이 정면인가, 뒤통수·등이 뭉개지지 않았나, 텍스처가 번지지 않았나, 좌우가 심하게 비대칭이 아닌가. 가까이서 본 결함이 게임 카메라 거리에서 보이는지는 게임 안 스크린샷으로 판단한다.

## 리깅 (움직이는 인물형만, 선택)

1회 **$0.80** 이다. 실행 전에 금액을 사용자에게 말한다. 감량·크기 맞춤이 끝난 모델을 넣는다.

```sh
$GF gen rig assets/game/models/<이름>.glb --height 1.2 --max-usd 1.0 --out assets/raw/rigged --name <이름>
$GF blender info assets/raw/rigged/<걷기 GLB>          # 뼈대와 애니메이션이 들어 있는지
$GF blender turntable assets/raw/rigged/<걷기 GLB> --out captures/turntable --name <이름>-rigged --count 4
```

- 결과에 뼈대가 든 GLB/FBX 와 기본 걷기·달리기 애니메이션 GLB 가 나온다(실측 파일 이름: `<이름>_basic_animations-walking_glb.glb`). 걷기 GLB 를 `assets/game/models/player.glb` 로 두면 두 3D 템플릿이 걷는 동안 그 애니메이션을 반복 재생한다. 리깅 뒤에도 정면 +Z 와 키가 유지됐다(실측). 다른 프리셋은 `--animate --animation-id <ID>`(ID 는 `$GF fal schema fal-ai/meshy/rigging` 과 모델 문서에서 확인한다. 추측하지 않는다).
- 두 팔 두 다리 인물형에만 맞는다. A-포즈가 아니거나 망토·꼬리처럼 몸에 붙은 큰 부분이 있으면 뼈대가 엉뚱하게 붙는다.
- 턴테이블은 정지 자세만 보여 준다. 움직임은 게임 안에서 연속 스크린샷(`engine capture --at 0.5,0.65,0.8,0.95`)으로 다리 위치가 바뀌는지 보고, 최종 판정은 사람이 한다. 두 번 해도 어색하면 리깅을 버리고 코드 애니메이션(상하 흔들림, 기울임, 부품 회전)으로 간다.

## 게임에 넣고 확인한다

GLB 는 `assets/game/models/` 에 둔다. 등록은 게임 폴더의 `AGENTS.md` "에셋" 절(web: `src/models.js` 의 `MODELS`, Godot: `scripts/player.gd` 의 `MODEL` 등). 하나 넣을 때마다:

```sh
$GF check assets
$GF engine test
$GF engine capture --out captures/assets-<이름> --script bot/<앞으로 걷는 입력>.json --at 1,2,3
$GF engine perf --seconds 5 --out captures/perf/<이름>.json
```

스크린샷을 Read 로 본다: 크기가 그레이박스 캡슐과 맞는가, 발이 바닥에 닿는가, 진행 방향을 보는가, 조명·색이 기준 화면과 맞는가. `perf` 의 프레임 시간·드로우 콜·메모리가 넣기 전보다 크게 나빠졌으면 삼각형·텍스처 크기를 줄인다. 채택한 컨셉 프롬프트는 다음 생성부터 `--keep` 으로 남긴다.

화면 품질은 `gf-verify` 의 블라인드 심사로 판정한다. 에셋·UI(`gf-ui`)·오디오(`gf-audio`)가 모두 들어가고 사용자가 화면을 승인하면 `gf-verify` 의 승인 절차로 단계를 넘긴다.
