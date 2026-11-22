# Godot 2D 게임 (픽셀 아트 겸용)

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

`gf/gf_bridge.gd`(오토로드 `GfBridge`)는 고치지 않는다. 게임은 `scripts/main.gd` 의 `_ready` 에서 `GfBridge.info` 와 `GfBridge.state_provider` 를 채운다. 메인 씬을 바꿔도 이 등록은 유지한다.

계약 전문은 하네스의 `templates/README.md` 에 있다. 요점:

- 상태 스냅샷의 필수 필드(`level`, `player.pos`, `player.vel`, `goal.pos`, `goal.reached`, `deaths`)를 유지한다. 게임에 맞게 필드를 더하는 것은 좋다(점수, 체력 등). 매 틱 변하는 타이머는 넣지 않는다.
- 입력은 액션 이름으로만 읽는다. 액션을 추가하면 `info.actions` 에도 넣는다.
- 게임 규칙은 고정 틱에서만 진행하고, 벽시계를 읽지 않고, 난수는 시드를 따른다. 그래야 재생이 원본과 일치한다.
- 플레이어·목표의 의미가 바뀌는 게임(목표가 여럿, 플레이어가 없음)이면 가장 가까운 것으로 채운다: `goal.reached` = 현재 레벨의 승리 조건, `deaths` = 실패 횟수.

## 구조

```
project.godot        입력 맵(left/right/jump), 픽셀 설정, 오토로드
scenes/main.tscn     루트 씬 (카메라, HUD)
scripts/level.gd     레벨 데이터 (상수). 그레이박스 단계에서는 여기만 고친다
scripts/main.gd      레벨 조립, 규칙(목표·위험물·낙사), 브리지 등록
scripts/player.gd    캐릭터 컨트롤러 (CharacterBody2D)
scripts/graybox.gd   도형 도우미
scripts/sprite_sheet.gd   스프라이트 시트 → SpriteFrames
bot/clear.json       레벨을 깨는 액션 스크립트
```

- 픽셀 퍼펙트 설정: 기준 해상도 320x180, 스트레치 `viewport` + 정수배, 텍스처 필터 nearest, 2D 변환·정점 픽셀 스냅. 픽셀 아트가 아니어도 그대로 두고, 고해상도 2D 로 갈 때만 사용자와 상의해 바꾼다.
- 게임 로직은 `_physics_process` 에 둔다 (`_process` 는 보간·연출만).
- Godot 은 스크립트 오류가 나도 종료 코드 0 을 낸다. `engine test` 가 출력의 `SCRIPT ERROR` 를 잡아 실패시키므로 이것으로 확인한다.
- 스크립트나 에셋을 추가한 뒤 직접 `godot` 을 실행할 때는 먼저 `godot --headless --path . --import` 를 돌린다 (`gf engine` 명령은 알아서 한다).

## 에셋

- `gf post sheet --name player_walk --out assets/game/sprites` 가 만든 `assets/game/sprites/player_walk.tres`(SpriteFrames)가 있으면 플레이어가 그것을 걷기 애니메이션으로 쓴다(`SpriteSheet.from_frames`: 첫 프레임이 대기 자세, 발이 충돌 상자 바닥에 온다, 그림은 오른쪽을 보게 만든다). 다른 캐릭터도 같은 함수로 불러온다.
- 스프라이트 시트는 `assets/game/` 에 PNG 로 둔다. `assets/game/player_sheet.png`(16x16 칸)가 있으면 플레이어가 그레이박스 사각형 대신 그것을 쓴다(`scripts/player.gd`). 다른 시트는 `SpriteSheet.make_sprite(경로, 칸 크기, {애니메이션: [칸 번호]})` 로 불러온다.
- `captures/`, `assets/raw/`, `references/`, `design/` 에는 `.gdignore` 가 있어 Godot 이 가져오지 않는다. 지우지 않는다. 게임이 쓰는 파일은 `assets/game/` 에만 둔다.
- 생성 원본은 `assets/raw/`, 후처리가 끝난 게임용 파일만 `assets/game/` 에 둔다. 게임 코드는 `assets/game/` 만 참조한다.
- 특정 기존 게임의 캐릭터·레벨·이름을 재현하지 않는다.
