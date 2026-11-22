---
name: gf-ui
description: 게임의 UI, HUD, 메뉴, 타이틀 화면, 버튼, 패널, 아이콘, 글꼴, 체력바, 점수 표시를 만들어 달라거나 "UI 가 밋밋하다/안 읽힌다/게임과 따로 논다"를 고쳐 달라는 요청에는, UI 코드를 짜기 전에 먼저 이 스킬을 쓴다. gameforge 의 assets 단계: 코드만으로 만든 UI 는 싸구려로 보이므로 기준 화면과 같은 룩의 생성 텍스처를 입히고 배치와 동작만 코드로 한다.
---

# UI: 코드만으로 만들지 않는다

기본 위젯과 평면 사각형으로 만든 UI 는 게임 전체를 "AI 가 대충 만든 것"으로 보이게 한다. UI 도 에셋이다. 기준 화면의 룩으로 **패널·버튼·아이콘 텍스처를 생성**해 입히고, 배치와 동작만 코드로 한다. UI 는 제약이 강할수록 잘 나온다: 요소 수를 줄이고 규칙을 먼저 정한다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 1. 목록과 규칙을 먼저 정한다

`design/brief.md` 와 `design/art-direction.md` 의 UI 절을 읽고, 화면별로 **꼭 필요한 것만** 적어 사용자에게 보여 준다.

| 화면 | 요소 (예) |
|---|---|
| 플레이 중 HUD | 체력/점수/남은 것 — 세 개 이하 |
| 타이틀 | 제목, 시작, (설정) |
| 일시정지 / 결과 | 다시 하기, 나가기, 기록 |

규칙: 글꼴 1~2종, 크기 2~3단계, 색은 팔레트에서, HUD 는 화면 가장자리의 10% 안쪽, 게임 화면을 가리지 않는다. 플레이어가 지금 봐야 하는 숫자 하나가 가장 크다.

## 2. UI 목업 한 장

기준 화면에 UI 를 얹은 그림을 먼저 만들어 방향을 정한다. 기준 화면에 이미 UI 가 있으면 건너뛴다.

```sh
$GF gen edit "add a game HUD to this screenshot, same art style: <요소와 위치>, minimal, readable, no extra decorations" \
  --image design/look/frame.png --aspect 16:9 --resolution 1K --out design/look --name ui-mock
```

Read 로 보고 사용자에게 보여 준다. 승인된 목업(`design/look/ui-mock.png`)이 UI 심사의 목표다. 목업 속 글자는 틀리게 나오는 일이 많다. 글자는 참고하지 않는다.

## 3. 부품 텍스처를 만든다

글자가 들어간 그림을 생성하지 않는다(모델이 글자를 틀린다). **빈 부품**을 만들고 글자는 엔진이 글꼴로 그린다.

```sh
# 패널·버튼: 목업을 참조로, 단색 배경에 부품 하나만
$GF gen edit "a single empty UI panel in the style of the reference HUD, no text, no icons, front view, flat solid pure magenta #FF00FF background" \
  --image design/look/ui-mock.png --aspect 1:1 --resolution 0.5K --out assets/raw/ui --name panel
$GF post chroma assets/raw/ui/panel.png --key auto --out assets/game/ui

# 아이콘 묶음: 한 장에 격자로 받아 스타일을 맞춘다 → 잘라 쓴다 (엔진의 atlas 영역 지정 또는 이미지 편집)
$GF gen edit "a 3x2 grid of game UI icons in the style of the reference: <heart, coin, key, ...>, each icon centered in its cell, no text, flat solid pure magenta #FF00FF background" \
  --image design/look/ui-mock.png --aspect 3:2 --resolution 1K --out assets/raw/ui --name icons
$GF post chroma assets/raw/ui/icons.png --key auto --out assets/game/ui
$GF post inspect assets/game/ui/panel.png --check captures/inspect/ui-panel.png
```

- 패널은 가운데가 비고 테두리가 일정한 형태로 받아야 9-slice(Godot `NinePatchRect`/`StyleBoxTexture`, web 은 `border-image` 나 캔버스 9칸 그리기)로 늘릴 수 있다. 모서리 장식이 변마다 다르면 다시 만든다.
- **픽셀 스타일**이면 UI 텍스처도 픽셀 사슬을 거친다(`gf-assets-pixel`: `chroma --hard` → `pixel-snap` → `palette apply`). `assets/game/` 의 PNG 는 전부 `check assets` 의 픽셀 검사를 받는다.
- 글꼴은 생성하지 않는다. 라이선스가 허용하는 글꼴 파일을 사용자가 고르게 하고 `assets/game/fonts/` 에 둔다. 픽셀 게임은 픽셀 글꼴을 정수배 크기로만 쓴다.
- 타이틀 로고는 글자를 엔진 글꼴로 그리고 뒤에 생성한 장식·배경을 깐다. 특정 게임의 로고·글자 모양을 닮게 하지 않는다.

## 4. 조립하고 확인한다

코드로 배치하고, 화면마다 스크린샷을 찍는다. 메뉴처럼 입력이 필요한 화면은 액션 스크립트로 연다.

```sh
$GF check assets
$GF engine test
$GF engine capture --out captures/ui-hud --at 1,3
$GF engine capture --out captures/ui-pause --script bot/<일시정지 여는 입력>.json --at 1.5
$GF engine capture --out captures/ui-small --size 960x540 --at 1        # 작은 창에서도 읽히는가
```

Read 로 보고 확인한다: 글자가 가장 어두운 배경과 가장 밝은 배경 위에서 모두 읽히는가, HUD 가 플레이어·위험물을 가리지 않는가, 숫자가 실제 상태(`capture.json` 의 상태)와 같은가, 작은 창에서 글자가 뭉개지지 않는가. UI 를 여는 입력은 `info.actions` 에 넣어 `engine test` 의 입력 생존 검사를 받는다.

판정은 `gf-verify` 의 블라인드 심사로 한다(목표 `design/look/ui-mock.png`, 항목 `ui_legibility`). 메뉴를 실제로 눌러 보는 것은 사람 몫이다: `$GF engine run` 으로 사용자에게 한 바퀴 눌러 보게 한다.
