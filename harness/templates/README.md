# 게임 템플릿과 브리지 계약

`gf init --engine <godot|web> --dim <2d|3d> --style <...>` 이 여기의 `<engine>-<dim>/` 을 게임 디렉터리로 복사한다.
네 템플릿 모두 도형만으로 만든 작은 그레이박스(출발점, 구덩이, 위험물, 목표)이고, 아래 **브리지 계약**을 구현한다.

브리지는 `gf engine ...` 명령이 게임을 실행하고, 실제 입력 경로로 조종하고, 화면과 상태를 읽는 유일한 통로다.
게임 코드를 고칠 때 이 계약이 깨지면 스크린샷·플레이 봇·입력 재생이 전부 멈춘다. `gf engine test` 가 계약을 검사한다.

| 템플릿 | 브리지 파일 | 게임이 등록하는 곳 |
|---|---|---|
| `godot-2d`, `godot-3d` | `gf/gf_bridge.gd` (오토로드 `GfBridge`) | `scripts/main.gd` 의 `_ready` |
| `web-2d`, `web-3d` | `gf/bridge.js` (`window.__gf`) | `src/main.js` 의 `installBridge({...})` |

같은 엔진의 두 템플릿은 브리지 파일이 글자 하나까지 같다(`tools/tests/test_engine_templates.py` 가 확인). 브리지 파일은 게임 쪽에서 고치지 않는다.
브리지에는 버전(`BRIDGE`)이 있고 하네스의 `BRIDGE_VERSION`(`tools/gf/engine/adapter.py`)과 같아야 한다. 옛 템플릿으로 만든 게임은 `gf engine` 이 실패하면서 브리지 파일을 바꿔 넣을 `cp` 명령을 알려 준다.

## 1. 게임이 선언하는 것: info

```json
{
  "dim": "2d",
  "actions": {
    "left":  {"move": [-1, 0], "keys": ["ArrowLeft", "KeyA"]},
    "right": {"move": [1, 0],  "keys": ["ArrowRight", "KeyD"]},
    "jump":  {"keys": ["Space"]}
  },
  "probe": ["right", "left", "jump"]
}
```

- `actions`: 게임이 받는 입력 액션. 이동 액션에는 그 액션이 플레이어를 보내는 방향 `move`(상태의 `pos` 와 같은 좌표계)를 적는다. 내장 봇 정책 `goal` 이 이것으로 방향을 정한다.
- `keys`: web 에서만 필수. `KeyboardEvent.code` 목록이고 첫 번째 키로 입력을 보낸다. Godot 은 입력 맵(project.godot `[input]`)에서 액션의 첫 키를 찾으므로 액션 이름이 입력 맵에 있어야 한다.
- `probe`: 게임 시작 직후 눌렀을 때 반드시 상태가 반응해야 하는 액션. `gf engine test` 가 하나씩 눌러 본다.

## 2. 게임이 내놓는 것: 상태 스냅샷

```json
{
  "tick": 120, "t": 2.0, "fps": 60,
  "level": "graybox-1",
  "player": {"pos": [189.0, 148.9], "vel": [90.0, 0.0], "on_floor": true},
  "goal": {"pos": [606.0, 140.0], "reached": false},
  "deaths": 0
}
```

- `tick`, `t`, `fps` 는 브리지가 붙인다. 나머지는 게임이 준다 (Godot: `GfBridge.state_provider`, web: `getState`).
- 필수: `level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`. 3D 는 `pos`/`vel` 이 `[x, y, z]` 다.
- `player.on_floor` 는 선택이지만, 있으면 `goal` 봇이 죽기 직전 발 디딘 자리를 기억해 다음에 그 앞에서 점프한다.
- 그 밖의 필드(점수, 체력, 열쇠 수, 현재 화면 이름 등)는 자유롭게 더한다. 숫자와 불리언으로 두면 "입력에 반응했는가" 판정에 쓰인다.
  반대로 **입력과 무관하게 매 틱 변하는 값(타이머 등)은 넣지 않는다.** 모든 입력이 반응한 것처럼 보이게 된다.

## 3. 시간과 결정성

- 시간 단위는 물리 틱(기본 초당 60)이다. `t = tick / tick_rate`.
- lockstep 모드에서는 하네스가 `step(n)` 을 부른 만큼만 틱이 진행된다. 벽시계와 무관하므로 같은 시드 + 같은 입력이면 같은 결과가 나와야 한다.
  - Godot: `--fixed-fps` 로 실행하고 브리지가 프레임마다 `_process` 끝에서(물리 틱과 틱 사이) 멈춰 명령을 기다린다. 게임 로직은 `_physics_process` 에 둔다.
    스크린샷은 그 자리에서 지금 상태를 다시 그려(`RenderingServer.force_draw`) 찍는다.
  - web: 브리지가 게임 루프를 소유한다. 게임은 `tick(dt)` 과 `render()` 만 넘기고 `requestAnimationFrame` 을 직접 돌리지 않는다.
    lockstep 에서도 브리지는 화면 프레임마다 `render()` 를 부른다(three 의 그림자 맵처럼 화면 프레임당 한 번만 갱신되는 것이 스크린샷에서 뒤처지지 않게). 그래서 `render()` 는 상태를 바꾸면 안 된다.
- 난수는 시드를 따른다. Godot 은 브리지가 `seed()` 를 부르므로 전역 난수(`randf` 등)를 쓰고 `randomize()` 를 부르지 않는다. web 은 `Math.random` 대신 `gf/bridge.js` 의 `random()` 을 쓴다.
- 게임 로직에서 벽시계(`Time.get_ticks_msec`, `Date.now`, `performance.now`)를 읽지 않는다.

## 4. 입력 주입

봇과 재생은 상태를 직접 바꾸지 않고 사람의 키와 같은 경로로 입력을 넣는다.

- Godot: 입력 맵에서 찾은 `InputEventKey` 를 `Input.parse_input_event` 로 넣는다. `Input.is_action_pressed` 와 `_input`/`_unhandled_input` 이 사람이 눌렀을 때와 똑같이 동작한다.
  넣는 시점은 틱과 틱 사이다. Godot 은 입력이 들어온 다음 물리 틱에 `is_action_just_pressed` 를 참으로 만들기 때문에, 물리 틱 안에서 넣으면 "방금 눌림"만 한 틱 늦는다(실측: 그렇게 넣던 때에는 사람의 키로 기록한 점프가 재생에서 매번 한 틱 늦었다). 첫 틱 전에 보낸 입력만 예외로 한 틱 늦다.
- web: Playwright 가 Chrome 에 키보드·마우스 이벤트를 보낸다(CDP `Input.dispatchKeyEvent`: 브라우저의 입력 처리 경로를 타고 `isTrusted` 가 참이다. 운영체제는 거치지 않는다). `window` 의 `keydown`/`keyup` 처리기가 그대로 받는다.
- 운영체제 쪽에서 들어오는 키로 확인하려면 `gf engine run --record --script <액션.json> --seconds N --os-input` 을 쓴다(macOS, 터미널 앱에 손쉬운 사용 권한 필요). 게임 창을 띄우고 Quartz 키 이벤트를 게임 프로세스에 보낸다(`CGEventPostToPid`). 앱 안에서는 사람이 누른 키와 같은 경로다. 키보드 하드웨어와 "어느 창이 키를 받는가"는 거치지 않으므로 그것까지 보려면 사람이 직접 누른다.

자동 실행 중의 창 포커스 (Godot, `--gf-auto`): Godot 은 앱이 포커스를 잃으면 눌린 키와 액션을 전부 뗀다(넣어 둔 키도 풀린다). 터미널에서 실행한 Godot 은 뜨자마자 스스로 포커스를 한 번 내줬다 되찾고, 그 뒤로도 사용자가 다른 창을 누르면 잃는다. 그래서 브리지는 인사 전에 시작 직후의 포커스 변화가 끝나기를 기다리고, 하네스는 원래 앞에 있던 앱을 다시 활성화해 Godot 을 비활성으로 둔다(사용자의 포커스를 빼앗지 않는다. macOS 만). 브리지는 포커스를 잃을 때마다 Input 이 "포커스 있음"으로 알게 되돌려, 그 뒤의 창 이동·최소화로 키가 풀리지 않게 한다. 그런데도 실행 중에 누가 게임 창을 직접 활성화했다 떠나면 키가 한 번 풀리는데, 브리지가 다시 누르고 오류(`logs`, `errors`)로 남긴다. 그 실행은 다시 돌린다.
web 의 자동 실행(headless)은 포커스를 잃지 않는다. 그래도 `blur` 가 오면 브리지가 콘솔 오류로 남긴다.

그래서 게임은 **입력을 액션 이름으로만** 읽어야 한다 (Godot: 입력 맵 액션, web: `src/input.js` 의 `KEYMAP`). 새 액션을 만들면 입력 맵/KEYMAP 과 `info.actions` 양쪽에 넣는다.

입력이 게임에 닿지 않는데 성공으로 보고하는 일을 막는 장치가 두 겹 있다.
1. 누른 뒤 0.25초 안에 상태(플래그·카운터 또는 속도 변화율)가 달라졌는지 본다.
2. 같은 시드로 입력 없이 한 번 더 돌려, 첫 입력 뒤에 두 실행의 상태가 갈라지는지 본다(반사실 비교). 끝까지 같으면 실패다.

## 5. 기록 형식 (`captures/sessions/<id>.jsonl`)

```json
{"type": "header", "version": 1, "engine": "godot", "tick_rate": 60, "seed": 0, "size": [1280, 720], "info": {}}
{"type": "input", "tick": 12, "t": 0.2, "down": true, "device": "key", "code": "Right", "actions": ["right"]}
{"type": "state", "tick": 18, "t": 0.3, "state": {}}
```

- `gf engine run --record` 중 사람이 누르고 뗀 모든 키·마우스 버튼(Godot 은 게임패드 버튼도)과, 6틱(0.1초)마다의 상태 표본이 남는다.
- 마우스 위치 `pos` 는 창 좌표다(Godot: 창의 물리 픽셀, web: `clientX/Y`). header 의 `size` 는 실제 창 안쪽 크기이고 재생은 그 크기로 띄운다.
- web 은 게임패드를 기록하지 않는다.
- 사람이 키를 누른 채 다른 창으로 가면 엔진은 그 키를 놓지만 뗌 이벤트는 오지 않는다. 브리지가 그 시점에 뗌을 적는다(`"cause": "focus_out"` / `"blur"`). 그래서 게임은 포커스를 잃을 때 키를 놓아야 한다(Godot 은 엔진이 한다. web 템플릿은 `src/input.js` 의 `blur` 처리).
- `code` 는 엔진 고유 표기다 (Godot: 물리 키 이름 `Right`, `Space` / web: `KeyboardEvent.code`). 기록은 같은 엔진에서만 재생한다.
- 마우스 이동과 아날로그 스틱은 기록하지 않는다. 마우스 시점 조작을 넣으면 재생이 원본과 달라진다.
- 봇·재생·캡처가 남기는 `trace.jsonl` 도 같은 형식이다 (표본 간격만 3틱).

## 6. 브리지 명령 (참고)

하네스 → 게임. Godot 은 `-- --gf-port=N` 으로 받은 로컬 TCP 포트에 접속해 JSON 한 줄씩 주고받고, web 은 `window.__gf` 의 메서드다.

| 동작 | Godot (`{"cmd": ...}`) | web (`window.__gf`) |
|---|---|---|
| n 틱 진행 후 상태 | `step` `{n}` | `step(n)` |
| 상태 | `state` | `state()` |
| 액션 누름/뗌 | `action` `{name, down}` | Playwright 키 입력 (`info.actions[name].keys[0]`) |
| 원시 입력 (재생) | `input` `{device, code, down, pos?}` | Playwright 키·마우스 입력 |
| 스크린샷 | `screenshot` `{path}` (뷰포트 텍스처를 창 크기로: 정수배 확대와 검은 띠 포함) | Playwright 페이지 스크린샷 |
| 소리 측정 꺼내기 | `audio` | `audio()` |
| 포커스 내주기 | `yield_focus` `{wait_ms}` | (필요 없다) |
| 프레임 시간 측정 | `perf_start`, `perf_stop` | `perfStart()`, `perfStop()` |
| 기록 꺼내기 | 브리지가 `--gf-record=<파일>` 에 직접 쓴다 | `drain()` |
| 종료 | `quit` | 브라우저를 닫는다 |

Godot 실행 인자: `--gf-port=N`, `--gf-lockstep`, `--gf-seed=N`, `--gf-record=<파일>`, `--gf-auto`(사람 대신 하네스가 입력한다), `--gf-audio`(소리 측정). 인자가 없으면 브리지는 아무 일도 하지 않는다.
web 쿼리: `gf_manual=1`, `gf_seed=N`, `gf_record=1`, `gf_audio=1`.

소리 측정(`gf engine audio`)은 게임 코드를 고치지 않고 잰다. Godot 은 마스터 버스에 `AudioEffectCapture` 를 달아 0.1초마다 피크·RMS 를 내고, 씬 트리의 `AudioStreamPlayer`(2D/3D 포함)를 틱마다 훑어 재생이 시작됐거나 반복 지점을 넘은 소리를 적는다. web 은 Web Audio 를 가로채 `destination` 으로 가는 연결을 분석기에 거치게 하고, `AudioBufferSourceNode.start` 와 `<audio>.play` 를 적는다(`<audio>` 요소의 신호 크기는 재지 못한다). 잰 것은 엔진 안의 최종 신호이지 스피커 소리가 아니다.

## 7. 3D 방향 규약 (한 곳에만 적는다)

생성 모델 → `gf blender rescale` → GLB → 두 3D 템플릿이 모두 같은 규약을 쓴다.

| 대상 | 규약 |
|---|---|
| GLB 파일 | y 가 위, 원점은 발밑 중심, **모델의 정면은 +Z** (glTF 표준), 1 단위 = 1 m |
| `gf blender rescale --turn <도>` | 위쪽 축 둘레로 돌려 정면을 +Z 에 맞춘다. 생성 모델(tripo)은 정면이 +X 로 나오므로 `--turn -90` |
| `gf blender turntable` | 0번 그림이 +Z 쪽에서 본 모습이다. **0번에 얼굴이 보이면 맞다** |
| 월드 | y 가 위. `forward` 입력은 -z(카메라에서 멀어지는 쪽), `right` 는 +x |
| 템플릿의 플레이어 | 모델의 정면(+Z)이 이동 방향 `(x, z)` 을 보도록 `rotation.y = atan2(x, z)` 로 돌린다 (Godot: `scripts/player.gd` 의 `_yaw`, web: `src/core.js` 의 `yaw`). 시작할 때는 -z(화면 안쪽)를 본다 |

그래서 `forward` 로 걸을 때는 카메라에 **등**이 보이고, `back` 으로 걸을 때 얼굴이 보인다. 반대로 보이면 GLB 의 정면이 +Z 가 아닌 것이므로
게임 코드에서 돌리지 말고 `rescale --turn` 을 고쳐 다시 내보낸다.

## 8. 2D 화면 설정 (스타일별)

두 2D 템플릿의 레벨 좌표·속도는 스타일과 상관없이 기준 해상도 320x180 단위다. 템플릿에는 픽셀 아트용 설정이 들어 있고,
`gf init --style 2d` 가 복사한 뒤 고해상도 2D 용으로 고친다(`tools/gf/core/render_profile.py`. 고칠 줄을 템플릿에서 못 찾으면 실패한다).

| | `--style pixel` | `--style 2d` |
|---|---|---|
| 그리는 해상도 | 320x180 → 정수배 확대, nearest | 창 해상도(1280x720 이면 4배), linear |
| 그림 픽셀 ÷ 레벨 단위 | 1 | 4 |
| Godot (`project.godot`) | 스트레치 `viewport` + `integer`, 필터 0, 픽셀 스냅 켬, `gameforge/art/pixels_per_unit=1` | `canvas_items` + `fractional`, 필터 1, 스냅 끔, `pixels_per_unit=4` |
| web (`src/view.js`) | `ppu: 1, smooth: false` | `ppu: 4, smooth: true` |

그림을 놓는 도우미(Godot `SpriteSheet`, web `src/sprites.js`)가 단위당 픽셀로 나눠 크기를 맞추므로 게임 코드는 레벨 단위만 쓴다.

창 크기와 배율에 따른 동작 (2026-11-22 에 이 맥에서 스크린샷으로 확인한 범위):

| | `--style pixel` | `--style 2d` | 3D |
|---|---|---|---|
| 16:9 가 아닌 창 | 물리 픽셀 기준 정수배로만 키우고 가운데에 둔다. 남는 자리는 띠 (Godot 검정, web 페이지 배경색) | 16:9 를 유지한 채 창에 맞추고 남는 쪽에 띠 | 띠 없이 창을 채운다. 세로 시야각을 유지해 넓은 창은 좌우가 더 보인다 |
| 레티나(배율 2) | 게임 픽셀 하나가 물리 픽셀 정수 개 (web 은 1.25·1.5 배율도) | 물리 해상도로 그린다 | 물리 해상도로 그린다 |
| HUD | Godot: 기준 해상도에 안티에일리어싱 없는 글자. web: DOM 글자가 배율만큼 커진다 | 창 해상도의 글자 | Godot: 창에 비례. web: 고정 24px |

`gf engine capture --size WxH` 의 PNG 는 Godot 에서 정확히 WxH(물리 픽셀. 띠 포함), web 에서 WxH × `--scale` 이다. Godot 창이 화면보다 커서 줄어들면 실패하고 `--screen N` 을 쓰라고 말한다.
배율이 섞인 모니터 구성(레티나 + 일반 모니터)에서 Godot 은 모든 화면을 최대 배율로 그리고 일반 모니터에는 macOS 가 줄여서 보여 준다. 그 모니터에서는 홀수 배율의 픽셀 아트가 고르지 않게 보일 수 있다(스크린샷에는 드러나지 않는다).

## 9. 명령 요약

```sh
gf() { uv run -q --project <harness>/tools gf --project <game> "$@"; }
gf engine test                                   # 부팅, 첫 화면, 콘솔 오류, 입력 생존
gf engine capture --out captures/now --at 1,3    # 스크린샷 + capture.json
gf engine capture --out captures/jump --script bot/clear.json --at 2.2
gf engine bot --policy goal --seconds 30         # 내장 정책: goal, random, idle
gf engine bot --policy bot/clear.json --require-goal
gf engine run --record                           # 사람이 플레이, 입력 기록
gf engine replay <id>                            # 기록 재생 + 반응 없는 입력 후보
gf engine perf --seconds 5                       # FPS, 드로우 콜, 메모리, 로딩 시간
gf engine audio --expect jump=jump               # 실시간으로 돌리며 소리가 나는지 잰다 → captures/audio/result.json
gf engine capture --out captures/wide --size 2560x1080 [--scale 2] [--screen 1]   # 다른 창 크기, 레티나(web), 화면 선택(Godot)
gf engine run --record --script bot/clear.json --seconds 8 --os-input   # 운영체제 키 이벤트로 기록 경로 점검
```

액션 스크립트(JSON): `{"seed": 0, "actions": [{"t": 0.2, "press": "right"}, {"t": 2.0, "tap": "jump", "hold": 0.1}, {"t": 3.0, "release": "right"}]}`.
봇 정책 파일(.py): `decide(state: dict, info: dict) -> list[str]` 이 지금 누르고 있을 액션 이름들을 돌려준다.
