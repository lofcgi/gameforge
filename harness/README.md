# gameforge

혼자서 AI 로 게임을 만드는 Claude Code 플러그인이다. 기획부터 공개까지 여섯 단계로 나누고, 단계마다 결과물(이미지, 스크린샷, 점수)을 파일로 보여 준 뒤 사용자의 승인을 받아야 다음으로 넘어간다. 2D(픽셀 포함)와 3D, 엔진은 Godot 과 three.js/웹을 다룬다.

밑에는 Python CLI `gf`(생성, 후처리, Blender, 엔진 실행·스크린샷·플레이 봇, 레퍼런스, 블라인드 심사)가 있고, 그 위에 단계별 스킬, 서브에이전트, 차단 훅이 올라간다. 구조와 규약은 `AGENTS.md` 에 있다.

## 준비물

| 도구 | 쓰는 곳 | 이 컴퓨터 |
|---|---|---|
| Claude Code | 플러그인 실행 | 설치됨 |
| uv (Python 3.12+) | `gf` 실행 | 설치됨 |
| Godot 4 | Godot 엔진 게임 | 4.7.2 |
| Blender | 3D 정리, 턴테이블 | 5.3.0 |
| ffmpeg | 영상 프레임, 오디오 측정 | 설치됨 |
| node, bun | 웹 템플릿 의존성 | 설치됨 |
| Chrome | 웹 게임 실행·캡처 | 설치됨 |
| Claude in Chrome | Pinterest·ArtStation 등에서 레퍼런스 검색 (선택) | 사용자의 Chrome 에 연결돼 있어야 한다 |
| `FAL_KEY` | 이미지·영상·3D·오디오 생성 | 게임 폴더나 그 위 폴더의 `.env` |

`FAL_KEY` 는 사용자가 `.env` 에 직접 넣는다. 에이전트는 `.env` 를 읽지 않는다(훅이 막는다).

## 플러그인 불러오기

설치하지 않고 세션 하나에만 불러온다. 게임을 만들 폴더에서:

```sh
claude plugin validate /Users/iyeonsang/Desktop/game/harness     # 선택: 형식 검사
claude --plugin-dir /Users/iyeonsang/Desktop/game/harness
```

세션 안에서 `/gameforge:gf-start` 를 실행하거나 "게임 만들자"라고 말한다. 플러그인 파일을 고친 뒤에는 `/reload-plugins`, 불러온 구성은 `/plugin` 의 Installed·Errors 탭에서 본다. 플래그를 줄 수 없는 환경에서는 환경변수 `CLAUDE_CODE_PLUGIN_DIRS` 에 이 폴더의 절대 경로를 넣는다.

## 흐름

```
 plan ──────► look ──────────────► graybox ─────► assets ──────────────► polish ──────► publish
 gf-plan      gf-reference         gf-graybox     gf-assets-pixel        gf-polish      gf-publish
              gf-look                             gf-assets-2d
                                                  gf-assets-3d
                                                  gf-ui · gf-audio
 한 문장 훅    레퍼런스 고르기       도형만으로      스타일별 에셋          손맛·가독성     빌드
 설계 요약     기준 화면 1장         핵심 루프       UI 텍스처              첫 1분·성능     플레이 링크
 범위 점검     아트 디렉션           사람이 재미     소리(재고, 사람이 듣기)  (가장 오래 걸림) 공개 글
                                    판정
    │            │                    │              │                      │              │
    └── 단계마다: 결과물을 보여 준다 → 사용자가 승인 → gf state approve ──────┴──────────────┘

 모든 단계에서 gf-verify:  자가 실행(동작) · 블라인드 심사(화면) · 사람 플레이(감각)
```

- 시작과 이어 가기: `gf-start` (환경 점검, 엔진·차원·스타일 선택, 프로젝트 생성, 지금 단계 안내).
- 서브에이전트: `blind-judge`(섞인 두 화면만 보고 판정), `playtest-reviewer`(봇·캡처 기록을 플레이어 눈으로 검토).
- 특정 기존 게임을 재현하지 않는다. 여러 출처에서 특성만 가져온다.

## 결과물이 생기는 곳

모두 게임 폴더 안이다. 에이전트가 절대 경로를 알려 주면 Orca/Paseo 나 Finder 에서 연다.

| 경로 | 내용 |
|---|---|
| `design/brief.md`, `design/art-direction.md`, `design/look/` | 설계 요약, 아트 디렉션, 기준 화면 |
| `references/inbox/`, `references/picked/` | 모은 레퍼런스, 고른 것, 모음판, 측정값 |
| `assets/raw/`, `assets/game/` | 생성 원본, 후처리가 끝난 게임용 에셋 |
| `captures/` | 스크린샷, 봇·재생 결과, 심사 쌍(`captures/judge/`), 플레이 기록(`captures/sessions/`) |
| `.gf/state.json`, `.gf/ledger.jsonl` | 단계·승인 기록, 생성 비용 기록 |

## 브라우저로 레퍼런스 모으기

Pinterest, ArtStation 처럼 자동 수집을 막는 사이트는 에이전트가 Claude in Chrome 도구로 사용자의 Chrome 에서 직접 검색한다(`gf-reference` 스킬).

1. 에이전트가 원하는 느낌을 묻고 검색어(한국어·영어)를 제안한다.
2. 새 탭에서 검색 결과를 읽기만 한다. 저장·팔로우·좋아요는 하지 않는다. 로그인이 필요하면 멈추고 사용자가 직접 로그인한다.
3. 검색어마다 8~12장을 `gf ref add <이미지 주소> --source-url <페이지 주소> --note ... --tags ...` 로 가져온다.
4. `gf ref sheet` 가 만든 번호 모음판에서 사용자가 고른다.

Chrome 도구가 없으면 이미지 파일을 내려받아 `gf ref add <파일>` 로 넣는다.

## 비용

- 코딩 에이전트 사용량과 별도로, 생성 호출이 fal 계정에서 과금된다. 2026-11-22 실측: 이미지 1장 $0.08, 스프라이트 영상 3초 약 $0.34, 룩 영상 4초 약 $0.9, 3D 모델 1개 약 $0.5, 리깅 1회 $0.8, 효과음 초당 $0.002, 음악 분당 $0.6.
- 일부 모델은 단가 단위(tokens, credits, compute seconds) 때문에 비용을 미리 계산할 수 없다. 그런 호출은 `--estimate-usd <대략의 값>`(한도와 비교)이나 `--allow-unknown-cost`(한도 확인 없이) 를 명시해야 실행된다. 보통 `--estimate-usd` 와 `--max-usd` 를 함께 건다. 호출당 기본 한도는 $3 이다(`.gf/config.toml` 의 `[budget]`).
- 모든 호출은 `.gf/ledger.jsonl` 에 남고, 누적은 `gf state show` 의 `spent_usd` 에 나온다.

## 훅이 막는 것

`.gf` 폴더가 있는 게임 프로젝트에서만 동작한다.

- 근거 없는 단계 승인: 마지막 변경 뒤의 통과한 스모크 테스트(`gf engine test` 가 `captures/test/result.json` 에 남긴다)와 스크린샷이 없으면 `gf state approve` 가 막힌다. 에셋 단계부터는 없는·빈 에셋 참조와 (픽셀 프로젝트의) 후처리 안 된 그림, 폴리시부터는 없는·무음 오디오도 본다.
- `.env` 읽기·출력.
- 승인·심사·비용 기록(`.gf/state.json`, `.gf/judge/`, `.gf/ledger.jsonl`)과 브리지 파일, 스모크 테스트 기록을 손으로 고치거나 지우는 것.
- 블라인드 심사자가 심사 폴더 밖의 파일을 읽는 것.

## 알려진 한계

- **통합 점검(2026-11-22)**: 픽셀 2D(Godot, 웹), 비픽셀 2D(Godot, 웹), 생성 모델 3D(Godot, three.js)를 실제 생성물로 끝까지 돌렸다. 결과와 약한 곳은 게임 폴더 옆 `demo-check/EVIDENCE.md` 에 있다. 소리는 길이·음량·재생 호출만 확인했고 사람이 듣지 않았다.
- **2D 의 대기 자세는 걷기 시트의 첫 프레임이다.** 영상 모델이 걷기 시작하며 자세를 바꾸기 때문에 정지 스프라이트와 섞으면 튄다. 따로 대기 동작이 필요하면 영상을 한 번 더 만든다.
- Godot 자동 실행 중 눌러 둔 키가 도중에 풀린 적이 있다(창 포커스 상실로 추정, 원인 미확인). 브리지가 풀린 키를 다시 누르고 경고(`GfBridge: 눌러 둔 키 ...`)를 남긴다. 이 경고가 보이면 그 실행의 타이밍은 한 틱쯤 어긋났을 수 있으니 다시 돌린다.
- **3D 인물 애니메이션이 약하다.** 가까이서 보는 인물, 정밀한 동작은 여러 번 다시 만들어도 어색할 수 있다. 원거리 카메라, 탈것·로봇·생물, 2D 를 권한다.
- **AAA 급 범위의 근거가 없다.** 이 방법이 검증된 것은 작은 레벨, 짧은 한 판, 스타일이 뚜렷한 게임이다.
- 브라우저로 레퍼런스를 읽는 절차는 사이트의 화면 구조에 기댄다. 사이트가 바뀌어 후보가 읽히지 않으면 이미지 파일을 내려받아 `gf ref add <파일>` 로 넣는다.
- 빌드·내보내기 명령이 `gf` 에 없다. 공개 단계의 빌드는 엔진의 방법을 직접 쓰고, 빌드 결과는 사람이 열어 확인해야 한다.
- 재미, 조작감, 소리의 느낌은 사람만 판정할 수 있다. 에이전트는 실행하고, 찍고, 재고, 묻는다.

## 개발

```sh
uv run --project tools pytest -q tools/tests
uv run --project tools ruff check tools
```
