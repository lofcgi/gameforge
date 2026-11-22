# 브리지 계약 요점

전문은 하네스의 `templates/README.md`. 브리지는 `gf engine ...` 이 게임을 실행하고, 실제 입력 경로로 조종하고, 화면과 상태를 읽는 유일한 통로다. 깨지면 스크린샷·봇·재생이 전부 멈춘다.

| 템플릿 | 브리지 파일 (고치지 않는다) | 게임이 등록하는 곳 |
|---|---|---|
| `godot-2d`, `godot-3d` | `gf/gf_bridge.gd` (오토로드 `GfBridge`) | `scripts/main.gd` 의 `_ready` 에서 `GfBridge.info`, `GfBridge.state_provider` |
| `web-2d`, `web-3d` | `gf/bridge.js` (`window.__gf`) | `src/main.js` 의 `installBridge({info, getState, tick, render, ...})` |

## info (게임이 선언)

```json
{"dim": "2d",
 "actions": {"left": {"move": [-1, 0], "keys": ["ArrowLeft", "KeyA"]}, "jump": {"keys": ["Space"]}},
 "probe": ["right", "left", "jump"]}
```

- `move`: 그 액션이 플레이어를 보내는 방향. 내장 봇 `goal` 이 이것으로 방향을 정한다.
- `keys`: web 에서만 필수(`KeyboardEvent.code`). Godot 은 입력 맵에서 찾는다.
- `probe`: 시작 직후 눌렀을 때 반드시 상태가 반응해야 하는 액션. `engine test` 가 하나씩 눌러 본다.

## 상태 스냅샷 (게임이 제공)

필수: `level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`. 3D 는 `pos`/`vel` 이 `[x, y, z]`.

- `player.on_floor` 가 있으면 `goal` 봇이 죽기 직전 발 디딘 자리를 기억해 그 앞에서 점프한다.
- 점수·체력·열쇠 수 같은 필드를 숫자·불리언으로 더하면 "입력에 반응했는가" 판정에 쓰인다.
- **입력과 무관하게 매 틱 변하는 값(타이머)은 넣지 않는다.** 모든 입력이 반응한 것처럼 보이게 된다.
- 플레이어·목표의 의미가 다른 게임이면 가장 가까운 것으로 채운다: `goal.reached` = 현재 레벨의 승리 조건, `deaths` = 실패 횟수.

## 결정성

- 게임 규칙은 고정 틱에서만 진행한다 (Godot `_physics_process`, web `tick(dt)`). web 은 `requestAnimationFrame` 을 직접 돌리지 않는다.
- 벽시계(`Time.get_ticks_msec`, `Date.now`, `performance.now`)를 읽지 않는다.
- 난수는 시드를 따른다. Godot: 전역 난수를 쓰고 `randomize()` 를 부르지 않는다. web: `Math.random` 대신 `gf/bridge.js` 의 `random()`.
- 마우스 이동과 아날로그 스틱은 기록되지 않는다. 마우스 시점 조작을 넣으면 재생이 원본과 달라진다고 사용자에게 알린다.

## 입력

봇과 재생은 상태를 직접 바꾸지 않고 사람의 키와 같은 경로로 입력을 넣는다. 게임은 입력을 **액션 이름으로만** 읽는다 (Godot 입력 맵, web `src/input.js` 의 `KEYMAP`).

입력이 닿지 않는데 성공으로 보고하는 일을 막는 장치가 두 겹 있다: ① 누른 뒤 0.25초 안에 상태가 달라졌는가 ② 같은 시드로 입력 없이 한 번 더 돌린 실행과 상태가 갈라지는가(`liveness`).

## 엔진별 메모

- Godot 은 스크립트 오류가 나도 종료 코드 0 을 낸다. `engine test` 가 출력의 `SCRIPT ERROR` 를 잡는다.
- web-3d 의 렌더러는 `three/webgpu`. 셰이더는 TSL(`three/tsl`)로 쓴다. GLSL `ShaderMaterial` 은 동작하지 않는다. 콘솔 오류·경고와 404 는 `engine test` 를 실패시킨다.
- web 은 규칙(`src/core.js`)과 그리기(`src/render.js`)를 섞지 않는다.
