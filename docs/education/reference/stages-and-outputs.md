# 단계별 스킬과 산출물

> 문서 유형: 참조

gameforge의 여섯 단계마다 어떤 스킬이 쓰이고 어떤 파일이 생기는지 정리했어요. "지금 단계에서 무엇이 나와야 하는가"와 "이 파일은 어느 단계에서 만들어지는가"를 찾을 때 쓰세요. 스킬 13개와 서브에이전트 2개의 원문은 `harness/skills/`와 `harness/agents/`에 있어요.

## 단계 순서

```
plan → look → graybox → assets → polish → publish
```

현재 단계는 `gf state show`로 확인하고, 사용자가 승인한 뒤 `gf state approve`로 넘어가요. 승인 전에 `gf check evidence`가 근거를 검사해요.

## 단계별 표

| 단계 | 스킬 | 하는 일 | 생기는 파일 (게임 폴더 기준) |
|---|---|---|---|
| (시작) | `gf-start` | 환경 점검, 엔진·차원·스타일 선택, 프로젝트 생성, 지금 단계 안내 | `.gf/state.json`, `.gf/config.toml`, 템플릿 파일 전체 |
| `plan` | `gf-plan` | 한 문장 훅, 설계 요약, 범위 점검 | `design/brief.md` |
| `look` (앞) | `gf-reference` | 레퍼런스 수집, 모음판, 사용자 선택, 측정, 글로 정리 | `references/inbox/`, `references/sheets/`, `references/picked/`, `references/picked/traits.json`, `traits-palette.png`, `analysis.md` |
| `look` (뒤) | `gf-look` | 기준 화면 후보 생성, 사용자 선택, 팔레트, 아트 디렉션 | `design/look/`(후보와 기준 화면), `design/palette.json`, `design/art-direction.md` |
| `graybox` | `gf-graybox` | 도형만으로 핵심 반복 구현, 자가 실행, 사람이 재미 판정 | 게임 코드, `bot/clear.json`, `captures/` |
| `assets` | `gf-assets-pixel` | 픽셀 스타일: 생성 → 크로마 → 격자 맞춤 → 팔레트 → 검사 | `assets/raw/`, `assets/game/`, `captures/inspect/` |
| `assets` | `gf-assets-2d` | 비픽셀 2D 스타일: 기준 화면을 참조로 생성 → 배경 제거 → 줄이기 | `assets/raw/`, `assets/game/` |
| `assets` | `gf-assets-3d` | 3D 스타일: 코드로 그리거나, 컨셉 이미지 → 3D 모델 → Blender 정리 | `assets/raw/`, `assets/game/`, `captures/turntable/` |
| `assets` | `gf-ui` | 기준 화면의 룩으로 패널·버튼·아이콘 텍스처를 생성해 입히기 | `assets/game/` 아래 UI 텍스처 |
| `assets`, `polish` | `gf-audio` | 효과음·음성·음악 생성, 측정, 사람에게 들려 묻기 | `assets/raw/audio/`, `assets/game/audio/`, `captures/audio/result.json` |
| `polish` | `gf-polish` | 손맛, 가독성, 첫 1분, 성능을 작은 변경 하나씩 고치기 | `design/polish-list.md`, `design/playtest-notes.md`, `captures/perf/` |
| `publish` | `gf-publish` | 빌드, 플레이 링크 점검, 공개 글 초안 | `build/`, `design/publish-post.md` |
| (모든 단계) | `gf-verify` | 자가 실행, 블라인드 심사, 사람 플레이, 단계 승인 절차 | `captures/test/result.json`, `captures/judge/<id>/`, `.gf/judge/`, `captures/sessions/` |

cat-angler는 기준 화면을 `design/look/target.png`에, 팔레트를 `design/look/palette.json`에 뒀어요. 스킬 문서의 예시 경로(`design/look/frame.png`, `design/palette.json`)와 달라요.

## 스킬과 함께 있는 보조 문서

스킬 폴더에는 `SKILL.md` 외에 세부 절차 문서가 있어요.

| 스킬 | 보조 문서 | 내용 |
|---|---|---|
| `gf-start` | `conventions.md` | 결과 보여 주기, 승인, 비용, 금지 사항의 공통 규약 |
| `gf-plan` | `brief-template.md` | 설계 요약의 틀 |
| `gf-reference` | `browser-collect.md` | 사용자의 Chrome에서 레퍼런스를 읽는 절차 |
| `gf-look` | `art-direction-template.md` | 아트 디렉션의 틀 |
| `gf-graybox` | `bridge-rules.md` | 브리지 계약의 요점 |
| `gf-assets-pixel` | `animation.md` | 픽셀 애니메이션 절차 |
| `gf-assets-3d` | `blender-build.md` | Blender 스크립트로 모델 만들기 |
| `gf-polish` | `feel-checklist.md` | 손맛 점검표 |
| `gf-publish` | `build.md`, `posting.md` | 빌드 절차, 공개 글 틀 |
| `gf-verify` | `blind-judging.md` | 블라인드 심사 절차와 해석 |

## 서브에이전트

| 이름 | 읽는 것 | 돌려주는 것 | 쓸 수 있는 도구 |
|---|---|---|---|
| `blind-judge` | 심사 폴더의 `rubric.md`, `X.png`, `Y.png`, (있으면) `target.png`만 | 승자, 항목별 점수, 이유가 든 JSON 하나 | Read |
| `playtest-reviewer` | 봇·캡처·재생이 남긴 결과 폴더, 설계 요약 | 플레이어 입장에서 본 문제 목록과 근거. 코드를 고치지 않아요 | Read, Glob, Grep |

## 단계 승인에 필요한 근거

훅이 `gf state approve`를 막을 때 보는 것이에요(`harness/README.md`).

| 단계 | 필요한 근거 |
|---|---|
| `plan` | 내용이 있는 `design/brief.md` |
| `graybox` 이후 | 마지막 변경 뒤에 통과한 스모크 테스트(`captures/test/result.json`)와 스크린샷 |
| `assets` 이후 | 위에 더해, 없는 에셋이나 빈 에셋을 가리키는 참조가 없을 것. 픽셀 프로젝트는 후처리 안 된 그림이 없을 것 |
| `polish` 이후 | 위에 더해, 없는 소리나 무음인 소리가 없을 것 |

`look` 단계의 근거 조건은 이 표에 없어요. 저장소 문서에서 명시된 문장을 찾지 못했어요. `gf check evidence`를 실행하면 그 단계에서 모자란 것을 알려 줘요.

## 더 보기

- 단계를 나눈 이유: [gameforge 하네스의 구조](../explanations/harness-structure.md)
- 명령 목록: [`gf` 명령 모음](gf-commands.md)
- 원문: `harness/skills/gf-start/SKILL.md`의 단계 표, `harness/AGENTS.md`
