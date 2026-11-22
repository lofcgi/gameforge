---
name: gf-start
description: gameforge 로 게임 만들기를 시작하거나 이어 간다. 사용자가 "게임 만들자", "새 게임 프로젝트", "gameforge 시작", "하던 게임 이어서"라고 하거나, .gf 폴더가 있는 게임 프로젝트에서 지금 무엇을 할 차례인지 물을 때 쓴다. 환경 점검, 엔진·차원·스타일 선택, 프로젝트 생성, 단계 안내를 한다.
argument-hint: "[게임 폴더 경로]"
---

# gameforge 시작 / 이어 가기

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`. 셸 변수는 호출 사이에 남지 않으니 매번 전체를 쓴다.
공통 규약(결과 보여 주기, 승인, 비용, 금지 사항)은 `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` 에 있다. 지금 읽는다.

## 1. 이어 가기인지 먼저 본다

게임 폴더(인자, 없으면 현재 폴더)에 `.gf/state.json` 이 있으면 새로 만들지 않는다.

```sh
$GF state show
```

`state.stage` 와 `approvals`, `spent_usd` 를 사용자에게 한 줄로 알려 주고 아래 표의 스킬로 넘어간다. `.claude/handoffs/` 에 인계 기록이 있으면 그것도 읽는다.

| stage | 할 일 | 스킬 |
|---|---|---|
| `plan` | 한 문장 훅, 설계 요약, 범위 점검 | `gf-plan` |
| `look` | 레퍼런스 수집·선택 → 기준 화면 → 아트 디렉션 | `gf-reference` → `gf-look` |
| `graybox` | 도형만으로 핵심 루프, 사람이 재미 판정 | `gf-graybox` |
| `assets` | 스타일별 에셋, UI, 오디오 | `gf-assets-pixel` / `gf-assets-2d` / `gf-assets-3d`, `gf-ui`, `gf-audio` |
| `polish` | 손맛, 가독성, 첫 1분, 성능 | `gf-polish` |
| `publish` | 빌드, 플레이 링크, 공개 글 | `gf-publish` |

검증(`gf-verify`)은 graybox 부터 모든 단계에서 쓴다.

## 2. 새 프로젝트: 환경 점검

```sh
$GF doctor
```

`missing` 이 비어 있고 `fal_key` 가 true 여야 한다. 빠진 도구는 무엇이 안 되는지와 함께 알린다: `godot` 없음 → Godot 엔진 불가, `blender` 없음 → 3D 정리·미리보기 불가, `ffmpeg` 없음 → 영상 프레임·오디오 측정 불가, `bun` 없음 → web-3d 의존성 설치 불가, `chrome` false → 웹 엔진 실행 불가, `fal_key` false → 생성 전부 불가(사용자가 게임 폴더나 그 위의 `.env` 에 `FAL_KEY` 를 넣는다. 에이전트는 `.env` 를 열지 않는다).

## 3. 세 가지를 정한다

사용자에게 만들고 싶은 게임을 한두 문장으로 듣고, 아래를 **추천과 이유를 붙여** 한 번에 묻는다. 사용자가 이미 정했으면 묻지 않는다.

| 고를 것 | 값 | 추천 기준 |
|---|---|---|
| 엔진 | `web` / `godot` | 링크 하나로 바로 플레이시키고 싶다, 3D 를 코드로 그린다 → `web` (three.js, 빌드 단계 없음). 2D 픽셀·물리·씬 편집, 데스크톱 배포 → `godot`. 둘 다 에이전트가 직접 실행하고 화면을 찍을 수 있다. |
| 차원 | `2d` / `3d` | 처음이거나 인물이 주인공이면 `2d`. 풍경·탈것·추상·기계가 중심이면 `3d` 도 좋다. |
| 스타일 | `pixel` / `2d` / `3d-code` / `3d-gen` | `pixel`: 저해상도 픽셀 아트(후처리로 진짜 1x 픽셀로 만든다). `2d`: 고해상도 일러스트풍. `3d-code`: 셰이더·절차 생성·Blender 스크립트로 만든다(인물 없음에 강함). `3d-gen`: 컨셉 그림 → 3D 모델 생성(카메라가 멀 때 좋다). |

추천할 때 이 약점을 숨기지 않는다. 사용자가 그래도 원하면 그대로 하되 이유를 말해 둔다.

- **가까이서 보는 3D 인물 애니메이션**은 지금 가장 약한 고리다. 생성 모델은 가까이서 보면 어색하고 걷기 하나에 여러 번 반려가 난다. 카메라를 멀리 두거나, 인물 대신 탈것·로봇·생물로 바꾸거나, 2D 로 가는 쪽이 결과가 좋다.
- **넓은 월드**는 빈 공간이 되기 쉽다. 작은 레벨 하나를 끝까지 다듬는 쪽이 낫다.
- 잘 되는 쪽: 분위기·속도감·아름다움이 중심인 게임, 원거리·고정 카메라, 스타일이 뚜렷한 그림.

## 4. 만든다

```sh
$GF init --engine <web|godot> --dim <2d|3d> --style <pixel|2d|3d-code|3d-gen> --name "<작업용 이름>"
$GF engine test
$GF engine capture --out captures/template --at 1
```

- `init` 은 템플릿(도형만 있는 작은 그레이박스)을 게임 폴더에 복사하고 `.gf/` 를 만든다. 이미 `.gf` 가 있으면 실패한다.
- 2D 는 스타일에 따라 화면 설정이 달라진다(결과의 `render`). `pixel`: 320x180 을 nearest 로 정수배 확대, 그림은 단위당 1픽셀. `2d`: 같은 320x180 레벨 단위를 창 해상도로 부드럽게 그리고 그림은 단위당 4픽셀. 스타일을 나중에 바꾸면 게임 폴더 `AGENTS.md` 의 표대로 설정을 직접 고쳐야 한다.
- `engine test` 는 스모크 테스트를 돌리고 결과를 `captures/test/result.json` 에 남긴다. 다섯 항목(boot, contract, first_frame, input_liveness, no_errors)이 모두 `ok` 여야 한다.
- 찍힌 스크린샷을 Read 로 보고 절대 경로를 사용자에게 준다. 게임 폴더의 `AGENTS.md`(템플릿이 넣어 둔 규칙)를 읽어 둔다.

## 5. 흐름을 설명하고 넘긴다

사용자에게 여섯 단계를 한 줄씩 설명하고(위 표), 단계마다 결과물을 보여 주고 승인을 받아야 다음으로 간다는 것, 가장 많은 시간이 폴리시에 든다는 것을 말한다. 그다음 `gf-plan` 으로 넘어간다.
