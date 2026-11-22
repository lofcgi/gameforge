# Godot 2D 게임 (픽셀 아트 / 고해상도 2D)

gameforge 하네스가 만든 게임 프로젝트다. 이 파일은 이 프로젝트에서 일하는 코딩 에이전트를 위한 규칙이다.

## 가장 중요한 규칙: 고친 뒤에는 직접 실행해서 화면을 본다

테스트가 통과해도 화면이 틀릴 수 있다. "고쳤다"고 말하기 전에 아래를 돌리고, 나온 PNG 를 직접 열어 본다.

```sh
gf() { uv run -q --project <harness>/tools gf --project . "$@"; }
gf engine test                                  # 부팅, 첫 화면, 콘솔 오류, 입력 생존. 변경마다 돌린다
gf engine capture --out captures/<이름> --at 1,3 [--script <액션.json>]   # 실제 렌더링 스크린샷 + 상태
gf engine bot --policy bot/smoke.json --seconds 60      # 고정 입력: 출항 → 닻 → 멸치 한 마리 → 귀항 → 팔기. 균형을 바꾸면 같이 고친다
gf engine bot --policy bot/full_run.py --seconds 5400 --shot-every 60 --require-goal   # 정책 봇이 처음부터 닫는 장면까지 깬다 (실제 시간 20분쯤)
CA_START="boat=3,rod=3,baits=8,legendbait=1,x=2200" gf engine bot --policy bot/full_run.py --seconds 300 --require-goal   # 중간부터 (design/graybox-play.md 의 디버그 시작)
gf engine perf --seconds 5                      # FPS, 드로우 콜, 메모리
gf engine audio --script bot/smoke.json         # 실시간으로 돌리며 소리가 실제로 나는지 잰다 (아직 소리가 없다)
gf engine run --record                          # 사람이 플레이하며 입력 기록 → captures/sessions/<id>.jsonl
gf engine replay <id>                           # 기록 재생. "반응 없는 입력" 후보는 버그로 다룬다
```

- 한 번에 한 가지만 바꾸고, 바꿀 때마다 `engine test` 와 스크린샷으로 확인한다.
- 사람이 "느낌이 이상하다"고 하면 추측으로 고치지 말고 `engine run --record` 로 받은 기록을 `engine replay` 로 재현한 뒤 고친다.
- 엔진/콘솔 오류와 경고는 결과 JSON 의 `logs` 에 있다. 오류 0건을 유지한다.

## 브리지를 깨지 않는다

`gf/gf_bridge.gd`(오토로드 `GfBridge`)는 고치지 않는다. 게임은 `scripts/main.gd` 의 `_ready` 에서 `GfBridge.info` 와 `GfBridge.state_provider` 를 채운다. 메인 씬을 바꿔도 이 등록은 유지한다.

계약 전문은 하네스의 `templates/README.md` 에 있다. 요점:

- 상태 스냅샷의 필수 필드(`level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`)를 유지한다. 게임에 맞게 필드를 더하는 것은 좋다(점수, 체력 등). 매 틱 변하는 타이머는 넣지 않는다.
- 입력은 액션 이름으로만 읽는다. 액션을 추가하면 `info.actions` 에도 넣는다.
- 게임 규칙은 고정 틱에서만 진행하고, 벽시계를 읽지 않고, 난수는 시드를 따른다. 그래야 재생이 원본과 일치한다.
- 플레이어·목표의 의미가 바뀌는 게임(목표가 여럿, 플레이어가 없음)이면 가장 가까운 것으로 채운다: `goal.reached` = 현재 레벨의 승리 조건, `deaths` = 실패 횟수.

## 구조

옆에서 본 낚시 게임의 그레이박스다. 그림과 소리는 아직 없고 모든 것을 도형으로 그린다. 설계는 `design/brief.md`, 플레이 안내는 `design/graybox-play.md`.

```
project.godot              입력 맵(left/right/up/down/action/cancel/bait/hold/codex), 화면 설정, 오토로드
scenes/main.tscn           루트 씬: Main → World(세계 그리기), Hud/Draw(화면 위 정보)
scripts/main.gd            입력을 읽어 코어를 틱마다 한 번 진행, 브리지 등록, 디버그 시작(CA_START / --start=)
scripts/data.gd            균형 데이터 전부 (아래 표). 균형은 여기만 고친다
scripts/core/              결정적 코어. 노드가 아니고 그리지 않는다. 고정 틱에서만 진행하고 전역 난수(브리지 시드)를 쓴다
  game.gd                  Game: 모드(land/sail/fish) 전환, 히트스톱, 사건 목록(events), 난파, 귀항, 브리지 상태 snapshot()
  sea.gd                   Sea: 구간·바닥 깊이·잔물결 (x 와 틱의 순수 함수, 표로 미리 계산)
  sailing.gd               Sailing: 배 운항, 큰 파도와 내구도, 어군 표시, 떠다니는 물건, "칸마다 볼거리 하나" 규칙
  shoal.gd                 Shoal: 배 주변 물고기의 생성과 헤엄
  fishing.gd               Fishing: 깊이 조준, 접근·입질, 줄다리기
  land.gd                  Land: 항구와 섬 걷기, 채집, 가게 열기, 배 타기
  menu.gd                  Menu: 패널(작업대·어시장·조선소·낚시 가게·어창·도감)과 이야기 카드
  inventory.gd             Inventory: 돈, 재료, 미끼, 어창, 장비 단계, 도감
scripts/view/              그리기. 코어를 읽기만 한다. 그림이 생기면 여기를 바꾼다
  world_view.gd            WorldView: 카메라, 물·수면·바닥, 그리는 순서
  actors.gd                Actors: 배와 고양이, 물고기, 어군 표시, 떠다니는 물건
  scenery.gd               Scenery: 먼 배경, 항구, 섬, 암초·난파선·소용돌이, 바닥 장식
  static_layer.gd          StaticLayer: 한 번 그려 두고 위치만 옮기는 겹(먼 배경, 항구, 섬). 성능 때문에 둔다
  fx.gd                    Fx: 입자, 화면 흔들림, 떠오르는 글자, 알림, 깜박임 (코어의 events 를 받아 만든다)
  hud.gd, panels.gd        상태 줄, 조작 안내, 깊이 눈금, 장력 게이지 / 패널과 카드
scripts/graybox.gd, sprite_sheet.gd, sound.gd   템플릿의 도우미. 에셋 단계에서 쓴다 (지금은 안 쓴다)
bot/smoke.json             고정 입력 스모크
bot/full_run.py            끝까지 깨는 정책 봇. 균형 표를 브리지 info["data"] 에서 읽는다
```

`scripts/data.gd` 의 표 (거리·깊이는 m, 화면 좌표는 가로 `X_PX`=2, 세로 `Y_PX`=4 를 곱한다):

| 표 | 내용 |
|---|---|
| `ZONES` | 구간: 범위, 바닥 깊이, 잔물결 높이(amp), 큰 파도 높이(crest), 필요한 배 등급(grade), 하늘·물·바닥 색 |
| `FISH` | 어종 13: 구간, 장소, 깊이 범위, 어창 칸, 값, 미끼, 힘, 속도, 헤엄 방식, 마릿수, 옆으로 달아나는지, 모양·색 |
| `RODS`, `BOATS` | 낚싯대 3단계(닿는 깊이, 힘, 감는 속도, 값), 배 3단계(파도 등급, 내구도, 속도, 가속, 어창, 값) |
| `BAITS`, `MATS` | 미끼 4종의 재료, 재료 4종. `GATHER_YIELD` 는 채집 한 번의 양 |
| `PLACES` | 암초·작은 섬·난파선·소용돌이 자리의 위치와 너비 |
| `TUG` | 줄다리기 상수: 장력 목표값, 예고 시간, 느슨함 한계, 풀려 나가는 속도 |
| `STATIONS`, `ISLAND_STATIONS` | 항구와 섬의 배치와 가게 주인 대사 |
| `NOTES`, `INTRO`, `ENDING`, `WRECKED` | 병 속 쪽지와 이야기 카드 글 |

규칙:

- 코어(`scripts/core/`)는 화면을 모른다. 화면에 알릴 일은 `g.emit(종류, 데이터)` 로 `events` 에 넣고 `Fx.consume` 이 연출로 바꾼다. 새 연출은 여기에 더한다.
- 입력은 `main.gd` 가 액션 이름으로 읽어 `Game.step(held, pressed)` 에 넘긴다. 코어 안에서는 `g.held()`, `g.pressed()` 만 쓴다. 액션을 더하면 `project.godot`, `main.gd` 의 `ACTIONS` 에 넣는다(`info.actions` 는 거기서 만든다).
- 모든 입력은 누른 틱에 상태(카운터나 값)와 화면이 바뀌어야 한다. 아무 일도 없는 경우에도 반응을 준다(닻을 내린 채 좌우 → 안내 깜박임, 빈 땅에서 Space → 폴짝).
- 브리지 상태(`Game.snapshot`)에는 입력과 무관하게 매 틱 변하는 값(물고기 위치, 파도)을 넣지 않는다. 줄다리기 중의 `tension`·`stamina` 만 예외다(도구가 싸움을 보려면 필요하다).
- 연출(Fx)도 물리 틱에서 진행하고 따로 가진 난수기를 쓴다. 코어의 난수 순서를 건드리지 않기 위해서다.
- 매 틱 다시 그리는 그리기 명령 수가 성능을 정한다. 넓은 면(물, 바닥)은 다각형 하나로, 작은 것은 사각형으로, 안 바뀌는 것은 `StaticLayer` 로 그린다. 다각형은 꼭짓점이 뒤집히면 삼각분할 오류가 나므로(콘솔 오류로 잡힌다) 높이를 미리 눌러 둔다. 고친 뒤 `gf engine perf` 의 p95 를 본다.

- 좌표·크기·속도는 스타일과 상관없이 **레벨 단위(기준 해상도 320x180)** 다. 화면 설정은 `gf init --style` 이 `project.godot` 에 정해 둔다. 지금 어느 쪽인지는 `window/stretch/mode` 로 안다.

  | | 픽셀 아트 (`--style pixel`) | 고해상도 2D (`--style 2d`) |
  |---|---|---|
  | `window/stretch/mode`, `scale_mode` | `viewport`, `integer` (320x180 으로 그린 뒤 정수배 확대) | `canvas_items`, `fractional` (창 해상도로 직접 그린다) |
  | `textures/canvas_textures/default_texture_filter` | `0` (nearest) | `1` (linear) |
  | `2d/snap/snap_2d_transforms_to_pixel`, `..._vertices_to_pixel` | `true` | `false` |
  | `gameforge/art/pixels_per_unit` (그림 픽셀 ÷ 레벨 단위) | `1` | `4` (1280x720 창에서 그림이 1:1) |

  스타일을 바꾸려면 이 여섯 줄을 표의 값으로 고치고 그림을 새 단위당 픽셀에 맞춰 다시 만든다. 픽셀 설정에 픽셀이 아닌 그림을 넣으면 320x180 으로 뭉개진 뒤 확대되어 지글거린다.
- 그림의 크기는 `SpriteSheet` 도우미가 단위당 픽셀로 나눠 맞춘다. 고해상도 2D 에서 24 단위 높이로 보일 캐릭터는 96px 높이로 만든다. 노드에 직접 텍스처를 넣을 때는 `scale = Vector2.ONE / SpriteSheet.pixels_per_unit()` 을 준다.
- 창 크기가 달라져도 화면은 16:9 다. 픽셀 아트는 정수배로만 커지고(1366x768 → 4배 1280x720, 1000x700 → 3배 960x540) 가운데에 놓이며 남는 자리는 검은 띠다. 고해상도 2D 는 16:9 를 유지한 채 창에 맞게 커지고 남는 쪽(4:3 은 위아래, 21:9 는 좌우)이 검은 띠다. HUD 는 게임 화면 안에 있어 띠에 가리지 않는다. 전체 화면도 같다. 확인: `$GF engine capture --out captures/<이름> --size 2560x1080 [--screen N]` (크기는 물리 픽셀. 창이 화면보다 크면 실패하므로 큰 화면 번호를 준다).
- 픽셀 아트 설정에서는 글자의 안티에일리어싱을 끈다(`gui/theme/default_font_antialiasing=0`). 8px 글자를 부드럽게 그리면 정수배로 키웠을 때 뭉개진다. 글자를 많이 쓰는 게임은 픽셀 글꼴을 넣는다.
- 게임 로직은 `_physics_process` 에 둔다 (`_process` 는 보간·연출만).
- Godot 은 스크립트 오류가 나도 종료 코드 0 을 낸다. `engine test` 가 출력의 `SCRIPT ERROR` 를 잡아 실패시키므로 이것으로 확인한다.
- 스크립트나 에셋을 추가한 뒤 직접 `godot` 을 실행할 때는 먼저 `godot --headless --path . --import` 를 돌린다 (`gf engine` 명령은 알아서 한다).

## 에셋

이 게임은 `scripts/view/` 가 도형으로 직접 그린다. 템플릿의 플랫포머 플레이어는 없으므로, 아래에서 플레이어가 그림을 자동으로 바꿔 쓰는 부분(`player_walk.tres`, `player_sheet.png`, `Player.jumped`)은 해당하지 않는다. 그림은 `Actors`/`Scenery` 의 해당 함수에서 `SpriteSheet` 도우미로 바꿔 넣고, 소리는 `Fx.consume` 이 받는 사건에 건다.

- `gf post sheet --name player_walk --out assets/game/sprites` 가 만든 `assets/game/sprites/player_walk.tres`(SpriteFrames)가 있으면 플레이어가 그것을 걷기 애니메이션으로 쓴다(`SpriteSheet.from_frames`: 첫 프레임이 대기 자세, 발이 충돌 상자 바닥에 온다, 그림은 오른쪽을 보게 만든다). 다른 캐릭터도 같은 함수로 불러온다.
- 정지 그림은 `SpriteSheet.standing(경로, 상자 크기)`(아래 가운데를 판정 상자의 아래 가운데에 놓는다. 늘리지 않는다), 바닥처럼 반복되는 그림은 `SpriteSheet.tiled(경로, 영역, 그림의 일부)` 로 만들고, `Graybox.dress(그레이박스 노드, 그림)` 으로 도형 대신 보이게 한다. 충돌과 규칙은 그레이박스 노드가 그대로 맡는다.
- 소리는 `Sound.player(경로, 볼륨 dB, 반복 여부)` 로 재생기를 만들어 `scripts/main.gd` 에 두고 규칙의 결과에서 `play()` 한다. 점프는 `Player.jumped` 시그널에 건다. 반복할 음악은 `gf post audio-loop <원본> --out assets/game/audio/<이름>.wav` 로 다듬은 .wav 를 쓴다(mp3 는 압축이 이음매를 흐트러뜨릴 수 있다). 넣은 뒤 `$GF engine audio` 로 실행 중에 소리가 나고 반복되는지 잰다.
- 스프라이트 시트는 `assets/game/` 에 PNG 로 둔다. `assets/game/player_sheet.png`(16x16 칸)가 있으면 플레이어가 그레이박스 사각형 대신 그것을 쓴다(`scripts/player.gd`). 다른 시트는 `SpriteSheet.make_sprite(경로, 칸 크기, {애니메이션: [칸 번호]})` 로 불러온다.
- `captures/`, `assets/raw/`, `references/`, `design/` 에는 `.gdignore` 가 있어 Godot 이 가져오지 않는다. 지우지 않는다. 게임이 쓰는 파일은 `assets/game/` 에만 둔다.
- 생성 원본은 `assets/raw/`, 후처리가 끝난 게임용 파일만 `assets/game/` 에 둔다. 게임 코드는 `assets/game/` 만 참조한다.
- 특정 기존 게임의 캐릭터·레벨·이름을 재현하지 않는다.
