---
name: gf-graybox
description: 게임의 프로토타입, 핵심 루프, 조작감, 레벨 배치, "일단 돌아가게", 플레이 테스트, "느낌이 이상하다"를 말하거나 .gf/state.json 의 stage 가 graybox 일 때는, 게임 코드를 고치기 전에 먼저 이 스킬을 쓴다. gameforge 의 graybox 단계: 템플릿 위에 도형만으로 핵심 루프(조작 → 목표 → 승패 → 재시작)를 만들고, 에이전트가 직접 실행해 스크린샷·봇·입력 재생으로 확인한 뒤 사람이 플레이해 재미를 판정한다.
---

# graybox: 그림 없이 재미부터

도형만 쓴다. 에셋을 입히지 않는다. 재미가 없으면 미련 없이 버리고 다시 만든다 — 프로토타입은 버리려고 만드는 것이다. 재미는 사람만 판정할 수 있다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 준비

읽는다: `design/brief.md`(핵심 루프, 닫힌 결정, 인수 기준), 게임 폴더의 `AGENTS.md`(구조와 규칙), 그리고 브리지 계약 `${CLAUDE_PLUGIN_ROOT}/templates/README.md`. 계약의 요점은 `${CLAUDE_SKILL_DIR}/bridge-rules.md` 에 있다.

brief 의 인수 기준을 작업 목록으로 옮긴다. 기준에 없는 것은 만들지 않는다.

## 루프: 하나 바꾸고, 돌리고, 본다

한 번에 한 가지만 바꾼다(이동 → 점프 → 위험물 → 목표 → 재시작 순서처럼). 바꿀 때마다:

```sh
$GF engine test                                         # 부팅, 계약, 첫 화면, 입력 생존, 콘솔 오류
$GF engine capture --out captures/<이름> --at 1,3        # 그 시각의 실제 화면 + capture.json
$GF engine capture --out captures/<이름> --script bot/<액션>.json --at 2.2   # 입력을 넣으면서
```

- 찍힌 PNG 를 Read 로 직접 본다. 테스트 통과는 "화면이 맞다"는 뜻이 아니다. 검은 화면, 화면 밖 플레이어, 겹친 도형은 눈으로만 잡힌다.
- 결과의 `errors`/`warnings`, `checks`, `inputs.unresponsive` 를 본다. 오류 0건을 유지한다.
- **입력에 반응하지 않는 것은 버그다.** `input_liveness` 실패나 `unresponsive` 항목은 "나중에"로 미루지 않는다.
- 새 액션은 입력 맵(Godot `project.godot`) 또는 `KEYMAP`(web `src/input.js`)과 브리지 `info.actions` 양쪽에 넣는다. 눌렀을 때 반드시 반응해야 하는 액션은 `info.probe` 에도 넣는다.
- 레벨을 바꾸면 `bot/clear.json`(레벨을 깨는 고정 입력)도 같이 고친다.

액션 스크립트 형식: `{"seed": 0, "actions": [{"t": 0.2, "press": "right"}, {"t": 2.0, "tap": "jump", "hold": 0.1}, {"t": 3.0, "release": "right"}]}`

## 봇으로 끝까지 가 본다

```sh
$GF engine bot --policy goal --seconds 30                 # 내장 정책: goal(목표로 이동), random, idle
$GF engine bot --policy bot/clear.json --require-goal     # 고정 입력으로 레벨을 깬다. 못 깨면 실패
$GF engine bot --policy bot/<정책>.py --seconds 60 --shot-every 5   # decide(state, info) -> 누를 액션 목록
```

`reached_goal`, `time_s`, `deaths`, `liveness` 를 보고 결과 폴더(`captures/bot/<정책>-<시각>/`)의 스크린샷 몇 장을 Read 로 본다. `idle` 로 돌렸는데 목표에 닿거나, `random` 이 쉽게 깨면 게임이 성립하지 않는 것이다. 봇은 "깰 수 있다"만 알려 준다. 재미와 균형은 알려 주지 못한다.

막히는 화면이나 판단이 애매한 스크린샷 묶음은 `playtest-reviewer` 서브에이전트에게 결과 폴더 경로를 주고 플레이어 입장의 문제 목록을 받는다.

## 사람이 플레이한다

인수 기준이 실행으로 확인되면 사용자에게 넘긴다. 창이 뜨는 명령이므로 사용자가 준비됐을 때 실행한다(창을 닫으면 끝난다).

```sh
$GF engine run --record            # captures/sessions/<id>.jsonl 에 입력과 상태가 남는다
```

플레이 뒤에 세 가지만 묻는다: ① 한 판 더 하고 싶었나 ② 조작에서 거슬린 순간 ③ 헷갈린 것. 사용자가 한 말은 `design/playtest-notes.md` 에 날짜와 함께 적는다. 이것이 다음 작업 목록이다.

"느낌이 이상하다"는 말을 추측으로 고치지 않는다. 기록을 재생해서 재현한다.

```sh
$GF engine replay <id> --shot-every 1     # replay.json: 반응 없는 입력 후보(inputs.unresponsive), 원본과의 위치 차이(drift)
```

`unresponsive` 후보는 버그로 다룬다. 고친 뒤 같은 기록을 다시 재생해 사라졌는지 확인한다. 한 번에 문제 5~10개를 넘겨받아 하나씩 고치고, 다시 플레이를 요청한다.

## 재미가 없으면

사용자가 두세 번 플레이하고도 "아직 재미없다"면 조정으로 버티지 않는다. 무엇을 바꿀지 사용자와 정한다: 핵심 동사를 바꾼다 / 규칙 하나를 더하거나 뺀다 / brief 로 돌아간다(`$GF state set plan`). 지금 그레이박스는 버려도 된다.

## 승인

사용자가 "이 루프가 재미있다"고 말했고 인수 기준이 모두 실행으로 확인됐을 때:

```sh
$GF engine test                                       # 결과가 captures/test/result.json 에 남는다 (승인 근거)
$GF engine bot --policy bot/clear.json --require-goal
$GF check evidence
$GF state approve --note "<사용자의 판정 한 줄>"
```

마지막 봇 실행의 스크린샷 경로와 결과(목표 도달, 시간, 사망 수)를 사용자에게 함께 보여 준다. 다음은 에셋 단계다(스타일에 맞는 `gf-assets-*`).
