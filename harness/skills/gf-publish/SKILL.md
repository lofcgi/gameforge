---
name: gf-publish
description: 게임의 배포, 빌드, export, itch.io, 링크 공유, 공개, 게시글, 트레일러, 레딧·X 에 올리기를 말하거나 stage 가 publish 일 때는 먼저 이 스킬을 쓴다. gameforge 의 publish 단계: 엔진별로 배포용 빌드를 만들고, 바로 플레이할 수 있는 링크를 준비하고, AI 가 한 것과 사람이 한 것을 나눠 밝히는 공개 글을 쓰고, 올릴 커뮤니티의 규칙을 확인한다.
---

# publish: 플레이할 수 있는 링크가 먼저다

영상만 있고 링크가 없는 게시글의 품질 주장은 믿어 주지 않는다. 누르면 바로 플레이되는 링크(가입 없이)가 가장 강한 증거다. 게시와 업로드는 **사용자가 직접** 한다. 에이전트는 빌드, 점검, 글 초안까지 한다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 1. 내보내기 전 점검

```sh
$GF engine test
$GF engine bot --policy bot/clear.json --require-goal --out captures/publish-bot
$GF engine perf --seconds 10 --out captures/perf/publish.json
$GF check assets
$GF check audio --require
$GF state show
```

하나라도 실패하면 내보내지 않는다. 이름을 확인한다: 게임 제목, 캐릭터 이름, 로고가 기존 게임과 겹치지 않는가(사용자에게 검색해 보게 한다).

## 2. 빌드

`gf` 에는 빌드 명령이 없다. 엔진의 방법을 직접 쓴다. 자세한 절차와 주의는 `${CLAUDE_SKILL_DIR}/build.md`.

| 엔진 | 방법 | 결과 |
|---|---|---|
| `web` | 빌드 단계가 없다. 실행에 필요한 파일만 `build/web/` 으로 복사한다 (web-3d 는 `node_modules/three` 의 필요한 부분 포함) | 정적 폴더 → zip |
| `godot` | `godot --headless --path . --export-release "Web" build/web/index.html` (또는 데스크톱 프리셋). `export_presets.cfg` 가 필요하다 | 웹 폴더 또는 실행 파일 |

**빌드한 것을 다시 확인한다.** 개발 폴더에서 통과한 것과 빌드가 같다는 보장이 없다(파일 누락, 경로 대소문자, 압축). `gf engine` 명령은 개발 폴더만 실행하므로 빌드 폴더는 아래처럼 확인한다:

```sh
cd <게임 폴더>/build/web && python3 -m http.server 8765      # 백그라운드로
```

사용자에게 `http://127.0.0.1:8765` 를 열어 **처음부터 끝까지 한 판** 해 보게 한다(소리 포함). 에이전트는 서버 로그의 404 를 확인한다. 이 확인이 끝나기 전에는 "빌드됐다"고만 말하고 "배포해도 된다"고 하지 않는다.

## 3. 플레이 링크

웹 빌드를 올릴 곳(itch.io HTML5, GitHub Pages, Cloudflare Pages 등)은 사용자가 고르고 직접 올린다. 올린 뒤 점검표:

- [ ] 로그인·설치 없이 링크만으로 플레이된다 (시크릿 창에서 확인)
- [ ] 로딩이 10초를 넘지 않는다. 넘으면 진행 표시가 있다
- [ ] 첫 화면에 조작법이 보이거나 누르면 바로 알 수 있다
- [ ] 다른 브라우저 하나, 휴대폰 하나에서 열어 봤다 (안 되면 안 된다고 페이지에 적는다)
- [ ] 소리가 난다 (첫 입력 뒤)
- [ ] 페이지에 조작법, 한 줄 소개, AI 사용 내용이 있다

## 4. 공개 글

`design/publish-post.md` 에 초안을 쓴다. 틀과 예시는 `${CLAUDE_SKILL_DIR}/posting.md`. 반드시 들어가는 것:

1. **플레이 링크가 본문 맨 위**에.
2. **AI 가 한 것 / 사람이 한 것**을 나눠서. 사실대로 쓴다. 근거는 프로젝트에 있다:
   - AI 가 한 것: 코드(어떤 모델·도구), 생성 에셋 종류와 사용 모델(`.gf/ledger.jsonl` 의 역할·엔드포인트), 생성 횟수와 비용(`$GF state show` 의 `spent_usd`)
   - 사람이 한 것: 기획 결정(`design/brief.md`), 레퍼런스 선택, 룩 승인, 플레이테스트 횟수와 메모(`design/playtest-notes.md`, `captures/sessions/` 의 기록 수), 반려한 것
3. **과정과 숫자**: 걸린 기간, 단계, 실패한 것 하나 이상. 잘된 것만 쓴 글은 홍보로 읽힌다.
4. **영상·스크린샷의 출처**: 봇이 플레이한 영상이나 스크린샷이면 "봇이 플레이한 화면"이라고 먼저 밝힌다. 가능하면 사람이 플레이한 끊김 없는 장면을 쓴다. 연출 컷보다 실제 플레이가 낫다.
5. 한계: 아직 안 되는 것, 알려진 버그.

과장하지 않는다("AAA 급", "혼자 하루 만에 완성" 같은 표현은 반발을 부른다). 프로토타입이면 프로토타입이라고 쓴다.

## 5. 올릴 곳의 규칙을 확인한다

커뮤니티마다 AI 제작물 규칙이 다르고 자주 바뀐다. **올리기 직전에 그 커뮤니티의 규칙 페이지를 직접 읽는다**(에이전트가 읽어 요약해 주고, 판단은 사용자가 한다). 조사 시점(2026-11)의 예는 `posting.md` 에 있다: AI 개발 과정을 본문에 쓰게 하는 곳, AI 프로젝트 자체를 금지하는 곳, 판매 게임에 플레어를 요구하는 곳. 금지하는 곳에는 올리지 않는다. AI 사용을 숨기고 올리지 않는다.

스토어(Steam 등)에 올릴 때는 그 스토어의 AI 콘텐츠 공시 양식을 규정대로 채운다. 공시 문구가 반응의 중심이 될 수 있다는 점을 사용자에게 미리 말해 둔다.

## 승인

사용자에게 빌드 폴더, 플레이 링크, `design/publish-post.md` 의 절대 경로를 주고 점검표 결과를 보여 준다. 사용자가 직접 플레이 링크를 확인하고 승인하면:

```sh
$GF check evidence
$GF state approve --note "<공개한 곳과 링크>"
```

공개 뒤에 받은 반응(버그, 조작감 지적)은 `design/playtest-notes.md` 에 모아 다음 polish 의 목록으로 쓴다(`$GF state set polish`).
