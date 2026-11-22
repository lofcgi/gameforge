# 웹 3D 게임 (three.js)

gameforge 하네스가 만든 게임 프로젝트다. 이 파일은 이 프로젝트에서 일하는 코딩 에이전트를 위한 규칙이다.

## 가장 중요한 규칙: 고친 뒤에는 직접 실행해서 화면을 본다

테스트가 통과해도 화면이 틀릴 수 있다. "고쳤다"고 말하기 전에 아래를 돌리고, 나온 PNG 를 직접 열어 본다.

```sh
gf() { uv run -q --project <harness>/tools gf --project . "$@"; }
gf engine test                                  # 부팅, 첫 화면, 콘솔 오류, 입력 생존. 변경마다 돌린다
gf engine capture --out captures/<이름> --at 1,3 [--script <액션.json>]   # 실제 렌더링 스크린샷 + 상태
gf engine bot --policy goal --seconds 30        # 봇이 실제 입력으로 플레이: 목표 도달, 시간, 사망 수
gf engine bot --policy bot/clear.json --require-goal   # 레벨을 깨는 고정 입력. 레벨을 바꾸면 같이 고친다
gf engine perf --seconds 5                      # FPS, 드로우 콜, 메모리
gf engine audio --expect jump=jump              # 실시간으로 돌리며 소리가 실제로 나는지 잰다 (스피커가 아니라 엔진 안의 신호)
gf engine run --record                          # 사람이 플레이하며 입력 기록 → captures/sessions/<id>.jsonl
gf engine replay <id>                           # 기록 재생. "반응 없는 입력" 후보는 버그로 다룬다
```

- 한 번에 한 가지만 바꾸고, 바꿀 때마다 `engine test` 와 스크린샷으로 확인한다.
- 사람이 "느낌이 이상하다"고 하면 추측으로 고치지 말고 `engine run --record` 로 받은 기록을 `engine replay` 로 재현한 뒤 고친다.
- 엔진/콘솔 오류와 경고는 결과 JSON 의 `logs` 에 있다. 오류 0건을 유지한다.

## 브리지를 깨지 않는다

`gf/bridge.js` 는 고치지 않는다. 게임 루프는 브리지가 소유한다: `src/main.js` 가 `installBridge({info, getState, tick, render, perfCounters})` 를 부르고, 게임은 `requestAnimationFrame` 이나 `renderer.setAnimationLoop` 을 직접 돌리지 않는다.

계약 전문은 하네스의 `templates/README.md` 에 있다. 요점:

- 상태 스냅샷의 필수 필드(`level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`)를 유지한다. 게임에 맞게 필드를 더하는 것은 좋다(점수, 체력 등). 매 틱 변하는 타이머는 넣지 않는다.
- 입력은 액션 이름으로만 읽는다. 액션을 추가하면 `info.actions` 에도 넣는다.
- 게임 규칙은 고정 틱에서만 진행하고, 벽시계를 읽지 않고, 난수는 시드를 따른다. 그래야 재생이 원본과 일치한다.
- 플레이어·목표의 의미가 바뀌는 게임(목표가 여럿, 플레이어가 없음)이면 가장 가까운 것으로 채운다: `goal.reached` = 현재 레벨의 승리 조건, `deaths` = 실패 횟수.

## 구조

```
index.html       캔버스, HUD, import map (node_modules 의 three 를 빌드 없이 읽는다)
package.json     three 의존성. bun.lock 과 함께 커밋하고 node_modules 는 커밋하지 않는다
src/level.js     레벨 데이터. 그레이박스 단계에서는 여기만 고친다
src/core.js      게임 규칙. three.js 를 모르는 순수 로직(AABB 충돌): step(game, input, dt), snapshot(game)
src/input.js     KEYMAP(액션 → 키)과 키보드 상태
src/render.js    three.js 장면·조명·카메라. 상태를 읽기만 한다
src/models.js    GLB 로더(GLTFLoader)와 모델 등록
src/main.js      조립과 브리지 등록
bot/clear.json   레벨을 깨는 액션 스크립트
```

- 렌더러는 `three/webgpu` 의 `WebGPURenderer` 다. WebGPU 가 없으면 three 가 WebGL2 로 내려가며, 실제로 쓰인 쪽이 `info.renderer`(`webgpu`|`webgl2`)로 보고된다. 셰이더를 직접 쓸 때는 TSL(`three/tsl`)로 쓴다. GLSL `ShaderMaterial` 은 이 렌더러에서 동작하지 않는다.
- `import "three"` 는 import map 이 `three.webgpu.js` 로 보낸다. 애드온은 `three/addons/...` 로 가져온다. 패키지는 `bun add <이름>` 으로 넣고 import map 에 경로를 더한다.
- 단위는 미터, y 가 위, `forward` 입력은 월드 -z 로 간다(카메라에서 멀어지는 쪽). 이동은 월드 축 기준이고 `info.actions` 의 `move` 벡터가 그것을 봇에게 알려 준다.
- 규칙(core)과 그리기(render)를 섞지 않는다. core 는 `Math.random`, `Date.now`, `performance.now` 를 쓰지 않는다. 난수는 `gf/bridge.js` 의 `random()`.
- 마우스 이동은 기록·재생되지 않는다. 마우스 시점 조작을 넣게 되면 사용자에게 재생이 어긋날 수 있음을 알린다.
- 창의 비율이 달라져도 화면은 늘어나지 않는다(`src/render.js` 의 `resize` 가 카메라 비율을 창에 맞춘다). 세로 시야각을 유지하므로 넓은 창(21:9)은 좌우가 더 보이고, 띠는 없다. HUD 는 왼쪽 위에 고정 크기(24px)로 붙어 있다. 레티나에서는 물리 해상도로 그린다(`setPixelRatio`, 배율 2 까지). 확인: `$GF engine capture --out captures/<이름> --size 1024x768`, 레티나는 `--scale 2`.
- 소리를 넣으면 `$GF engine audio` 로 실행 중에 소리가 나는지 잰다. 브라우저는 사용자의 첫 입력 전에 소리를 내지 못한다(web-2d 템플릿의 `src/audio.js` 방식을 따른다).
- 콘솔 오류·경고와 404 는 `engine test` 를 실패시킨다.

## 에셋

- 3D 모델은 GLB 로 `assets/game/models/` 에 두고 `src/models.js` 의 `MODELS` 에 등록한다. 규약: 원점은 발밑, **모델의 정면은 +Z**(glTF 표준), 1 단위 = 1 m. `gf blender rescale` 이 이 규약으로 내보낸다. `player` 를 등록하면 플레이어가 캡슐 대신 그것을 쓰고, 정면(+Z)이 이동 방향을 보도록 돌린다(`src/core.js` 의 `yaw`). 다른 모델을 놓을 때도 정면이 +Z 라고 보고 `rotation.y` 를 정한다.
- 플레이어 GLB 에 뼈대와 애니메이션이 들어 있으면(`gf gen rig` 의 걷기 GLB) 첫 애니메이션을 걷는 동안 반복 재생한다(`src/render.js`). 애니메이션은 고정 틱으로 진행해 캡처가 재현된다.
- 생성 원본은 `assets/raw/`, 후처리가 끝난 게임용 파일만 `assets/game/` 에 둔다. 게임 코드는 `assets/game/` 만 참조한다.
- 특정 기존 게임의 캐릭터·레벨·이름을 재현하지 않는다.
