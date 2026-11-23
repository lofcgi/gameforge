# 인계: gameforge 하네스와 cat-angler 게임 (2026-11-23)

다른 컴퓨터에서 이어서 작업하기 위한 기록이다. 새 세션은 이 파일과 `AGENTS.md`, `harness/AGENTS.md`, `games/cat-angler/design/brief.md` 를 먼저 읽는다.

## 지금 어디까지 왔나

| 영역 | 상태 |
|---|---|
| 조사 | 끝남. 최종본 `reports/AI 풀제작 고퀄 1인 게임 방법론 2.md` |
| 하네스 `harness/` | 완성, 테스트 279개 통과, `claude plugin validate` 통과 |
| 데모 6종 `demo-check/` | 엔진 2종 × 스타일 조합을 실제 생성 에셋으로 끝까지 확인 |
| 게임 `games/cat-angler/` | 단계 `graybox`. 도형만으로 처음부터 엔딩까지 플레이 가능. 사용자의 플레이 평가를 기다리는 중 |

## 새 컴퓨터에서 준비할 것

1. 도구 설치 (macOS 기준): `brew install uv ffmpeg node bun gh`, `brew install --cask godot blender`. 확인한 버전은 Godot 4.7.2, Blender 5.3.0, ffmpeg 8.1.
2. `cp .env.example .env` 후 `FAL_KEY` 를 넣는다. 키는 저장소에 없다.
3. `cd harness/tools && uv sync`
4. 점검: `uv run -q --project harness/tools gf doctor` 와 `cd harness/tools && uv run pytest -q`
5. 웹 3D 데모를 돌리려면 그 프로젝트에서 `bun install` (어댑터가 첫 실행 때 자동으로 한다).
6. 레퍼런스 이미지는 저작권 때문에 저장소에 없다. 출처가 든 메타(`references/inbox/*.json`)만 있다. 필요하면 메타의 `image_url` 또는 `source_url` 로 `gf ref add` 를 다시 돌린다. 고른 결과의 요약은 `games/cat-angler/references/picked/analysis.md` 와 `traits.json` 에 남아 있어 다시 받지 않아도 작업은 이어진다.

## 하네스 쓰는 법

```sh
cd <게임 폴더>
claude --plugin-dir /경로/harness
# 세션 안에서 /gameforge:gf-start
```

- 단계: `plan → look → graybox → assets → polish → publish`. `gf state approve` 는 사용자 승인 뒤에만 한다. 훅이 근거 없는 승인을 막는다.
- 명령은 zsh 에서 변수 대신 함수로 줄인다: `gf() { uv run -q --project <harness>/tools gf --project . "$@"; }`
- 생성 모델은 역할 이름으로 부르고 실제 fal 모델 ID는 `harness/tools/gf/core/defaults.toml` 에 있다. 비용을 추정할 수 없는 모델(Tripo, Seedance, 배경 제거)은 `--estimate-usd` 나 `--allow-unknown-cost` 가 있어야 호출된다.
- 레퍼런스 수집은 Chrome 확장 방식을 없애고 Claude in Chrome 도구로 직접 검색해 `gf ref add --source-url` 로 넣는 방식이다(`harness/skills/gf-reference/`). Pinterest 는 그 Chrome 에 로그인돼 있어야 한다. Reddit 은 Claude in Chrome 이 막는다.

## cat-angler: 정해진 것

별주부전을 모티브로 한 2D 픽셀 낚시 성장 게임. 주인공은 고양이.

- 설계: `games/cat-angler/design/brief.md` (닫힌 결정 표가 있다)
- 화풍: `design/art-direction.md`, 기준 화면 `design/look/target.png`, 팔레트 `design/look/palette.json` (24색)
- 레퍼런스 읽기: `references/picked/analysis.md`
- 핵심 결정: Godot, 픽셀 320×180 정수배, 하나로 이어진 긴 바다를 좌우로 항해, 파도·내구도·어창이 항해를 제한, 깊이 조준 + 줄다리기 낚시, 어군 표시·암초·섬·난파선·떠다니는 물건, 항구는 걸어 다니는 구역, 첫 전설의 심해어를 바치면 끝, 이야기는 그림 컷 + 자막, 별주부는 이야기 장면에만, **플레이 시간 제한 없음**.

사용자가 준 중요한 피드백:

- 처음 설계(고정 한 화면)를 "너무 단순하다"고 반려했다. 다른 낚시 게임처럼 횡으로 이동하고 멀리 나갈 수 있어야 한다. 설계를 단순하게 줄이지 말 것.
- 기획은 사용자가 말한 대로 받아 적지 말고 인터뷰식으로 잡는다.
- 단기간에 스토리 애니메이션과 플레이 분량을 뽑기 위해 일반 2D가 아니라 픽셀로 정했다.
- 귀여움이 핵심이다.

## cat-angler: 그레이박스 상태

- 실행: `uv run -q --project harness/tools gf --project games/cat-angler engine run --record --id <이름>`
- 중간부터: 앞에 `CA_START="rod=3,boat=3,baits=8,legendbait=2,x=2200"` 를 붙인다.
- 조작과 해 볼 것: `games/cat-angler/design/graybox-play.md`
- 균형 수치는 전부 `games/cat-angler/scripts/data.gd` 의 표에 있다.
- 봇 `bot/full_run.py` 가 엔딩까지 깬다(게임 시간 약 27분, 출항 14번).
- 사용자의 첫 플레이는 63초였다: 멸치 1마리를 낚고 팔지 않은 채 종료. "할 일 없는 키" 반응 3번, "안 됨" 3번. **왜 그만뒀는지는 아직 답을 받지 못했다.** 다음 세션은 이것부터 묻는다.

그레이박스에서 의심스러운 것(제작 에이전트의 추정, 사람 확인 필요):

- 줄다리기 예고 0.38초가 사람에게 충분한지
- 넙치가 첫 낚싯대로 너무 쉽게 끊어지는지
- 배 2단계 전 얕은 바다 4바퀴가 단조로운지
- 깊은 곳에서 매번 줄을 5~6초 다시 내리는 번거로움
- 작은 물고기가 0.4초 만에 올라와 싱거운지
- 8~10px 한글 가독성

## 다음에 할 일

1. 사용자에게 첫 플레이에서 무엇이 걸렸는지 묻고, 그 답과 `engine replay` 로 그레이박스 조작감·숫자를 고친다. 한 번에 하나씩 바꾸고 매번 `engine test` 와 캡처로 확인한다.
2. 손맛이 승인되면 `gf state approve` → `assets` 단계. 픽셀 사슬은 `harness/skills/gf-assets-pixel/` 를 따른다(단색 배경 생성 → chroma → pixel-snap(`--trim --height`) → 팔레트 적용 → 1배 검사).
3. 이야기 컷(여는 장면 6~8컷, 닫는 장면 2컷)과 소리.

## 알려진 한계와 미확인

- 3D 사람 캐릭터 애니메이션은 약하다. AAA급 범위의 근거는 조사에도 없었다.
- 대기 자세가 없다: 영상 모델이 걷기 시작하며 자세를 바꿔 정지 스프라이트를 대기 자세로 쓰기 어렵다.
- 디테일 많은 픽셀 캐릭터는 1배에서 얼룩이 된다. 단순한 형태로 생성해야 한다.
- 소리는 측정만 했고 사람이 듣지 않았다. `flat2d-web` 은 음악이 효과음보다 많이 작다.
- 소리 측정 경고는 단계 승인을 막지 않는다. 다듬기 단계부터 막을지는 미정.
- `tomli-w` 의존성은 쓰이지 않는다. 빼도 되는지 사용자 답을 못 받았다.
- `gf engine` 명령이 게임에 인자를 넘길 방법이 없어 cat-angler 는 환경 변수 `CA_START` 를 쓴다.
- 템플릿 관례대로 `main.gd` 멤버 초기화에서 난수를 쓰면 브리지가 시드를 정하기 전이라 실행마다 달라진다. 게임 객체는 `_ready` 에서 만든다. 템플릿 문서에 아직 적지 않았다.
- 스킬 13개 중 자연어 발동을 실제 세션에서 다시 확인한 것은 3개(pixel, verify, audio)다.

## 비용

fal 추정 누적 약 $9 (하네스 시험 약 $8, cat-angler 약 $0.7). Tripo·Seedance 는 단가로 계산이 안 돼 실제 청구액은 대시보드로 확인해야 한다. 잔액이 두 번 바닥났고 사용자가 두 번 충전했다. cat-angler 데모 전체의 생성 비용은 $13~17 로 가늠했다.

## 저장소에 올리지 않은 것

`.gitignore` 참조. `.env`, 가상 환경과 `node_modules`, Godot 캐시, 큰 실행 기록(`captures/sessions/*.jsonl`, 봇 `trace.jsonl`), 수집한 레퍼런스 이미지와 모음판, `demo-check/plugin-session/`.

## 갱신 (2026-11-23 오후): 그레이박스 반려와 전면 재제작

사용자가 그레이박스를 강하게 반려했다: 기준 화면 느낌이 아니고 너무 거칠고 단순하다, 화면이 넘어가야 한다, 미끼와 상점이 따로 구현돼야 한다, 첫 애니메이션이 나레이션 하나다, 퀄리티가 말이 안 되게 낮다. **이 사용자에게는 색 덩어리 임시 버전을 보여 주고 손맛을 묻는 방식이 통하지 않는다. 실제 품질의 화면으로 보여 줘야 한다.**

그래서 세 갈래로 다시 만들었다(단계는 `assets`):

- 해상도 640×360, 장소마다 씬 분리와 전환 연출, 가게 4곳 전용 실내 화면, 저장, 첫 출항 길잡이
- 그림 197장(24색 팔레트), 효과음 23개, 음악 9곡. 규격은 `games/cat-angler/design/asset-spec.md`, 상태는 `design/asset-status.md`
- 여는 컷신 10컷 89.6초, 닫는 컷신 3컷 30.4초 (`scenes/cutscenes/`, 대본 `design/cutscene-script.md`)

결과 화면은 `games/cat-angler/SCREENSHOTS.md`. 조작과 실행은 `design/play-guide.md` (`graybox-play.md` 를 대체).

아직 약한 것은 SCREENSHOTS.md 끝에 있다. 사용자의 평가를 아직 받지 못했다. cat-angler 누적 생성 비용 약 $16.

## 갱신 (2026-11-23 저녁): 다듬기 패스와 교육 자료

- 다듬기: 바다 화면만 세계를 2배로 당겨 그려 고양이와 배가 기준 화면 비율이 됐다. 물속 장식, 잔고기 떼, 해파리, 바닥 섞임, 고양이 꼬리·귀·깜박임, 가게 주인 입 모양, 컷신 걷기 프레임과 용왕 깜빡임, 빠진 효과음 5개, 길잡이 문구, 마우스 왼쪽 버튼 = Space.
- 블라인드 심사(기준 화면 대 게임 화면) 7번 중 앞 5번은 기준 화면 승, 마지막 2번은 게임 화면 근소 승. 표본이 작다.
- 최종 코드로 타이틀 → 닫는 컷신 한 번 실행: 1757초, 입력 1466/1466 반응, 오류 0. `gf check assets/audio/evidence` 통과. 하네스 테스트 282개 통과.
- 남은 약점은 `games/cat-angler/SCREENSHOTS.md` 끝에 있다. 큰 것: 바다만 2배라 마을·실내와 고양이 크기가 다르다, 소리는 아무도 듣지 않았다, 기본 모니터에서 p95 60fps 미달(다른 화면에서는 충족).
- cat-angler 비용 기록 합계 $12.80 (`.gf/ledger.jsonl`). 앞의 "약 $16"은 근거 없는 어림이었다.
- 교육 자료: `docs/education/` (Markdown 원본 + HTML). 공개 주소 https://lofcgi.github.io/gameforge/docs/education/ . 원본을 고치면 `uv run docs/education/build_html.py` 로 HTML을 다시 만든다. GitHub Pages는 main 루트를 그대로 내보낸다(`.nojekyll`).
- 사용자는 아직 다시 만든 게임을 플레이해 평가하지 않았다. 다음 세션은 그것부터 받는다.

