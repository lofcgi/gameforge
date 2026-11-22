# 통합 점검 근거 (2026-11-22)

gameforge 하네스를 실제 생성물로 끝까지 돌린 결과다. 프로젝트 여섯 개가 이 폴더에 남아 있다(아래 세 개는 두 번째 점검에서 추가했다. D~G 절).

| 프로젝트 | 내용 | 지출(추정) |
|---|---|---|
| `pixel-godot` | Godot 2D 픽셀. 생성 스프라이트 4종 + 걷기 애니메이션 + 효과음 2 + 음악 1 | $0.84 |
| `model-godot` | Godot 3D. 컨셉 → 3D 모델 → Blender 정리 → 리깅 걷기 | $1.38 |
| `model-web` | three.js 3D. 위와 같은 GLB 를 그대로 사용 | $0 |
| `flat2d-godot` | Godot 2D 비픽셀(플랫 벡터 카툰, 여우). 스프라이트 4종 + 걷기 + 효과음 2 + 음악 1 | $0.74 |
| `pixel-web` | 웹 캔버스 2D 픽셀(우주인). 스프라이트 4종 + 걷기 + 효과음 2 + 음악 1. 플레이어는 한 번 다시 만들었다 | $1.16 |
| `flat2d-web` | 웹 캔버스 2D 비픽셀(과슈 동화풍, 병아리). 스프라이트 4종 + 걷기 + 효과음 2 + 음악 1 | $0.74 |

판정은 화면을 직접 보고 적었다: 좋음 / 쓸 만함 / 약함.

## A. 픽셀 2D (Godot)

- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/art/shot_02_t2.30.png` — 점프 중인 게임 화면. 캐릭터·가시·바닥이 색으로 구분되고 팔레트가 한 벌로 보인다. **좋음.** 캐릭터는 화면 높이의 약 1/8 로 작지만 읽힌다.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/graybox/shot_02_t2.30.png` — 같은 순간의 그레이박스. 위 그림과 비교용.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/art-goal/shot_02_t7.00.png` — 목표 도달(GOAL!). 등불 우체통이 가늘고 어두워 목표로서 눈에 띄지 않고, 캐릭터가 화면 오른쪽 끝에서 잘린다. **약함.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/inspect/raw-sources.png` — 생성 원본 4장(마젠타 배경). 원본 품질은 **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/inspect/static-sprites-check.png` — 1x 로 줄인 결과를 밝은·어두운 배경에 올린 것. 마젠타 테두리 없음. 로봇·타일 **좋음**, 가시덤불(1번)은 붉은 가시가 전부 갈색으로 뭉쳐 **약함** → 굵은 결정 모양으로 다시 생성해 교체했다(`captures/inspect/spikes.png`).
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/inspect/player-walk-loop.png` — 영상에서 고른 12프레임 반복 구간(원본 해상도). 다리가 번갈아 벌어졌다 모인다. 걷기로 읽힌다. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/inspect/player_walk_sheet.png` — 같은 구간의 1x 시트(21x25, 12색). 다리 움직임은 남았지만 다리가 5px 로 짧고 어두워 어두운 배경에서는 약하게 읽힌다. 가방 색이 프레임마다 조금 바뀐다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/inspect/art-walk-ingame.png` — 게임 안에서 걷는 연속 4장. 프레임이 바뀌는 것이 보인다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/judge/graybox-vs-art/X.png`, `Y.png` — 블라인드 심사 쌍. 맥락 없는 새 서브에이전트가 아트 쪽을 골랐다(가독성 7 대 5, 일관성 7 대 3). 지적: 바닥 타일 반복 무늬, 단색 기둥과 지형의 밀도 차이, 등 쪽 갈색 물체가 모호함.

## B. 생성 모델 3D (Godot, three.js)

- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/assets/raw/concept/scout.png` — 컨셉 이미지(A-포즈, 정면). **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/turntable/player_sheet.png` — 정리·감량(3,000 삼각형)·크기 맞춤 뒤 턴테이블. 0번이 정면(얼굴)이다. 텍스처 유지. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/inspect/facing-closeup.png` — Godot 에서 앞·오른쪽·뒤·왼쪽으로 걸을 때의 확대. 네 방향 모두 진행 방향을 본다. 발이 바닥에 닿고 그림자가 붙어 있다. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/model-web/captures/inspect/facing-closeup.png` — three.js 에서 같은 네 방향. 방향·접지·그림자 모두 맞다. **좋음.** (고치기 전에는 그림자가 캐릭터에서 떨어져 떠 보였다.)
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/inspect/rigged-walk-closeup.png` — 리깅된 걷기 애니메이션의 연속 화면(Godot). 다리와 팔 위치가 프레임마다 바뀐다. 다리가 짧고 뒤에서는 가방에 가려 약하게 읽힌다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/model-web/captures/inspect/rigged-walk-closeup.png` — 같은 것(three.js). **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/inspect/model-sheet.png`, `/Users/iyeonsang/Desktop/game/demo-check/model-web/captures/inspect/model-sheet.png` — 게임 카메라에서 본 진행 화면(1초, 점프 중, 4초, 목표). 캐릭터는 화면 높이의 약 1/8. 목표 화면에서 캐릭터가 등불 기둥 뒤에 가려진다(배치 문제). 레벨 자체는 회색 상자 그대로다. **쓸 만함.**

## C. 레퍼런스

- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/references/sheets/inbox-01.png` — 모음판(스팀 3장 + 로컬 2장). 한 작품에서 3장을 고르자 편중 경고가 나왔고, 2장을 빼자 사라졌다.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/references/picked/traits-palette.png` — 고른 것과 "아님"의 색 견본.

## 숫자

| 항목 | pixel-godot | model-godot | model-web |
|---|---|---|---|
| `engine test` | 5개 항목 통과 | 통과 | 통과 |
| 고정 입력 봇(`bot/clear.json`) | 목표 도달 6.6초, 사망 0 | 5.4초, 사망 0 | 5.4초, 사망 0 |
| 내장 `goal` 봇 | 12.65초, 사망 2 | 13.65초, 사망 2 | 12.6초, 사망 2 |
| 성능(5초) | 평균 74.8 fps, 드로우 콜 8 | 평균 75.1 fps, 드로우 콜 49, 프리미티브 12,902 | 60.0 fps, 드로우 콜 53, 삼각형 6,601 |
| 에셋 | 팔레트 16색, 스프라이트 7~12색, 걷기 12프레임 @12fps(1초) | 플레이어 3,000 삼각형, 등불 60 삼각형 | 같은 GLB |
| 오디오 | jump 0.48초 최대 -1.2 dB, goal 1.2초 -3.9 dB, theme 10.0초 -1.3 dB | 없음 | 없음 |

## 확인하지 못한 것

- 소리는 길이와 음량만 쟀다. 듣지 못했다. 음악이 매끄럽게 반복되는지도 모른다.
- 움직임의 느낌(걷기 속도와 이동 속도의 어울림, 발 미끄러짐)은 정지 화면으로만 봤다.
- (2026-11-23 제거) 레퍼런스용 크롬 확장과 수신 서버(`gf ref serve`)는 하네스에서 뺐다. 그 점검 폴더 `ext-check/` 도 함께 휴지통으로 옮겼다. 레퍼런스 탐색은 Claude in Chrome 도구 + `gf ref add` 로 한다.
- 사람 플레이 기록·재생(`engine run --record`, `replay`)은 이번에 돌리지 않았다.
- (첫 점검 때) 비픽셀 2D 사슬과 web-2d 의 에셋 통합은 돌리지 않았다 → 두 번째 점검(D~G)에서 돌렸다.

---

# 두 번째 점검: 2D 의 나머지 세 조합 (2026-11-22)

Godot + 비픽셀 2D, 웹 + 픽셀 2D, 웹 + 비픽셀 2D 를 실제 생성물로 끝까지 돌렸다. 세 프로젝트의 그림은 서로 다른 생성물이다(영상·프레임을 나눠 쓰지 않았다). 유료 호출 합계 추정 $2.63 (이미지 13장 $1.04, 스프라이트 영상 4개 $1.34, 음악 3개 $0.24, 효과음 6개 $0.01). 다시 만든 것은 pixel-web 의 플레이어 이미지와 영상 한 번이다.

## D. 비픽셀 2D (Godot) — `flat2d-godot`

- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/graybox/shot_02_t2.30.png` — `init --style 2d` 직후의 그레이박스. 글자와 도형이 1280x720 해상도로 또렷하다(스트레치 canvas_items).
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/inspect/raw-sources.png` — 생성 원본 4장(마젠타 배경, 1024px). 선 굵기와 색이 한 벌로 보인다. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/inspect/static-sprites-check.png` — `post chroma` → `post resize --trim` 결과를 밝은·어두운 배경에 올린 것. 마젠타 테두리 없음, 외곽선이 매끈하다. **좋음.** (이 그림의 바닥 타일은 테두리 선을 덜 자른 첫 판이다. 게임에는 `--inset 26` 으로 다시 만든 것이 들어갔다.)
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/inspect/player-walk-loop.png` — 영상에서 고른 12프레임 반복 구간. 두 다리가 번갈아 나가고 꼬리가 흔들린다. 걷기로 읽힌다. **좋음.** 영상 모델이 정지 그림(정면에 가까움)과 다른 옆모습으로 돌려 버려서 정지 스프라이트는 게임에서 쓰지 않는다.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/art/shot_03_t2.30.png` — 점프 중. 그림이 부드럽게(선형 필터, 1:1) 나오고 여우·덩굴·바닥이 한 스타일이다. **좋음.** 캐릭터는 화면 높이의 약 1/7 로 작고 화면 위쪽 2/3 가 비어 있다(레벨·카메라 설계의 한계).
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/art/shot_04_t3.10.png` — 가시덤불 앞. 덩굴이 40px 높이라 붉은 가시가 작게 보인다. 위험물로는 읽히지만 약하다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/art/shot_06_t7.20.png` — 목표 도달(GOAL!). 여우가 도토리 푯대 옆에 서 있고 잘리지 않는다. **좋음.** 푯대가 가늘어 멀리서는 눈에 덜 띈다.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/inspect/art-walk-ingame.png` — 게임 안 연속 8장: 오른쪽으로 걷기 5장, 멈춤, 왼쪽으로 걷기, 왼쪽을 본 채 멈춤. 프레임이 바뀌고, 방향이 뒤집히고, 발이 풀 위에 닿는다. **좋음.** 대기 자세가 걷기 첫 프레임(한 발을 든 자세)이라 멈춰 있어도 걷는 중처럼 보인다. **약함.**

## E. 픽셀 2D (웹) — `pixel-web`

- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/raw-sources.png` — 처음 생성한 원본 4장. 우주인은 주름·패널이 많다.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/player-walk-all.png` — 첫 우주인의 영상 프레임 37장. 원본 해상도에서는 걷기가 좋다. 그러나 24px 로 줄이자 음영이 흰 몸통 위의 어두운 점들로 남아 지저분했다(**약함**, 채택하지 않음).
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/assets/raw/pix/player2.png` — 다시 생성한 단순한 우주인(큰 색면, 음영 한 단계). 이것을 채택했다.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/player2-walk-all.png` — 다시 만든 영상의 프레임 37장. 다리가 번갈아 크게 나간다. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/player_walk_sheet.png` — 1x 시트(16x24, 11프레임, 11색)를 밝은·어두운 배경에 올린 것. 마젠타 없음. 어두운 배경에서 형태와 다리가 읽힌다. 밝은 배경에서는 흰 옷의 외곽선이 군데군데 끊긴다(게임 배경은 어둡다). **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/static-sprites-check.png` — 정지 스프라이트 4종의 1x(8배 확대). 우주인·깃발 **좋음**, 선인장(20x16)은 흰 가시가 점으로 남아 "가시 달린 초록 덩어리"로 읽힌다 **쓸 만함**, 바닥 타일은 벽돌 줄눈이 점무늬로 뭉쳤다 **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/art/shot_03_t2.30.png` — 점프 중. 스크린샷이 정확히 4배 정수 확대다(`post inspect` 의 `integer_scale: 4`). 팔레트가 한 벌이고 플레이어가 배경에서 분리된다. **좋음.** HUD 글자는 DOM 으로 옮겨 또렷하다(고치기 전에는 8px 캔버스 글자가 뭉개졌다).
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/art/shot_06_t7.20.png` — 목표 도달. 깃발과 우주인이 나란히 보인다. **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/inspect/art-walk-ingame.png` — 게임 안 연속 8장(걷기, 멈춤, 왼쪽 걷기, 왼쪽을 본 채 멈춤). 프레임이 바뀌고 뒤집힌다. **좋음.**

## F. 비픽셀 2D (웹) — `flat2d-web`

- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/inspect/raw-sources.png` — 생성 원본 4장(초록 배경). 초록이 순수한 #00FF00 이 아니라 #08C520 쯤이고 얼룩이 있다. 그림 자체는 **좋음.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/inspect/static-sprites-check-v1.png` — `post chroma --key auto` → `post resize --trim` 결과(4배 확대, 밝은·어두운 배경). 붓 질감의 부드러운 가장자리인데도 초록 테두리가 없다. **좋음.** 등불의 크림색 후광은 불투명한 덩어리라 어두운 배경에서 스티커처럼 보인다. **약함.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/inspect/player-walk-loop.png` — 12프레임 반복 구간. 부츠가 번갈아 나간다. 다리가 짧아 보폭은 작다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/inspect/player_walk_sheet.png` — 줄인 시트(67x104)의 아랫줄을 밝은·어두운 배경에. 가장자리 깨끗함. 마지막 프레임의 부츠 위에 초록 섞인 점이 하나 남았다(다리 사이의 움직임 번짐). **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/art/shot_04_t3.10.png` — 가시공 앞. 캔버스가 1280x720 으로 만들어져 그림이 부드럽고 1:1 이다. 크림색 병아리가 어두운 배경에서 가장 먼저 보이고 산호색 가시공이 위험물로 읽힌다. **좋음.** 바닥 타일의 바위 무늬가 32 단위마다 반복되는 것이 보인다.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/art/shot_06_t7.20.png` — 목표 도달. 병아리가 등불 기둥 앞에 선다. 후광 덩어리가 어색하다. **쓸 만함.**
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/inspect/art-walk-ingame.png` — 게임 안 연속 8장. 프레임이 바뀌고 뒤집히고 발이 이끼 위에 닿는다. **좋음.**

## G. 두 번째 점검의 숫자

| 항목 | flat2d-godot | pixel-web | flat2d-web |
|---|---|---|---|
| 화면 설정(`init` 의 `render`) | 단위당 4px, linear, 창 해상도 | 단위당 1px, nearest, 정수배 | 단위당 4px, linear, 창 해상도 |
| `engine test` | 5개 항목 통과 | 통과 | 통과 |
| 고정 입력 봇(`bot/clear.json`) | 6.6초, 사망 0 | 6.6초, 사망 0 | 6.6초, 사망 0 |
| 내장 `goal` 봇 | 12.65초, 사망 2 | 12.55초, 사망 2 | 12.55초, 사망 2 |
| 성능(5초) | 평균 75.0 fps, 드로우 콜 15 | 60.0 fps, 프레임당 JS 0.21 ms | 60.0 fps, 프레임당 JS 0.29 ms |
| 플레이어 걷기 | 93x104 px, 12프레임 @12fps(1초) | 16x24 px, 11프레임 @12fps(0.92초) | 67x104 px, 12프레임 @12fps(1초) |
| 정지 그림 | 가시덤불 73x40, 푯대 54x160, 타일 128x128 | 선인장 20x16, 깃발 14x32, 타일 32x32. 팔레트 16색, 그림당 5~11색 | 가시공 60x48, 등불 121x160, 타일 128x128 |
| 오디오(길이, 최대 음량) | jump 0.48초 -1.5 dB, goal 1.2초 -2.2 dB, theme 8.0초 -1.0 dB | jump 0.48초 -1.6 dB, goal 1.2초 -1.6 dB, theme 8.0초 -4.2 dB | jump 0.48초 -9.5 dB, goal 1.2초 -11.6 dB(작다. 음악을 낮춰 맞춤), theme 8.0초 -1.2 dB |
| 소리 재생 확인 | 상태의 `sounds_jump` 3, `sounds_goal` 1 | 첫 입력 전 잠김 → 입력 뒤 `__audio.started` = jump 2, theme 1, 콘솔 경고 0 | 같음 |
| `check assets` / `audio --require` / `evidence` | 통과 | 통과 | 통과 |

기존 프로젝트 재확인: `pixel-godot`, `model-godot`, `model-web` 의 `engine test` 통과, 고정 입력 봇 6.6초 / 5.4초 / 5.4초. `pixel-godot` 스크린샷은 여전히 4배 정수 확대다(`/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/recheck/shot_02_t2.30.png`).

## 두 번째 점검에서 확인하지 못한 것

- 소리는 듣지 못했다. 길이·음량과 재생 호출 횟수만 확인했다. 음악이 매끄럽게 반복되는지, 웹에서 사람이 눌렀을 때 실제로 들리는지 모른다(자동 실행의 Chrome 은 소리를 내보내지 않는다).
- 움직임은 정지 화면 연속으로만 봤다. 걷기 속도와 이동 속도의 어울림, 발 미끄러짐은 사람이 봐야 한다.
- 고해상도 2D 는 1280x720 창에서만 찍었다. 다른 창 크기, 레티나(devicePixelRatio 2), 전체 화면에서의 모습은 확인하지 않았다.
- Godot 자동 실행에서 누르고 있던 키가 도중에 풀리는 일이 두 차례(연속 3~4회씩) 있었다가 사라졌다. 브리지가 풀린 키를 다시 누르게 고쳤고 흉내 낸 키 해제로는 확인했지만, 실제 원인(창 포커스 상실로 추정)은 재현하지 못했다. 두 번째 때는 뒤이은 점프 입력도 먹지 않았는데 이 부분은 설명하지 못했다.
- 블라인드 심사, 사람 플레이 기록·재생은 이번에도 돌리지 않았다.

## H. 세 번째 점검 (2026-11-22): 소리·실제 키·키 풀림·화면 크기

아래 숫자는 전부 측정이다. 소리는 듣지 않았고, 키는 손으로 누르지 않았다.

### 소리 (실행 중 신호 + 파일)

- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/audio/result.json` — 실시간 실행에서 마스터 버스 피크 -6.2 dB, RMS -25.5 dB. jump.mp3 3회(점프 입력 3회 직후), goal.mp3 1회(목표 도달 틱), theme.wav 가 8.5초 반복 지점을 넘어 계속 재생, 반복 지점의 끊김 0.0ms.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/audio/result.json` — 피크 -7.7 dB, RMS -28.4 dB. jump 3, goal 1, 반복 1회 확인, 끊김 0.0ms.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/audio/result.json` — 첫 입력 전 AudioContext 0개·신호 없음, 자동 재생 경고 0건. 입력 뒤 피크 -8.0 dB, RMS -28.4 dB. jump 3, goal 1, 반복 확인, 끊김 0.1ms (headless Chrome 의 destination 직전 신호).
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/audio/result.json` — 첫 입력 전 무음, 피크 -9.5 dB, RMS -31.5 dB. jump 3, goal 1, 반복 확인, 끊김 0.1ms.
- 효과음과 음악의 균형(점프 직전 → 직후 피크): pixel-godot -16 → -7 dB, flat2d-godot -21 → -10 dB, pixel-web -20 → -10 dB, flat2d-web -30 → -9 dB(음악이 20 dB 낮다. 작게 들릴 수 있다).
- 반복 이음매(고치기 전 mp3 → `post audio-loop` 뒤 wav). 네 곡 모두 고치기 전에는 기준을 넘었다.
  - `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/assets/game/audio/theme.wav` — 앞뒤 무음 11.2ms → 0, 겹침 1.52초(박자 상관 0.78), 10.03초 → 8.50초. 통과.
  - `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/assets/game/audio/theme.wav` — 앞뒤 무음 25.5ms, 끝이 18.4 dB 잦아듦, 음색 차이 3.31배 → 0ms, -0.4 dB, 0.39배. 겹침 0.69초, 8.04초 → 7.33초. 통과.
  - `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/assets/game/audio/theme.wav` — 앞뒤 무음 23.2ms → 0. 겹침 0.25초, 8.04초 → 7.77초. 통과(음색 차이 1.09배, 기준 1.5배).
  - `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/assets/game/audio/theme.wav` — 앞뒤 무음 24.4ms → 0. 겹침 0.42초(박자 상관 0.39 로 낮다), 8.04초 → 7.60초. 통과.
- 고치기 전 실행 중 반복 지점의 끊김: Chrome 19.2ms, Godot 9.5ms. 고친 뒤 0.1ms, 0.0ms.
- 파일 검사(`check audio`): 네 프로젝트 모두 잘림 0곳, 직류 치우침 0.0007 이하, 경고 0건. flat2d-web 의 jump.mp3 는 앞 무음 25.7ms(기준 30ms 안쪽).

### 실제 키 입력과 기록·재생

- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/sessions/os-keys.jsonl` — macOS Quartz 키 이벤트(CGEventPostToPid)로 `bot/clear.json` 을 넣어 기록. 보낸 7개가 전부 기록됨. 재생 `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/replays/os-keys/replay.json`: 위치 차이 최대 0.0, 반응 없는 입력 0, 목표 도달.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/replays/os-keys/replay.json` — 8개 기록, 차이 0.0, 목표 도달.
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/replays/os-keys/replay.json` — 7개 기록, 차이 0.0, 목표 도달.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/replays/os-keys/replay.json` — 헤드 있는 Chrome 창에 같은 방식으로 8개, 차이 0.0, 목표 도달.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/replays/os-keys/replay.json` — 8개, 차이 0.0.
- `/Users/iyeonsang/Desktop/game/demo-check/model-web/captures/replays/os-keys/replay.json` — 7개, 차이 0.0.
- 이 점검에서 찾아 고친 것: Godot 재생의 점프가 매번 한 틱 늦던 것(차이 최대 3.56 → 0), web 에서 한 틱보다 짧게 친 키가 사라지던 것, Godot 의 마우스 위치가 스트레치 배율로 나뉘어 기록되던 것, 키를 누른 채 창을 떠나면 기록에 뗌이 남지 않던 것(차이 200 넘음 → 0).
- 마우스: Godot 은 실제 커서 클릭(HID 수준 Quartz 이벤트)과 브리지 주입 둘 다 기록·재생 확인, web 은 CDP 클릭으로 확인(임시 사본에서 했고 파일은 남기지 않았다). 게임패드: Godot 에 브리지로 넣은 버튼만 확인. 실제 패드와 web 게임패드는 확인하지 않았다.

### Godot 키 풀림

- 원인: 앱이 포커스를 잃으면 Godot 이 눌린 키·액션을 전부 뗀다(`SceneTree` 의 `NOTIFICATION_APPLICATION_FOCUS_OUT` → `Input.release_pressed_events`). 터미널에서 띄운 Godot 은 시작 직후 스스로 포커스를 내줬다 되찾고, 그 뒤에는 다른 앱이 앞에 올 때마다 잃는다.
- 같은 45회 반복(세 Godot 데모, 포커스를 일부러 흔드는 다섯 방식): 고치기 전 39회에서 눌러 둔 키가 풀림(아무것도 하지 않은 9회 중 4회 포함) → 고친 뒤 0회. 고친 뒤 45회의 최종 상태는 프로젝트별로 전부 같다.
- web 의 자동 실행은 다른 탭·다른 앱을 앞으로 보내도 blur 0건(9회).

### 화면 크기 (직접 본 스크린샷)

- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/sizes/4x3-1024x768/shot_01_t2.30.png` — 위아래 검은 띠, 16:9 유지, HUD 가 게임 화면 안 왼쪽 위. 좋음.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/sizes/21x9-2560x1080/shot_01_t2.30.png` — 좌우 검은 띠. 잘린 것 없음. 좋음.
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-godot/captures/sizes/small-960x540/shot_01_t2.30.png` — 그림과 글자가 선명하다. 좋음. (`1920x1080` 도 같은 폴더 옆에 있다.)
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/sizes/1366x768/shot_01_t2.30.png` — 4배(1280x720) + 사방 띠. HUD 글자의 안티에일리어싱을 꺼서 또렷해졌다(색 107개 → 18개). 쓸 만함(기본 글꼴이라 a 와 t 가 붙어 보인다).
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/sizes/1000x700/shot_01_t2.30.png` — 3배(960x540), 띠의 위치가 실제 창 캡처와 같다.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-godot/captures/sizes/fullscreen-3024x1898/shot.png` — 내장 레티나 화면의 전체 화면. 9배(2880x1620) + 띠. 좋음.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/sizes/1000x700/shot_01_t2.30.png` — 3배 + 페이지 배경색 띠. 가로·세로 색 경계 간격이 전부 3의 배수.
- `/Users/iyeonsang/Desktop/game/demo-check/pixel-web/captures/sizes/retina-1366x768/shot_01_t2.30.png` — 배율 2, 2732x1536. 간격이 전부 8의 배수. 배율 1.5(`dpr1.5-1366x768`)와 1.25(`dpr1.25-1000x700`)도 6, 3의 배수로 고르다(고치기 전에는 한 축이 어긋났다).
- `/Users/iyeonsang/Desktop/game/demo-check/flat2d-web/captures/sizes/21x9-2560x1080/shot_01_t2.30.png` — 좌우 띠, HUD 또렷. 좋음. 같은 폴더 옆에 `1920x1080`, `4x3-1024x768`, `small-960x540`, `retina-1280x720`, `fullscreen-mbp-1512x982`.
- `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/sizes/21x9-2560x1080/shot_01_t2.30.png`, `/Users/iyeonsang/Desktop/game/demo-check/model-godot/captures/sizes/4x3-1024x768/shot_01_t2.30.png` — 늘어나지 않고 넓은 창은 좌우가 더 보인다. 좋음.
- `/Users/iyeonsang/Desktop/game/demo-check/model-web/captures/sizes/retina-1280x720/shot_01_t2.30.png` — 레티나에서 흐리던 것을 물리 해상도로 그리게 고쳤다. `4x3-1024x768`, `21x9-2560x1080` 도 늘어남 없음. HUD 는 고정 24px 이라 넓은 창에서 작다. 쓸 만함.
- Godot 스크린샷은 이제 띠를 포함한 창 크기 그대로다. 레티나 화면의 실제 창 캡처(`screencapture`)와 띠의 행·열 수가 같았다.

### 세 번째 점검에서 확인하지 못한 것

- 소리를 귀로 듣지 않았다. 스피커로 나오는지, 음악이 듣기 좋은지, 겹쳐 섞은 이음매의 박자가 자연스러운지는 모른다(flat2d-web 은 박자 상관이 0.39 로 낮다).
- 반복 지점의 "딱" 소리는 파일로만 쟀다. 실행 중에는 끊김(무음)만 잰다.
- 키보드를 손으로 누르지 않았다. 보낸 키는 프로세스의 이벤트 큐에 직접 넣은 것이라 키보드 하드웨어와 창 포커스 판단을 거치지 않는다.
- 실제 게임패드, web 게임패드, web 의 OS 수준 마우스는 확인하지 않았다.
- 누가 실행 중에 Godot 창을 직접 활성화했다 떠나는 경우는 흉내 낸 알림으로만 확인했다(다시 누르고 오류로 남긴다).
- 두 번째 점검의 "점프 입력도 먹지 않았다"는 재현하지 못했다(풀림 39회 중 0회).
- 배율이 섞인 모니터에서 일반 모니터에 보이는 Godot 픽셀 아트(2배로 그린 뒤 줄여 보여 준다)는 스크린샷으로 판정할 수 없다.
