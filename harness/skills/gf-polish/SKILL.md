---
name: gf-polish
description: 게임을 "다듬자"고 하거나 "타격감", "게임 필", "손맛", "밋밋하다", "뭔가 허전하다", "첫인상", "최적화", "렉", "로딩이 길다"를 말할 때, 또는 stage 가 polish 일 때는, 코드를 고치기 전에 먼저 이 스킬을 쓴다. gameforge 의 polish 단계: 손맛(반응·타격감), 가독성, 첫 1분, 성능을 우선순위대로 작은 변경 하나씩 고치고 매번 실행·심사·사람 플레이로 확인한다. 가장 많은 노력이 드는 단계다.
---

# polish: 프로토타입을 게임으로 만드는 구간

돌아가는 것과 기분 좋은 것 사이가 가장 멀다. 실제 사례에서 가장 많은 작업이 들어간 곳은 처음 만들 때가 아니라 이 단계였다. 계획할 때 **전체 노력의 절반쯤**을 여기에 잡는다. 사용자에게도 그렇게 말해 둔다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md`, 검증 방법: `gf-verify` (아직 안 읽었으면 먼저 읽는다).

## 1. 문제 목록을 만든다

추측으로 시작하지 않는다. 세 곳에서 모은다.

```sh
$GF engine bot --policy bot/clear.json --require-goal --shot-every 2 --out captures/polish-base
$GF engine perf --seconds 10 --script bot/clear.json --out captures/perf/base.json
$GF engine run --record            # 사용자가 처음부터 끝까지 한 판
```

1. **사람**: 사용자의 플레이 메모(`design/playtest-notes.md`)와 방금 플레이의 한마디. 가장 무겁게 본다.
2. **플레이어 시점 검토**: `playtest-reviewer` 서브에이전트에게 `captures/polish-base` 의 절대 경로와 `design/brief.md`, `design/look/frame.png` 경로를 주고 문제 목록을 받는다.
3. **측정**: `perf` 의 프레임 시간(평균과 최악), `load_s`, 콘솔 경고.

모은 것을 `design/polish-list.md` 에 표로 적고(문제, 근거 파일, 분류, 순위) 사용자에게 보여 준다. 순서는 아래 우선순위를 기본으로 하되 사용자가 바꿀 수 있다.

## 2. 우선순위

| 순위 | 분류 | 묻는 것 | 대표 수단 |
|---|---|---|---|
| 1 | **손맛** | 입력이 즉시, 분명하게 돌아오는가 | 입력 지연 제거, 히트스톱, 화면 흔들림, 플래시, 스쿼시·스트레치, 파티클, 소리 |
| 2 | **가독성** | 주인공·위험·목표가 한눈에 보이는가 | 명도 대비, 외곽선, 배경 채도 낮추기, 위험 예고 |
| 3 | **첫 1분** | 설명 없이 무엇을 할지 아는가, 30초 안에 재미가 나오는가 | 첫 화면, 첫 성공까지의 거리, 실패 후 재시작 시간 |
| 4 | **성능** | 목표 프레임을 지키는가, 로딩이 짧은가 | 드로우 콜·삼각형·텍스처 크기 줄이기 |
| 5 | 그 밖 | 화면 전환, 결과 화면, 설정 | — |

분류별 구체 수단과 출발 수치는 `${CLAUDE_SKILL_DIR}/feel-checklist.md` 에 있다. 새 기능·새 레벨은 여기서 만들지 않는다(brief 의 Out of scope). 필요해 보이면 사용자에게 묻는다.

## 3. 루프: 하나 고치고, 확인하고, 남기거나 되돌린다

목록의 한 줄마다:

1. 변경 **전** 화면을 찍는다: `$GF engine capture --out captures/<항목>-before --script bot/<액션>.json --at <그 순간> --seed 0`
2. **한 가지만** 바꾼다. 수치(흔들림 세기, 정지 프레임 수)는 코드 위쪽 상수로 빼 둔다.
3. 실행: `$GF engine test` → 같은 명령으로 `captures/<항목>-after` 를 찍고 Read 로 본다.
4. 판정:
   - 화면이 달라지는 변경 → 블라인드 심사(`gf-verify` 2절, `--mode change --target design/look/frame.png`). 지면 되돌린다. 묶음의 `stop.met` 이 true 면 그 방향은 끝낸다.
   - 움직임·타이밍·소리 변경(정지 화면으로 안 보이는 것) → 연속 스크린샷(`--at 1.00,1.05,1.10,1.15`)으로 실제로 일어나는지만 확인하고, 좋은지는 사람에게 묻는다.
   - 성능 변경 → `$GF engine perf --seconds 10 --script bot/clear.json --out captures/perf/<항목>.json` 을 base 와 비교. 나아지지 않았으면 되돌린다.
5. `$GF engine bot --policy bot/clear.json --require-goal` 로 게임이 여전히 깨지는지 확인한다(손맛 변경이 판정을 바꾸는 일이 잦다).
6. `design/polish-list.md` 의 그 줄에 결과와 근거 파일을 적는다.

서너 개를 고칠 때마다 사용자에게 `$GF engine run --record` 로 플레이를 부탁한다. 손맛은 사람만 안다. 사용자의 말이 심사·봇 결과와 다르면 사용자의 말을 따른다.

## 4. 멈출 때

- 목록의 1~3순위가 비었고 사용자가 "이제 됐다"고 한다. 또는
- 심사 묶음들이 멈춤 조건에 닿았고, 최근 사람 플레이에서 새 문제가 5개 미만이다.

끝없이 다듬지 않는다. 남은 것은 `design/polish-list.md` 에 "미룸"으로 적는다.

## 승인

```sh
$GF engine test
$GF engine bot --policy bot/clear.json --require-goal --out captures/approve-polish
$GF engine perf --seconds 10 --out captures/perf/final.json
$GF check assets
$GF check audio --require
$GF judge history
$GF check evidence
```

사용자에게 최종 스크린샷, base 대비 성능, 심사 요약, 고친 것과 미룬 것, 확인하지 못한 것을 보여 주고 마지막으로 한 판 플레이를 부탁한다. 사용자가 승인하면 `$GF state approve --note "<승인 내용>"`. 다음은 `gf-publish`.
