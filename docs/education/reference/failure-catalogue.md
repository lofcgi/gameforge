# 실패 사례 목록

> 문서 유형: 참조

gameforge와 cat-angler를 만들면서 실제로 겪은 결함을 증상, 원인, 고친 방법, 저장소 위치로 정리했어요. 비슷한 증상을 만났을 때 찾아보거나, 에이전트에게 일을 맡기기 전에 "무엇이 잘못될 수 있는지" 훑어볼 때 쓰세요.

## 읽는 법

- **근거** 열이 저장소 경로이면 그 파일에서 내용을 확인할 수 있어요.
- **근거** 열이 "세션 기록"이면 작업 세션의 기록으로만 전해지는 내용이에요. 고친 뒤의 코드나 문서는 저장소에 있지만, 고치기 전의 증상을 적은 파일은 없어요.
- 대부분의 사례는 합성 입력으로 만든 테스트는 통과했고 **진짜 입력으로 실제 실행했을 때** 드러났어요.

## 픽셀과 2D 에셋

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 격자 자동 감지가 생성 이미지에서 실패한다 | 모델의 "픽셀 아트"는 512픽셀에 100칸, 칸 하나가 5.12픽셀이다. 정수 격자가 아니다 | 격자를 추측하지 않고 목표 크기를 직접 준다: `gf post pixel-snap --trim --height <픽셀>`. 자동 감지는 신뢰도 0.25 미만이면 실패로 끝낸다 | `harness/tools/gf/post/pixel.py`, `harness/skills/gf-assets-pixel/SKILL.md` | 저장소 |
| "32x32"를 요청했는데 크기가 제각각이다 | 모델은 요청한 픽셀 크기를 지키지 않는다(100×100칸으로 나왔다) | 대상만 잘라 세로를 맞춘다(`--trim --height`) | `harness/skills/gf-assets-pixel/SKILL.md` | 저장소 |
| 팔레트를 뽑았더니 눈의 흰자가 사라졌다 | 면적이 작은 색이 팔레트에서 밀려났다 | 팔레트 추출 방법을 바꿨다. 지금은 넓게 퍼진 색 무리부터 나누는 가중 k-means다 | `harness/tools/gf/post/palette.py` | 세션 기록 (현재 방법은 저장소) |
| 영상 프레임의 외곽선에 배경색(초록)이 남는다 | 영상 압축 때문에 배경색이 가장자리로 번진다. 정지 그림용 기본값으로는 지워지지 않는다 | 영상 프레임에는 `gf post chroma --despill 5 --erode 2`를 쓴다 | `harness/skills/gf-assets-pixel/animation.md`, `harness/skills/gf-assets-2d/SKILL.md` | 저장소 |
| 24픽셀로 줄인 캐릭터가 얼룩이 된다 | 원본에 주름, 패널, 명암 줄이 많다 | 큰 색면과 음영 한 단계로 다시 생성한다 | `demo-check/EVIDENCE.md` E절 (`pixel-web`의 우주인) | 저장소 |
| 가시덤불의 붉은 가시가 전부 갈색으로 뭉쳤다 | 가는 형태는 1배에서 살아남지 못한다 | 굵은 결정 모양으로 다시 생성했다 | `demo-check/EVIDENCE.md` A절 | 저장소 |
| 멈춰 있어도 걷는 것처럼 보인다 | 영상 모델이 걷기 시작하며 자세를 바꿔서, 정지 그림을 대기 자세로 쓸 수 없다. 걷기 첫 프레임을 대기 자세로 쓴다 | 고치지 못했다. 대기 동작이 필요하면 영상을 한 번 더 만든다 | `harness/README.md` "알려진 한계", `demo-check/EVIDENCE.md` D절 | 저장소 |
| 비픽셀 스타일 프로젝트의 화면이 픽셀 설정으로 나온다 | 템플릿에 픽셀 아트용 화면 설정만 들어 있었다 | `gf init --style 2d`가 템플릿을 복사한 뒤 고해상도 2D용 설정으로 고친다 | `harness/templates/README.md` 8절, `harness/tools/gf/core/render_profile.py` | 세션 기록 (현재 동작은 저장소) |
| 웹 템플릿이 하네스가 만든 스프라이트 시트를 읽지 못하고 소리를 낼 길이 없다 | 템플릿과 `gf post sheet`를 따로 만들었고 함께 돌려 본 적이 없었다 | 웹 템플릿이 시트의 매니페스트를 읽게 하고 소리 경로를 넣었다 | `harness/templates/web-2d/`, `demo-check/EVIDENCE.md` E~G절 | 세션 기록 (점검 결과는 저장소) |
| 웹 픽셀 게임의 HUD 글자가 뭉개진다 | 8픽셀 글자를 캔버스에 그렸다 | HUD 글자를 DOM으로 옮겼다 | `demo-check/EVIDENCE.md` E절 | 저장소 |

## 3D 에셋

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 삼각형 수를 줄였더니 모델에 구멍이 난다 | 생성 모델의 면들이 서로 떨어져 있다 | 줄이기 전에 겹친 정점을 먼저 합친다 | `harness/tools/gf/blender/scripts/decimate.py`("면들이 떨어진 채로 줄이면 구멍이 난다") | 저장소 |
| 캐릭터가 옆을 보고 걷는다 | 생성 모델은 정면이 +X로 나온다. 모듈마다 "앞"의 기준이 달랐다 | 규약을 한 곳에만 적었다: GLB의 정면은 +Z. `gf blender rescale --turn -90`으로 맞춘다. 턴테이블 0번 그림에 얼굴이 보이면 맞다 | `harness/templates/README.md` 7절 | 저장소 (모듈마다 달랐다는 것은 세션 기록) |
| three.js에서 그림자가 캐릭터에서 떨어져 떠 보인다 | (원인 기록 없음) | 고쳤다고만 적혀 있다 | `demo-check/EVIDENCE.md` B절 | 저장소 |
| Blender 명령이 실행되지 않는다 | 호출 코드는 있었지만 Blender 앱이 설치돼 있지 않았다 | 설치했다. 지금은 `gf doctor`가 Blender 유무를 보여 주고, 없으면 오류 문장이 설치 명령을 알려 준다 | `harness/tools/gf/blender/runner.py`, `harness/tools/gf/core/commands.py` | 세션 기록 (현재 오류 문장은 저장소) |

## 생성 호출과 비용

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 작업 도중 생성 호출이 실패하고 원시 traceback이 나온다 | fal 잔액이 바닥났다(두 번). 오류를 감싸지 않았다 | 오류를 `{"ok": false, "error": ...}` 형식으로 감쌌다. 사용자가 두 번 충전했다 | `.claude/handoffs/2026-11-23-gameforge-cat-angler.md`의 "비용" | 잔액은 저장소, traceback은 세션 기록 |
| 단가를 계산할 수 없는 호출이 한도 검사를 통과한다 | 한도 검사가 비용을 추정할 수 없는 호출을 막지 않았다 | `--estimate-usd`나 `--allow-unknown-cost`를 명시해야만 호출된다 | `harness/tools/gf/core/fal.py`, `harness/AGENTS.md` | 세션 기록 (현재 동작은 저장소) |
| `gf gen image --ref`가 실패한다 | 기본 `image.concept` 모델은 참조 이미지를 받지 않는다 | 조용히 다른 모델로 바꾸지 않고, 오류가 `gf gen edit --image`를 쓰라고 알려 준다 | `harness/AGENTS.md` "fal 호출 규칙" | 저장소 |
| 단가 API가 연속 호출에 429를 낸다 | 플랫폼 API의 호출 제한 | 지수 백오프로 다시 시도한다 | `harness/AGENTS.md` "fal 호출 규칙" | 저장소 |

## 엔진 실행과 입력

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| Godot 자동 실행 중에 눌러 둔 키가 저절로 풀린다 | 앱이 포커스를 잃으면 Godot이 눌린 키와 액션을 전부 뗀다. 터미널에서 띄운 Godot은 시작 직후 포커스를 내줬다 되찾는다 | 브리지가 풀린 키를 다시 누르고 기록을 남긴다. 같은 45회 반복에서 고치기 전 39회 발생, 고친 뒤 0회 | `demo-check/EVIDENCE.md` H절 "Godot 키 풀림" | 저장소 |
| Godot 재생에서 점프가 매번 한 틱 늦다 | (원인 기록 없음) | 고쳤다. 위치 차이 최대 3.56 → 0 | `demo-check/EVIDENCE.md` H절 | 저장소 |
| 웹에서 한 틱보다 짧게 친 키가 사라진다 | (원인 기록 없음) | 고쳤다 | `demo-check/EVIDENCE.md` H절 | 저장소 |
| 레티나 화면에서 웹 3D가 흐리다 | 물리 해상도로 그리지 않았다 | 물리 해상도로 그리게 고쳤다 | `demo-check/EVIDENCE.md` H절 "화면 크기" | 저장소 |
| 게임 객체의 난수가 실행마다 다르다 | `main.gd`의 멤버 초기화는 브리지가 시드를 정하기 전에 실행된다 | 게임 객체를 `_ready`에서 만든다. 템플릿 문서에는 아직 적지 않았다 | `.claude/handoffs/2026-11-23-gameforge-cat-angler.md` "알려진 한계" | 저장소 |
| 저장 파일이 있으면 기록 재생이 어긋난다 | 남은 저장 파일이 타이틀 메뉴의 처음 커서를 바꾼다 | 자동 실행에서는 저장을 끈다. 재생할 기록은 `CA_SAVE=off`로 남긴다 | `games/cat-angler/design/play-guide.md` | 저장소 |

## 소리

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 음악이 반복될 때마다 끊긴다 | 생성한 음악의 앞뒤에 무음이 있다(네 곡 모두 11~25ms). 고치기 전 실행 중 끊김은 Chrome 19.2ms, Godot 9.5ms | `gf post audio-loop`로 무음을 자르고 꼬리를 머리에 섞는다. 고친 뒤 0.1ms, 0.0ms | `demo-check/EVIDENCE.md` H절 "소리", `harness/tools/gf/post/audio_loop.py` | 저장소 |
| 컷신 음악의 이음매에서 박자가 밀린다 | 반복 길이가 박의 정수배가 아니다(35.66박, 80.38박) | 박의 정수배로 다시 잘랐다 | `games/cat-angler/design/asset-status.md` "소리" | 저장소 |
| 효과음이 음악에 묻힌다 | 순간 피크 뒤의 몸통이 25 dB 작았다 | 그 효과음을 다시 생성했다 | `games/cat-angler/design/asset-status.md` "소리" | 저장소 |
| 실행 중 전체 신호가 넘친다 | 피크가 +1.7 dB였다 | 음량을 맞춰 −3.5 dB로 내렸다 | `games/cat-angler/design/asset-status.md` | 저장소 |
| 소리가 "된다"고 했지만 아무도 듣지 않았다 | 에이전트는 듣지 못한다 | 고칠 수 없다. 측정하고 "듣지 않았다"고 적는다 | `harness/README.md`, `games/cat-angler/SCREENSHOTS.md` | 저장소 |

## 플러그인과 에이전트

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 평범한 말로 요청하면 스킬이 발동하지 않는다(13개 중 12개) | 스킬 설명이 "무엇을 하는지"만 말하고 "어떤 요청에 쓰는지"를 말하지 않았다 | 설명을 "…를 해 달라는 요청에는 … 전에 먼저 이 스킬을 쓴다" 형태로 다시 썼다. 실제 세션에서 다시 확인한 것은 3개다 | `harness/skills/*/SKILL.md`의 `description`, `.claude/handoffs/2026-11-23-gameforge-cat-angler.md` | 12개는 세션 기록, 3개는 저장소 |
| 각자 테스트를 통과한 모듈이 함께 돌지 않는다 | 모듈 사이의 규약(방향, 비용, 경로)이 서로 달랐다 | 통합 점검에서 틈 일곱 개를 고쳤다 | `demo-check/EVIDENCE.md` | 개수는 세션 기록 |
| 만들고 브라우저 시험까지 한 기능을 걷어 냈다 | 레퍼런스 수집용 Chrome 확장과 수신 서버(결함 여섯 개를 고쳤다)를 사용자가 원하지 않았다. 사용자의 로그인된 Chrome을 에이전트가 직접 쓰는 방식을 골랐다 | 기능을 없애고 `gf ref add --source-url` 방식으로 바꿨다. git이 없던 때라 지운 파일은 휴지통으로 옮겼다 | `demo-check/EVIDENCE.md`("2026-11-23 제거"), `harness/skills/gf-reference/SKILL.md` | 제거는 저장소, 결함 수는 세션 기록 |

## 기획과 소통

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| 사용자가 설계를 "너무 단순하다"며 반려했다 | 에이전트가 범위를 줄이라는 지침을 "작을수록 안전하다"로 읽고 모든 것을 고정된 한 화면에 넣었다 | 이어진 긴 바다로 다시 설계했다. "설계를 단순하게 줄이지 말 것"을 인계 기록에 남겼다 | `games/cat-angler/design/brief.md`, `.claude/handoffs/2026-11-23-gameforge-cat-angler.md` | 저장소 |
| 사용자가 그레이박스를 63초 만에 그만두고 강하게 반려했다 | 색 덩어리 빌드가 이 사용자에게는 소통 도구로 작동하지 않았다. 승인한 기준 화면과 전혀 달라 보였다 | 실제 품질의 화면으로 전면 재제작했다 | `.claude/handoffs/2026-11-23-gameforge-cat-angler.md` "갱신" | 저장소 |
| 봇은 엔딩까지 깼는데 사람은 하지 않았다 | 봇의 완주는 "막히는 곳이 없다"만 증명한다 | 고칠 대상이 아니다. 사람 플레이를 대신할 수 없다는 사실이다 | `.claude/handoffs/2026-11-23-gameforge-cat-angler.md` | 저장소 |
| 블라인드 심사에서 게임 화면이 기준 화면에 진다 | 고양이와 배가 작고, 물고기가 작고 옅고, 물속이 단조롭다 | 다듬는 중이다(2026-11-23) | `games/cat-angler/.gf/judge/history.jsonl`, `games/cat-angler/design/asset-status.md` | 저장소 |

## 조사

| 증상 | 원인 | 고친 방법 | 저장소 위치 | 근거 |
|---|---|---|---|---|
| Reddit과 X의 글이 읽히지 않는다 | 평범한 방법의 자동 수집을 막는다 | 공개 API, 영상 자막, 사용자의 로그인된 브라우저를 차례로 시도했다. 끝까지 못 읽은 것은 보고서에 "확인하지 못한 것"으로 적고 링크를 지어내지 않았다 | `reports/AI 풀제작 고퀄 1인 게임 방법론 2.md`의 "확인하지 못한 것", `research_notes/` 07~14번 | 저장소 (시도 순서는 세션 기록) |

## 더 보기

- 이 사례들이 주는 교훈: [에이전트 작업 분할 원칙](../explanations/splitting-work.md), [세 가지 검증의 역할](../explanations/three-checks.md)
- 반려 두 번의 전후 사정: [cat-angler 제작 과정](../explanations/cat-angler-case-study.md)
- 원문: `demo-check/EVIDENCE.md`
