# 웹 2D 게임 (캔버스, 픽셀 아트 / 고해상도 2D)

gameforge 하네스가 만든 게임 프로젝트다. 이 파일은 이 프로젝트에서 일하는 코딩 에이전트를 위한 규칙이다.

## 가장 중요한 규칙: 고친 뒤에는 직접 실행해서 화면을 본다

테스트가 통과해도 화면이 틀릴 수 있다. "고쳤다"고 말하기 전에 아래를 돌리고, 나온 PNG 를 직접 열어 본다.

```sh
GF="uv run -q --project <harness>/tools gf --project ."
$GF engine test                                  # 부팅, 첫 화면, 콘솔 오류, 입력 생존. 변경마다 돌린다
$GF engine capture --out captures/<이름> --at 1,3 [--script <액션.json>]   # 실제 렌더링 스크린샷 + 상태
$GF engine bot --policy goal --seconds 30        # 봇이 실제 입력으로 플레이: 목표 도달, 시간, 사망 수
$GF engine bot --policy bot/clear.json --require-goal   # 레벨을 깨는 고정 입력. 레벨을 바꾸면 같이 고친다
$GF engine perf --seconds 5                      # FPS, 드로우 콜, 메모리
$GF engine run --record                          # 사람이 플레이하며 입력 기록 → captures/sessions/<id>.jsonl
$GF engine replay <id>                           # 기록 재생. "반응 없는 입력" 후보는 버그로 다룬다
```

- 한 번에 한 가지만 바꾸고, 바꿀 때마다 `engine test` 와 스크린샷으로 확인한다.
- 사람이 "느낌이 이상하다"고 하면 추측으로 고치지 말고 `engine run --record` 로 받은 기록을 `engine replay` 로 재현한 뒤 고친다.
- 엔진/콘솔 오류와 경고는 결과 JSON 의 `logs` 에 있다. 오류 0건을 유지한다.

## 브리지를 깨지 않는다

`gf/bridge.js` 는 고치지 않는다. 게임 루프는 브리지가 소유한다: `src/main.js` 가 `installBridge({info, getState, tick, render})` 를 부르고, 게임은 `requestAnimationFrame` 을 직접 돌리지 않는다.

계약 전문은 하네스의 `templates/README.md` 에 있다. 요점:

- 상태 스냅샷의 필수 필드(`level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`)를 유지한다. 게임에 맞게 필드를 더하는 것은 좋다(점수, 체력 등). 매 틱 변하는 타이머는 넣지 않는다.
- 입력은 액션 이름으로만 읽는다. 액션을 추가하면 `info.actions` 에도 넣는다.
- 게임 규칙은 고정 틱에서만 진행하고, 벽시계를 읽지 않고, 난수는 시드를 따른다. 그래야 재생이 원본과 일치한다.
- 플레이어·목표의 의미가 바뀌는 게임(목표가 여럿, 플레이어가 없음)이면 가장 가까운 것으로 채운다: `goal.reached` = 현재 레벨의 승리 조건, `deaths` = 실패 횟수.

## 구조

```
index.html       캔버스, HUD 글자(DOM), 모듈 진입점. 빌드 단계가 없다(ES 모듈 그대로)
src/view.js      화면 설정 VIEW (기준 해상도, 단위당 픽셀, 부드럽게 그릴지). gf init 이 스타일에 맞춰 쓴다
src/level.js     레벨 데이터. 그레이박스 단계에서는 여기만 고친다
src/core.js      게임 규칙. DOM 을 모르는 순수 로직: step(game, input, dt) → 이번 틱의 사건 이름들, snapshot(game)
src/input.js     KEYMAP(액션 → 키)과 키보드 상태
src/render.js    그리기. 상태를 읽기만 한다
src/sprites.js   그림 등록(SHEETS, IMAGES)과 그리기 도우미(drawFrame, drawStanding, drawTiled)
src/audio.js     소리 등록(SOUNDS)과 재생. 첫 입력 뒤에 소리가 풀린다
src/main.js      조립과 브리지 등록, 캔버스 크기, HUD
bot/clear.json   레벨을 깨는 액션 스크립트
```

- 규칙(core)과 그리기(render)를 섞지 않는다. core 는 `Math.random`, `Date.now`, `performance.now` 를 쓰지 않는다. 난수는 `gf/bridge.js` 의 `random()`.
- 좌표·크기·속도는 스타일과 상관없이 **레벨 단위(기준 해상도 320x180)** 다. 화면 설정은 `gf init --style` 이 `src/view.js` 의 `VIEW` 한 줄에 정해 둔다.

  | | 픽셀 아트 (`--style pixel`) | 고해상도 2D (`--style 2d`) |
  |---|---|---|
  | `VIEW.smooth` | `false`: 320x180 캔버스를 정수배로 확대(`image-rendering: pixelated`, 스무딩 끔, 좌표 반올림) | `true`: 캔버스를 창 해상도(× devicePixelRatio)로 만들고 그만큼 확대해 부드럽게 그린다 |
  | `VIEW.ppu` (그림 픽셀 ÷ 레벨 단위) | `1` | `4` (1280x720 창에서 그림이 1:1) |

  스타일을 바꾸려면 이 줄을 고치고 그림을 새 `ppu` 에 맞춰 다시 만든다. 픽셀 설정에 픽셀이 아닌 그림을 넣으면 320x180 으로 뭉개진 뒤 확대되어 지글거린다.
- 그리기 코드는 레벨 단위로만 쓴다. 그림의 크기는 `src/sprites.js` 의 도우미가 `VIEW.ppu` 로 나눠 맞추고, 반올림은 `snap()` 이 스타일에 맞게 한다.
- HUD 글자는 캔버스가 아니라 `#hud`(DOM)에 쓴다. 저해상도 캔버스에 쓴 글자는 확대하면 뭉개진다. 글자 크기는 `main.js` 가 확대 배율에 맞춘다.
- 프레임워크와 번들러를 들이지 않는다. 필요해지면 사용자와 먼저 상의한다.
- 콘솔 오류·경고와 404 는 `engine test` 를 실패시킨다.

## 에셋

- 애니메이션은 `src/sprites.js` 의 `SHEETS` 에 등록한다. `gf post sheet --name player_walk --out assets/game/sprites` 가 만든 매니페스트를 `player: { manifest: "./assets/game/sprites/player_walk.json" }` 로 등록하면 플레이어가 그레이박스 사각형 대신 그것을 쓴다(매니페스트의 애니메이션이 `run`, 첫 프레임이 `idle`. 발이 판정 상자 바닥에 온다. 그림은 오른쪽을 보게 만들고, 왼쪽으로 가면 뒤집힌다). 같은 크기 칸의 격자 시트는 `{ url, cell, fps, animations }` 로 등록한다.
- 정지 그림은 `IMAGES` 에 등록하고 `src/render.js` 에서 `drawStanding(ctx, 그림, 판정 상자)`(아래 가운데를 맞춘다. 늘리지 않는다)나 `drawTiled(ctx, 그림, 영역, 그림의 일부)`(반복해서 깐다)로 그린다. `draw` 는 `art.images.<이름>`, `art.sheets.<이름>` 으로 받는다.
- 소리는 `assets/game/audio/` 에 두고 `src/audio.js` 의 `SOUNDS` 에 등록한다. 이름이 규칙의 사건(`jump`, `death`, `goal`: `core.js` 의 `step` 이 돌려준다)과 같으면 그때 나고, `theme` 은 반복 음악으로 재생된다(`loop: true` 로 등록). 브라우저는 사용자의 첫 입력 전에 소리를 내지 못하므로 `audio.js` 가 첫 키·클릭에서 오디오를 연다. `AudioContext` 를 그보다 먼저 만들지 않는다(콘솔 경고가 나고 `engine test` 가 실패한다). 재생 여부는 콘솔의 `__audio.unlocked()`, `__audio.started` 로 본다.
- 생성 원본은 `assets/raw/`, 후처리가 끝난 게임용 파일만 `assets/game/` 에 둔다. 게임 코드는 `assets/game/` 만 참조한다.
- 특정 기존 게임의 캐릭터·레벨·이름을 재현하지 않는다.
