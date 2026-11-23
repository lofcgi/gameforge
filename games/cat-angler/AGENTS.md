# 고양이 낚시꾼 (Godot 2D 픽셀 아트)

gameforge 하네스가 만든 게임 프로젝트다. 이 파일은 이 프로젝트에서 일하는 코딩 에이전트를 위한 규칙이다.

## 가장 중요한 규칙: 고친 뒤에는 직접 실행해서 화면을 본다

테스트가 통과해도 화면이 틀릴 수 있다. "고쳤다"고 말하기 전에 아래를 돌리고, 나온 PNG 를 직접 열어 본다.

```sh
gf() { uv run -q --project <harness>/tools gf --project . "$@"; }
gf engine test                                  # 부팅, 첫 화면, 콘솔 오류, 입력 생존. 변경마다 돌린다
gf engine capture --out captures/<이름> --at 1,3 [--script <액션.json>]   # 실제 렌더링 스크린샷 + 상태
gf engine bot --policy bot/smoke.json --seconds 116     # 고정 입력: 타이틀 → 컷신 건너뛰기 → 채집 → 미끼 → 출항 → 닻 → 넙치 세 마리 → 귀항 → 팔기. 균형·배치를 바꾸면 다시 만든다(bot/make_smoke.py)
gf engine bot --policy bot/full_run.py --seconds 5400 --shot-every 60 --require-goal   # 정책 봇이 타이틀부터 닫는 컷신까지 깬다
CA_BOT_ONLY=legend CA_START="boat=3,rod=3,baits=8,legendbait=1,x=2200" gf engine bot --policy bot/full_run.py --seconds 400 --require-goal   # 전설의 심해어 앞에서부터 닫는 컷신까지 (design/play-guide.md 의 디버그 시작)
gf engine perf --seconds 5                      # FPS, 드로우 콜, 메모리
gf engine audio --script bot/smoke.json         # 실시간으로 돌리며 소리가 실제로 나는지 잰다
CA_SAVE=off gf engine run --record              # 사람이 플레이하며 입력 기록 → captures/sessions/<id>.jsonl (재생할 기록은 저장을 끄고 남긴다)
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

옆에서 본 낚시 게임이다. 장소마다 화면(씬)이 따로 있고 전환 연출로 넘어간다. 설계는 `design/brief.md`, 그림과 코드가 맞물리는 계약은 `design/asset-spec.md`, 플레이 안내는 `design/play-guide.md`.

```
타이틀 → 여는 컷신 → 항구 마을 ⇄ 채집지          (마을 왼쪽 끝 ⇄ 채집지 오른쪽 끝)
                        ├ 미끼 공방 · 어시장 · 조선소 · 낚시 가게   (문 앞에서 Space/↑, 안에서 X)
                        └ 부두 → 바다(운항 ⇄ 낚시) ⇄ 섬           (부두·섬 기슭 앞에서 Space)
                                   └ 전설의 심해어를 싣고 부두에 대면 → 닫는 컷신 → 마을
```

```
project.godot              입력 맵(left/right/up/down/action/cancel/bait/hold/codex/pause/debug), 640×360 정수배, 오토로드
scenes/main.tscn           루트: Main → Stage(지금 화면), Hud, Overlay(메뉴·도감), Trans(전환), Audio
scenes/screens/*.tscn      화면 씬: title, cutscene, town, forage, island, in_bait, in_market, in_yard, in_tackle, sea
scenes/cutscenes/          컷신 씬(intro, ending). 컷신 담당이 만든다. 게임은 cutscene_host 로 틀기만 한다
scripts/main.gd            씬 관리자: 입력 → 코어 한 틱 → 코어의 scene 에 맞는 화면 씬으로 교체. 브리지 등록, 저장 칸, 디버그 시작
scripts/data.gd            균형 데이터와 글(아래 표). 균형은 여기만 고친다
scripts/layout.gd          Layout: 그림 옆 JSON(문, 재료 자리, 앉는 자리)을 읽는다. 없으면 기본 배치
scripts/assets.gd          Assets: 그림·애니메이션·글꼴·소리를 읽는 한 곳. 없는 파일은 임시 그림/무음으로 대신하고 missing 에 적는다
scripts/placeholder.gd     Placeholder: 임시 그림을 도형으로 찍는다(px.gd, pal.gd). 진짜 그림이 오면 쓰이지 않는다
scripts/save.gd            Save: user://<칸>.json 에 진행 저장
scripts/audio.gd           GameAudio: 화면·구간별 음악, 사건별 효과음
scripts/core/              결정적 코어. 노드가 아니고 그리지 않는다. 고정 틱에서만 진행하고 전역 난수(브리지 시드)를 쓴다
  game.gd                  Game: scene 과 mode, 화면 전환(goto), 컷신 진행, 히트스톱, 사건 목록(events), 난파, 귀항, 브리지 상태 snapshot()
  walk.gd                  Walk: 걷는 화면(마을·채집지·섬). 문, 줍기, 배 타기, 화면 끝으로 나가기
  shop.gd                  Shop: 가게 안. 주인의 대사(한 글자씩)와 가게별 거래(만들기·팔기·수리·개조·낚싯대)
  menu.gd                  Menu: 화면을 덮는 것(타이틀 메뉴, 일시정지, 조작 안내, 알림, 어창, 도감)
  guide.gd                 Guide: 첫 출항 길잡이(할 일 한 줄과 가리킬 곳)
  sea.gd, sailing.gd, shoal.gd, fishing.gd, inventory.gd   바다의 모양, 운항·파도·어군·떠다니는 물건, 물고기, 낚시와 줄다리기, 가진 것
scripts/screens/           화면 씬의 스크립트. 코어를 읽어 그리기만 한다
  screen.gd                Screen: 바탕(고양이·효과·화살표 그리기, 전환의 초점)
  title.gd, cutscene_host.gd, walk_screen.gd(마을·채집지·섬), sea_screen.gd
  shop_screen.gd           ShopScreen: 실내 바탕(배경, 주인, 초상화와 대사 창). in_bait.gd(작업대), in_market.gd(진열대), in_yard.gd(선거), in_tackle.gd(벽의 낚싯대)
scripts/view/              hud.gd(상태 줄·할 일·조작 안내·깊이 눈금·장력), overlays.gd(메뉴·도감·빠진 에셋 목록), wipe.gd(전환), fx.gd(입자·흔들림·알림·동전)
scripts/ui/ui.gd           Ui: 9-slice 틀, 글자(역할별 글꼴), 키 표시, 게이지
scripts/cutscene/          컷신 담당의 재생기. 고치지 않는다
scripts/graybox.gd, sprite_sheet.gd, sound.gd   템플릿의 도우미(sound.gd 는 GameAudio 가 쓴다)
bot/smoke.json             고정 입력 스모크(bot/make_smoke.py 로 다시 만든다)
bot/full_run.py            끝까지 깨는 정책 봇. 균형 표와 배치를 브리지 info["data"] 에서 읽는다
bot/shot_*.json            화면 하나를 여는 짧은 입력(스크린샷용)
bot/capture_all.sh         화면마다의 스크린샷(captures/screens/)을 전부 다시 찍는다
```

화면 전환: 코어에서 `g.goto(화면, "fade" | "iris", 인자)` 를 부른다. 28틱(0.47초) 동안 입력을 받지 않고, 가운데 틱(화면이 다 가려진 때)에 `scene` 이 바뀌며 `main.gd` 가 화면 씬을 갈아 끼운다. `fade` 는 격자 무늬로 어두워지고 `iris` 는 고양이에게로 오므라든다. 다 가려진 동안에는 가운데에 물결 문양이 뜬다(하네스가 단색 스크린샷을 렌더링 실패로 보기 때문이기도 하다).

컷신: `scenes/cutscenes/<intro|ending>.tscn` 의 루트가 `finished` 를 내면 `cutscene_host` 가 `game.cut_done()` 을 부른다. 씬이 없으면 "준비 중" 임시 카드가 4초 뜬다. 규칙은 `design/asset-spec.md` 의 컷신 절.

`scripts/data.gd` 의 표 (거리·깊이는 m, 화면 좌표는 가로 `X_PX`=4, 세로 `Y_PX`=8 을 곱한다. 화면 너비 640px = 160m):

| 표 | 내용 |
|---|---|
| `ZONES` | 구간: 범위, 바닥 깊이, 잔물결 높이(amp), 큰 파도 높이(crest), 필요한 배 등급(grade) |
| `FISH`, `FISH_NOTES` | 어종 13: 구간, 장소, 깊이 범위, 어창 칸, 값, 미끼, 힘, 속도, 헤엄 방식, 마릿수, 옆으로 달아나는지 / 도감 설명 |
| `RODS`, `BOATS` | 낚싯대 3단계(닿는 깊이, 힘, 감는 속도, 값), 배 3단계(파도 등급, 내구도, 속도, 가속, 어창, 값) |
| `BAITS`, `MATS` | 미끼 4종의 재료, 재료 4종. `GATHER_YIELD` 는 종류마다 한 번 나갈 때 줍는 양 |
| `PLACES` | 암초·작은 섬·난파선·소용돌이 자리의 위치와 너비 |
| `TUG` | 줄다리기 상수 |
| `SHOPS` | 가게 넷: 실내 화면 이름, 주인, 대사(인사·상황별 한마디·물건 설명) |
| `GUIDE` | 길잡이의 단계와 글("미끼를 내리자"는 `Guide._lower_note` 가 깊이·어종·미끼 상황에 맞춰 바꿔 쓴다) |
| `NOTES`, `WRECKED`, `DELIVERED` | 병 속 쪽지, 알림 글 |

규칙:

- 코어(`scripts/core/`)는 화면을 모른다. 화면에 알릴 일은 `g.emit(종류, 데이터)` 로 `events` 에 넣고 `Fx.consume`(연출)과 `GameAudio.consume`(소리)이 받는다. 새 연출과 소리는 거기에 더한다.
- 마우스 왼쪽 버튼은 `action`(Space)에 묶여 있다(`project.godot`).
- 입력은 `main.gd` 가 액션 이름으로 읽어 `Game.step(held, pressed)` 에 넘긴다. 코어 안에서는 `g.held()`, `g.pressed()` 만 쓴다. 액션을 더하면 `project.godot`, `main.gd` 의 `ACTIONS` 에 넣는다(`info.actions` 는 거기서 만든다).
- 모든 입력은 누른 틱에 상태(카운터나 값)와 화면이 바뀌어야 한다. 하는 일이 없는 키에도 반응을 준다(귀 움찔 `shrugs`, 폴짝 `hops`, 안 되는 선택 `denied`, 전환·컷신 중 `taps`). 화면 아래 조작 안내(`Hud.hints`)에는 지금 실제로 하는 일이 있는 키만 넣는다.
- 그림·글꼴·소리는 `Assets` 로만 읽는다. 경로는 `design/asset-spec.md` 의 것만 쓴다. 규격에 없는 것이 필요하면 규격에 먼저 더하고 `Assets.probe` 의 목록과 `Placeholder` 에도 넣는다.
- 브리지 상태(`Game.snapshot`)에는 입력과 무관하게 매 틱 변하는 값(물고기 위치, 파도)을 넣지 않는다. 줄다리기 중의 `tension`·`stamina` 만 예외다. 더한 필드: `scene`, `mode`(title/cut/land/shop/sail/fish), `transition`, `panel`(열린 메뉴 또는 가게의 거래), `talking`, `near`, `spots`, `guide`, `missing_count`. 빠진 에셋의 전체 목록은 `info.missing_assets`(시작할 때)와, 디버그를 켰을 때(F3 또는 `CA_DEBUG=1`) 상태의 `missing_assets` 에 있다(매 표본에 싣기에는 길어서 늘 싣지는 않는다).
- 연출(Fx)도 물리 틱에서 진행하고 따로 가진 난수기를 쓴다. 코어의 난수 순서를 건드리지 않기 위해서다.
- 저장(`Save`)은 자동 실행에서 꺼져 있다(`CA_SAVE`). 켜면 남은 저장 파일이 다음 실행의 타이틀 메뉴를 바꿔 재생이 어긋난다.
- 바다 화면(`SeaScreen`)은 세계를 2배로 당겨 그린다(`ZOOM`, 보이는 세계는 320×180). 노드의 `scale` 로 당기므로 `_draw` 안의 좌표는 세계 px(`VIEW`) 기준이고, 세계 위의 글자·화살표만 `_texts` 에 모아 마지막에 1배로 얹는다. 타이틀의 배와 문양도 같은 2배다. 다른 화면은 1배다.
- 그리기: 바다 화면은 수면 높이를 틱마다 한 번만 재서(`_surf`) 물기둥(4px), 수면선, 문양(8px 띠), 배가 함께 쓴다. 바닥은 높이가 같은 구간을 묶어 2px 단위로 놓는다. 바닥 장식·잔고기·해파리의 자리는 난수 없이 x 칸의 번호(`_pick`)와 틱으로 정한다. 틱 하나(코어 + 화면 갱신 준비)는 평균 1ms 안쪽이다(`CA_PROFILE=1` 로 잰다). 고친 뒤 `gf engine perf --uncapped` 의 평균을 본다. 창이 뒤에 있을 때의 p95 는 화면 주사에 좌우된다: 75Hz 화면에서는 타이틀도 17ms 안팎이고, `--screen 0`(120Hz)·`--screen 1`(60Hz)에서는 다섯 화면 모두 14ms 아래다.

- 좌표·크기·속도는 **기준 해상도 640×360 의 픽셀**이다(하네스 템플릿의 320×180 에서 두 배로 옮겼다. `window/size/viewport_*` 가 640×360, 창은 1280×720 = 2배).

  | | 이 프로젝트 (픽셀 아트) |
  |---|---|
  | `window/stretch/mode`, `scale_mode` | `viewport`, `integer` (640×360 으로 그린 뒤 정수배 확대: 1280×720 은 2배, 1920×1080 은 3배) |
  | `textures/canvas_textures/default_texture_filter` | `0` (nearest) |
  | `2d/snap/snap_2d_transforms_to_pixel`, `..._vertices_to_pixel` | `true` |
  | `gameforge/art/pixels_per_unit` (그림 픽셀 ÷ 화면 픽셀) | `1` |

- 창 크기가 달라져도 화면은 16:9 다. 정수배로만 커지고 가운데에 놓이며 남는 자리는 검은 띠다. HUD 는 게임 화면 안에 있어 띠에 가리지 않는다. 확인: `$GF engine capture --out captures/<이름> --size 1920x1080 [--screen N]`.
- 글자는 픽셀 글꼴(갈무리)을 제 크기로만 쓴다(`Assets.font(역할)`: body 12px, bold 12px, small 10px, large 15px). 안티에일리어싱은 끈다.
- 게임 로직은 `_physics_process` 에 둔다 (`_process` 는 보간·연출만).
- Godot 은 스크립트 오류가 나도 종료 코드 0 을 낸다. `engine test` 가 출력의 `SCRIPT ERROR` 를 잡아 실패시키므로 이것으로 확인한다. 아직 열지 않은 화면의 스크립트 오류는 그 화면을 열 때에야 드러나므로, 화면 스크립트를 고친 뒤에는 `godot --headless --path . --check-only --script <파일>` 로 파싱을 확인하고 그 화면을 캡처한다.
- 스크립트나 에셋을 추가한 뒤 직접 `godot` 을 실행할 때는 먼저 `godot --headless --path . --import` 를 돌린다 (`gf engine` 명령은 알아서 한다).

## 에셋

그림·글꼴·소리는 `assets/game/` 아래에 `design/asset-spec.md` 의 경로와 크기로 둔다. 코드는 `scripts/assets.gd`(Assets)로만 읽는다.

- `Assets.tex("boats/boat1.png")` 정지 그림, `Assets.anim("chars/cat_idle")`·`Assets.frame(...)` 애니메이션(`gf post sheet` 의 `.tres`, 없으면 PNG + JSON), `Assets.font(역할)`, `Assets.stream("coin")`.
- 파일이 없으면 `Placeholder` 의 임시 그림(소리는 무음)을 쓰고 `Assets.missing` 에 이름을 적는다. F3 으로 화면에서 보고, 브리지 `info.missing_assets` 로 읽는다. 파일을 넣으면 다음 실행부터 코드 수정 없이 쓰인다.
- 문·재료 자리·앉는 자리 같은 좌표는 그림 옆의 JSON 에 적고 `Layout` 으로 읽는다(`places/town.json`, `boats/boat1.json`, `chars/cat.json` 등). 코드에 좌표를 박지 않는다.
- 소리는 `Fx.consume` 과 같은 사건을 받는 `GameAudio.consume` 의 표(`EVENT_SOUNDS`)에 건다. 파일 경로와 재생 음량(dB)은 같은 파일의 `TRACKS` 에 적는다. 반복할 음악은 `gf post audio-loop` 로 다듬은 .wav 를 쓴다. 넣은 뒤 `$GF engine audio` 로 실행 중에 소리가 나고 반복되는지 잰다.
- `captures/`, `assets/raw/`, `references/`, `design/` 에는 `.gdignore` 가 있어 Godot 이 가져오지 않는다. 지우지 않는다. 게임이 쓰는 파일은 `assets/game/` 에만 둔다.
- 생성 원본은 `assets/raw/`, 후처리가 끝난 게임용 파일만 `assets/game/` 에 둔다. 게임 코드는 `assets/game/` 만 참조한다.
- 특정 기존 게임의 캐릭터·레벨·이름을 재현하지 않는다.
