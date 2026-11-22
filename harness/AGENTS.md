# gameforge 하네스

Claude Code 플러그인이다. 기획부터 공개까지 단계별로 진행하고, 단계마다 결과물(이미지·스크린샷·점수)을 파일로 남겨 사용자가 Orca/Paseo나 대화창에서 보고 승인하게 한다. 2D(픽셀 포함)와 3D를 같은 뼈대로 다루고 에셋 모듈만 스타일별로 바꾼다.

## 디렉터리와 소유권

```
harness/
  .claude-plugin/plugin.json      플러그인 선언
  skills/<name>/SKILL.md          단계 스킬 (gf-* 접두사)
  agents/*.md                     서브에이전트 (블라인드 심사 등)
  hooks/hooks.json, hooks/*.py    차단 규칙
  tools/                          uv 프로젝트. 패키지 gf, 실행 파일 gf
    pyproject.toml
    gf/cli.py                     하위 명령 등록만 한다 (각 모듈의 register(subparsers) 호출)
    gf/core/                      config, state, ledger, fal 클라이언트, 출력 규약, 경로 해석(paths), 2D 화면 설정(render_profile)
    gf/gen/                       생성기: image, video, model3d, rig, audio
    gf/post/                      후처리: pixel, chroma, resize, frames, sheet, contact
    gf/blender/                   Blender 배치 스크립트와 호출기
    gf/engine/                    엔진 어댑터: godot, web
    gf/play/                      플레이 봇, 입력 기록·재생
    gf/refs/                      레퍼런스 수집·모음판·선택·측정
    gf/judge/                     블라인드 심사용 쌍 만들기
    tests/
  templates/godot-2d, godot-3d, web-2d, web-3d   게임 프로젝트 템플릿
```

## 명령 규약

모든 명령은 `uv run -q --project <harness>/tools gf --project <게임 폴더> <group> <cmd> ...` 형태다. 게임 프로젝트 디렉터리를 가리키는 `--project <dir>`(기본값: 현재 디렉터리)는 `gf` 바로 뒤, group 앞에 온다. 스킬 안에서는 `<harness>` 를 `${CLAUDE_PLUGIN_ROOT}` 로 쓴다.

- 성공하면 종료 코드 0과 함께 표준 출력 마지막 줄에 JSON 한 줄을 낸다: `{"ok": true, "files": [...], "cost_usd": 0.0, ...}`.
- 실패하면 0이 아닌 종료 코드와 `{"ok": false, "error": "..."}`를 낸다. 에러를 삼키거나 조용히 대체 경로로 빠지지 않는다.
- 결과 파일은 게임 프로젝트 안에만 쓴다. 명령에 주는 상대 경로(입력·출력 모두)는 현재 폴더가 아니라 게임 프로젝트 기준이다(`gf/core/paths.py` 의 `resolve`, `inside`, `source`).

| group | 명령 | 역할 |
|---|---|---|
| (루트) | `init`, `state show/set/approve`, `doctor` | 프로젝트 생성(2D 는 스타일에 맞는 화면 설정까지), 단계 상태, 환경 점검 |
| `fal` | `search`, `price`, `schema`, `run` | 모델 검색, 단가, 입력 스키마, 임의 호출 |
| `gen` | `image`, `edit`, `rembg`, `video`, `model3d`, `rig`, `sfx`, `tts`, `music` | 역할 기반 생성 |
| `post` | `chroma`, `pixel-snap`, `resize`, `palette extract/apply`, `frames`, `align`, `loop`, `sheet`, `contact`, `inspect`, `audio-loop` | 스타일별 후처리와 숫자 검사 (`pixel-snap` 의 확대 미리보기는 `captures/inspect/pixel/` 에 따로 쓴다). `audio-loop` 는 음악의 반복 이음매를 다듬는다 |
| `blender` | `info`, `clean`, `decimate`, `rescale`, `turntable`, `run` | 3D 정리와 미리보기 렌더 |
| `engine` | `run`, `record`, `capture`, `bot`, `replay`, `perf`, `audio`, `test` | 실행, 스크린샷, 플레이 봇, 입력 기록·재생, 성능 측정, 실행 중 소리 측정(`captures/audio/result.json`), 스모크 테스트(결과를 `captures/test/result.json` 에 기록) |
| `ref` | `steam`, `frames`, `add`, `sheet`, `pick`, `unpick`, `traits`, `status` | 레퍼런스 수집과 선택. `add` 는 이미지 주소와 함께 `--source-url`(실려 있던 페이지), `--title`(작가·작품)을 받는다. 자동 수집을 막는 사이트는 `gf-reference` 스킬이 Claude in Chrome 도구로 검색 결과를 읽어 `add` 에 넘긴다 |
| `judge` | `pair`, `record`, `history` | 블라인드 심사용 X/Y 쌍 생성, 결과 기록, 묶음별 승패 |
| `check` | `evidence`, `assets`, `audio` | 승인 근거 검사(훅이 호출), 에셋·오디오 참조 검사와 음량 측정. `audio` 는 잘림·앞뒤 무음·반복 이음매를 `warnings` 로 낸다 |

## 게임 프로젝트 안의 하네스 파일

```
<game>/.gf/state.json        단계, 엔진(godot|web), 차원(2d|3d), 스타일(pixel|2d|3d-code|3d-gen), 승인 기록
<game>/.gf/config.toml       역할 → fal 모델 ID 매핑, [budget] 호출 한도, [check] allow_silent (기본값은 gf/core/defaults.toml)
<game>/.gf/ledger.jsonl      생성 호출 기록 (시각, 모델, 단가, 추정 비용, 출력 파일)
<game>/.gf/prompts.jsonl     채택된 생성 프롬프트 (--keep, 이후 생성의 기준)
<game>/.gf/judge/            심사 쌍의 정답 대응표와 history.jsonl (심사자와 메인 에이전트는 읽지 않는다)
<game>/AGENTS.md             템플릿이 넣는 게임 프로젝트 규칙 (구조, 브리지, 에셋 등록)
<game>/gf/                   브리지 (gf_bridge.gd 또는 bridge.js). 게임 쪽에서 고치지 않는다
<game>/bot/                  액션 스크립트(.json)와 봇 정책(.py). clear.json 은 레벨을 깨는 고정 입력
<game>/design/               brief.md, art-direction.md, palette.json(+png), look/ (기준 이미지), playtest-notes.md, polish-list.md
<game>/references/inbox/     수집한 레퍼런스 (이미지 + 같은 이름의 .json 메타: source_url, 주소로 넣었으면 image_url), 모음판
<game>/references/picked/    사용자가 고른 것, traits.json, traits-palette.png, analysis.md
<game>/assets/raw/           생성 원본과 후처리 중간물
<game>/assets/game/          후처리 끝난 게임용 에셋 (게임 코드는 여기만 참조한다)
<game>/captures/             엔진 스크린샷과 capture.json, bot/ (봇 결과), replays/, sessions/ (입력 기록),
                             perf/, test/ (first_frame.png, result.json), audio/ (result.json), judge/<id>/ (심사자가 읽는 폴더), turntable/, inspect/
<game>/build/                배포용 빌드 (gf 가 만들지 않는다)
```

3D 방향 규약(GLB 의 정면은 +Z, 템플릿이 그 정면을 이동 방향으로 돌린다)은 `templates/README.md` 7절 한 곳에만 적는다.

단계 순서: `plan → look → graybox → assets → polish → publish`. `state approve`로 사용자가 승인해야 다음 단계로 넘어간다.

## 생성 역할과 기본 모델

역할 이름으로 호출하고 실제 모델 ID는 설정에서 읽는다. 모델은 자주 은퇴하므로 코드에 ID를 박지 않는다. 아래는 2026-11-22에 fal 모델 검색 API로 존재를 확인한 ID다.

| 역할 | 기본 모델 |
|---|---|
| `image.concept` | `fal-ai/nano-banana-2` |
| `image.edit` | `fal-ai/nano-banana-2/edit` |
| `image.rembg` | `fal-ai/birefnet/v2` |
| `video.look` | `bytedance/seedance-2.5/image-to-video` |
| `video.sprite` | `fal-ai/kling-video/v3/turbo/standard/image-to-video` |
| `model3d.gen` | `tripo3d/p2/image-to-3d` |
| `model3d.rig` | `fal-ai/meshy/rigging` |
| `audio.sfx` | `elevenlabs/sound-effects/v3` |
| `audio.tts` | `fal-ai/elevenlabs/tts/eleven-v3` |
| `audio.music` | `elevenlabs/music/v2.5` |

입력 필드는 모델마다 다르다. `gf fal schema <id>`로 실제 스키마를 읽고 맞춘다. 추측으로 필드를 넣지 않는다.

## fal 호출 규칙

- `FAL_KEY`는 게임 프로젝트에서 위로 올라가며 찾은 `.env`를 `python-dotenv`로 로드해 환경변수로만 쓴다. 키를 출력·기록·커밋하지 않는다.
- 플랫폼 API(`https://api.fal.ai/v1/models`, `/v1/models/pricing`)는 연속 호출 시 429를 낸다. 지수 백오프로 재시도한다.
- 생성 전에 단가를 조회해 추정 비용을 계산하고, 호출 뒤 `ledger.jsonl`에 남긴다. `--max-usd`를 넘으면 실행하지 않는다. 비용을 추정할 수 없는 호출(단가 단위가 tokens·credits·compute seconds, 길이 미지정)은 `--estimate-usd <USD>` 나 `--allow-unknown-cost` 가 있어야 실행한다.
- 기본 `image.concept` 모델은 참조 이미지를 받지 않고(`gen image --ref` 실패 → `gen edit --image`), 기본 `video.sprite` 모델은 끝 프레임을 받지 않는다(`gen video --end-image` 실패 → `--role video.look` 또는 `post loop`). 조용히 다른 모델로 바꾸지 않고 오류가 대신 쓸 명령을 말한다.
- 시험 호출은 가장 싼 설정(낮은 해상도, 짧은 길이)으로 한다.

## 코드 규칙

- Python 3.12+, `uv`, `ruff`, `pytest`. 외부 의존성은 `pyproject.toml`에 추가한다.
- `gf/cli.py`에는 로직을 두지 않는다. 각 모듈이 `register(subparsers)`를 제공한다.
- 다른 소유자의 디렉터리는 수정하지 않는다. 공용으로 필요한 것은 `gf/core/`에 있고, 없으면 보고한다.
- 네트워크 없이 도는 단위 테스트를 `tests/`에 둔다. 실제 생성 호출 시험은 수동 실행 스크립트로 분리한다.
- 특정 기존 게임을 재현하는 프롬프트·템플릿·예제를 넣지 않는다.
