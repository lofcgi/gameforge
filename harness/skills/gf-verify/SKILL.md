---
name: gf-verify
description: 게임 화면이 목표(기준 화면)와 비슷한지·나아졌는지 봐 달라거나 "확인해 봐", "진짜 돼?", "더 좋아졌어?"라고 할 때, 게임 코드를 고친 뒤 "됐다/고쳤다/완료"라고 말하기 전, 단계를 승인하려 할 때는, 스크린샷을 스스로 보고 평가하기 전에 먼저 이 스킬을 쓴다. gameforge 의 세 가지 검증과 근거 규칙: 자가 실행(engine test/capture/bot/perf)은 동작을, 블라인드 심사(judge pair → blind-judge 서브에이전트 → judge record, 멈춤 규칙)는 화면을, 사람 플레이(engine run --record → replay)는 감각을 확인한다.
---

# 검증: 동작은 실행으로, 화면은 블라인드 심사로, 감각은 사람이

| 검증 | 잡는 것 | 못 잡는 것 | 언제 |
|---|---|---|---|
| **자가 실행** | 부팅 실패, 콘솔 오류, 반응 없는 입력, 깰 수 없는 레벨, 느린 프레임 | 화면이 좋은가, 재미있는가 | 코드를 바꿀 때마다 |
| **블라인드 심사** | 화면이 목표에 가까워졌는가, 변경이 나아졌는가 (자기 칭찬 방지) | 재미, 조작감, 소리 | 화면에 영향을 주는 변경마다 |
| **사람 플레이** | 재미, 손맛, 헷갈림, 소리 | (사람의 시간이 든다) | 빌드가 달라질 때마다, 단계 승인 전 |

사람의 판정은 모든 자동 통과보다 우선한다.

## 근거 규칙

**실행해서 본 것만 말한다.** "고쳤다", "된다", "완료"라고 말하려면 그 변경 **뒤에** 돌린 결과가 있어야 하고, 사용자에게 그 파일의 절대 경로를 함께 준다. 지켜야 할 것:

- 테스트 통과만으로 "화면이 맞다"고 하지 않는다. 스크린샷을 Read 로 직접 본다.
- 실패한 검사를 통과시키려고 검사를 약하게 만들지 않는다: `info.probe` 에서 액션 빼기, 상태에 매 틱 변하는 값 넣기, `bot/clear.json` 을 쉬운 길로 바꾸기, 브리지 파일 수정, `--threshold` 올리기. 게임을 고친다.
- 스크린샷·심사 기록을 지우거나 골라서 보여 주지 않는다. 진 심사도 기록에 남는다.
- 확인하지 못한 것은 "확인 못 했다"고 말한다(예: "소리는 재기만 했고 듣지 못했다").

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 1. 자가 실행

```sh
$GF engine test                                               # 변경마다. checks 다섯 항목이 모두 ok, 오류 0건. 결과는 captures/test/result.json 에 남는다 (승인 근거)
$GF engine capture --out captures/<이름> --at 1,3 [--script bot/<액션>.json]   # 플레이어 시점 화면 + capture.json
$GF engine bot --policy bot/clear.json --require-goal          # 레벨을 여전히 깰 수 있는가
$GF engine bot --policy goal --seconds 30                      # 내장 정책 goal / random / idle
$GF engine perf --seconds 5 --out captures/perf/<이름>.json     # 프레임 시간, 드로우 콜, 메모리, 로딩 시간
$GF check assets                                              # 참조한 에셋이 있는가, 픽셀 프로젝트에 원본이 섞였는가
$GF check audio --require                                     # 참조한 오디오가 있고 소리가 나는가 (warnings: 잘림, 앞 무음, 반복 이음매)
$GF engine audio --expect jump=jump                           # 실행 중에 소리가 실제로 나는가 (엔진 안의 신호를 잰다. 스피커 소리가 아니다)
```

- 결과 JSON 의 `checks`, `errors`, `warnings`, `inputs.unresponsive`, `liveness`, `reached_goal` 을 읽는다. 반응 없는 입력은 버그다.
- 같은 화면을 전후로 비교하려면 **같은 `--script`, 같은 `--at`, 같은 `--seed`, 같은 `--size`** 로 찍는다.
- 화면 배치를 고쳤으면 다른 창 크기로도 찍어 본다: `--size 1024x768`(4:3), `--size 2560x1080`(21:9), web 의 레티나는 `--scale 2`. Godot 의 `--size` 는 물리 픽셀이고, 창이 화면보다 커서 실패하면 `--screen <번호>` 로 큰 화면을 고른다. PNG 는 띠(레터박스)까지 포함한 창 그대로다.
- Godot 결과의 `logs` 에 "앱이 포커스를 잃어 눌러 둔 키 … 가 풀렸다" 오류가 있으면 실행 중에 누가 게임 창을 활성화했던 것이다. 그 실행은 버리고 다시 돌린다. 자동 실행은 창의 포커스를 원래 앱에 돌려주므로 평소에는 나오지 않는다.
- 스크린샷이 여러 장이거나 판단이 애매하면 `playtest-reviewer` 서브에이전트에게 결과 폴더의 절대 경로와 brief 경로를 주고 플레이어 입장의 문제 목록을 받는다(코드를 고치지 않는 읽기 전용 검토자다).
- 성능은 변경 전 값을 `captures/perf/base.json` 으로 남겨 두고 비교한다. `--uncapped` 는 수직 동기화를 끄고 최대 프레임을 잰다.

## 2. 블라인드 심사

자기가 고친 화면을 자기가 평가하면 항상 "좋아졌다"가 나온다. 전후 화면을 섞어 맥락 없는 새 심사자에게 준다. 절차와 해석은 `${CLAUDE_SKILL_DIR}/blind-judging.md` 에 자세히 있다. 요약:

```sh
# 변경 판정: a=수정 전, b=수정 후. 목표 그림을 함께 보여 준다
$GF judge pair --a captures/before/shot_01_t1.00.png --b captures/after/shot_01_t1.00.png \
  --target design/look/frame.png --mode change --id <쌍 이름> --series <묶음 이름>

# 목표 대비 판정: a=목표 그림, b=게임 화면
$GF judge pair --a design/look/frame.png --b captures/now/shot_01_t1.00.png --mode target --id <쌍 이름> --series <묶음 이름>
```

1. 결과의 `judge_reads`(심사 폴더)에 있는 파일들의 **절대 경로만** `blind-judge` 서브에이전트에게 준다. 어느 쪽이 수정 후인지, 무엇을 고쳤는지, 프로젝트 설명은 주지 않는다. 메인 에이전트는 `.gf/judge/` 를 읽지 않는다.
2. 심사자가 돌려준 JSON(`winner`, `scores`, `notes`)을 그대로 기록한다:

   ```sh
   $GF judge record --id <쌍 이름> --winner <X|Y|tie> --scores '<심사자의 scores JSON>' --notes "<심사자의 notes>"
   $GF judge history --series <묶음 이름>
   ```

3. 결과를 따른다:
   - `change` 방식: `keep_change` 가 false 면(수정 전이 이겼다) **변경을 되돌린다.** 이기거나 비겼을 때만 남긴다.
   - `stop.met` 이 true 면 그 방향은 **그만 다듬고** 다음 작업으로 간다 (`target`: 게임 화면이 목표를 2번 이김 / `change`: 최근 2판 연속으로 수정 후가 못 이김). 기준 횟수는 `--stop-after` 로 바꾼다.
   - **목표 그림에 없다는 이유만으로 게임 화면의 요소를 지우지 않는다.** UI, 캐릭터, 이펙트는 게임에 필요해서 있는 것이다.
4. 심사자의 `notes` 에서 고칠 점 하나를 골라 다음 변경으로 삼는다.

심사는 화면만 본다. 엄격한 심사에서는 좋은 화면도 5~6점이 나온다. 점수의 절대값이 아니라 승패와 이유를 쓴다.

## 3. 사람 플레이

```sh
$GF engine run --record                 # 사용자가 플레이. captures/sessions/<id>.jsonl
$GF engine replay <id> --shot-every 1   # 재현 + 반응 없는 입력 후보 + 원본과의 위치 차이
```

- 플레이를 부탁할 때 **무엇을 봐 달라는지** 한두 가지로 좁힌다("점프 높이가 맞는지", "첫 30초에 뭘 해야 할지 아는지").
- 사용자의 말은 고치지 말고 그대로 `design/playtest-notes.md` 에 날짜와 함께 적는다. 한 번에 문제 5~10개를 받아 하나씩 고친다.
- "느낌이 이상하다"는 추측으로 고치지 않는다. 기록을 `engine replay` 로 재현해 그 순간의 스크린샷과 상태를 보고 원인을 찾는다. 고친 뒤 같은 기록을 다시 재생한다.
- 마우스 이동은 기록되지 않는다. 마우스 시점 게임은 재생이 원본과 어긋날 수 있다(`drift` 를 본다).
- 사람 없이 기록 경로만 점검하려면 `$GF engine run --record --id <이름> --script bot/clear.json --seconds 8 --os-input` 뒤에 `$GF engine replay <이름>` 을 돌린다. 운영체제 키 이벤트를 게임 창에 보내 기록하므로(macOS, 터미널 앱의 손쉬운 사용 권한 필요. 실행 중에는 게임 창이 맨 앞에 있어야 한다) `drift.max` 가 0 이고 `inputs.unresponsive` 가 비어야 한다. 이것은 키보드 하드웨어를 거치지 않으므로 "사람이 눌러 봤다"를 대신하지 않는다.

## 단계 승인 절차 (graybox 이후 공통)

```sh
$GF engine test
$GF engine capture --out captures/approve-<단계> --at 1,3 [--script bot/clear.json]
$GF check evidence            # 무엇이 모자란지 말해 준다. 통과해야 승인 명령이 막히지 않는다
```

사용자에게 ① 방금 찍은 스크린샷의 절대 경로 ② 테스트·봇 결과 한 줄 ③ 심사 기록 요약(`judge history`) ④ 확인하지 못한 것을 보여 주고 승인을 묻는다. 사용자가 승인하면 `$GF state approve --note "<승인 내용>"`. 승인 명령은 훅이 `check evidence` 로 다시 검사한다: 마지막 코드·에셋 변경보다 새로운 통과 기록과 스크린샷이 없으면 막힌다.
