# 블라인드 심사 돌리기

> 문서 유형: 문제 해결 (How-to 가이드)

이 가이드를 따라 하면 화면을 고친 뒤 "정말 나아졌는가"를 에이전트의 자기 평가 없이 판정받을 수 있어요. 변경을 남길지 되돌릴지, 언제 다듬기를 멈출지를 기록에 근거해 정해요.

## 이럴 때 쓰세요

- 화면을 고친 에이전트가 매번 "더 좋아졌다"고만 보고할 때
- 게임 화면이 기준 화면 수준에 왔는지 알고 싶을 때
- 다듬기를 언제 멈춰야 할지 모를 때

자기가 고친 화면을 자기가 평가하면 "좋아졌다"가 나와요. 블라인드 심사는 조건 세 가지로 이 편향을 막아요: **같은 카메라**, **섞인 순서**, **맥락 없는 새 심사자**(`harness/skills/gf-verify/blind-judging.md`).

## 준비하기

- 비교할 스크린샷 두 장이 필요해요. 변경 판정이라면 수정 전 화면을 **변경하기 전에** 찍어 둬야 해요.
- 아래 명령의 `gf`는 게임 폴더를 지정한 함수예요.
- `gf judge` 명령은 무료예요. 심사자는 코딩 에이전트의 서브에이전트라서 에이전트 사용량이 조금 들어요.
- 심사자(`blind-judge`)는 gameforge 플러그인을 불러온 Claude Code 세션에서 쓸 수 있어요.

## 1. 같은 조건으로 두 화면 찍기

변경 전과 후를 같은 명령으로 찍으세요. 입력 스크립트, 시점, 시드가 같아야 바꾼 것만 다른 두 화면이 나와요.

```sh
gf engine capture --out captures/<작업>-before --script bot/<액션>.json --at 2.0 --seed 0
# ... 한 가지를 바꾼다 ...
gf engine capture --out captures/<작업>-after  --script bot/<액션>.json --at 2.0 --seed 0
```

## 2. 심사 쌍 만들기

목적에 맞는 방식을 고르세요.

| 방식 | `--a` | `--b` | 쓰는 때 |
|---|---|---|---|
| `change` | 수정 전 화면 | 수정 후 화면 | 변경 하나를 남길지 되돌릴지 정할 때. `--target <기준 화면>`을 함께 주면 심사자가 "목표에 더 가까운 쪽"을 골라요 |
| `target` | 기준 화면 | 게임 화면 | 게임 화면이 목표 수준에 왔는지 볼 때 |

```sh
gf judge pair --a captures/<작업>-before/shot_01_t2.00.png --b captures/<작업>-after/shot_01_t2.00.png \
  --mode change --id <쌍 이름> --series <묶음 이름>
```

```json
{"ok": true, "cost_usd": 0.0, "id": "sprite-01", "mode": "change", "series": "sprite", "judge_reads": "captures/judge/sprite-01", "judge_must_not_read": ".gf/judge", "folder": "captures/judge/sprite-01", "files": ["captures/judge/sprite-01/X.png", "captures/judge/sprite-01/Y.png", "captures/judge/sprite-01/rubric.md"], "size": [1280, 720], "aspect_mismatch": false}
```

- 명령이 두 화면을 `X.png`, `Y.png`로 무작위로 섞고, 원본 파일 이름이 넘어가지 않게 다시 인코딩해요. 어느 쪽이 무엇인지는 `.gf/judge/`에만 남아요.
- `--id`는 한 번 쓴 이름을 다시 쓸 수 없어요(`fog-01`, `fog-02`처럼 붙이세요).
- `--series`는 승패를 함께 세는 묶음이에요. 작업 방향 하나에 하나씩 두세요.
- `aspect_mismatch`가 `true`면 두 화면의 비율이 달라요. 그 쌍은 버리고 같은 `--size`로 다시 찍으세요.

## 3. 심사자 부르기

`blind-judge` 서브에이전트를 **매번 새로** 부르세요. 프롬프트에는 심사 폴더의 파일 경로만 넣으세요.

```
아래 파일만 읽고 rubric.md 의 형식대로 답하라.
<게임 폴더>/captures/judge/<쌍 이름>/rubric.md
<게임 폴더>/captures/judge/<쌍 이름>/X.png
<게임 폴더>/captures/judge/<쌍 이름>/Y.png
<게임 폴더>/captures/judge/<쌍 이름>/target.png      (있을 때만)
```

넣으면 안 되는 것: 무엇을 고쳤는지, 어느 쪽이 수정 후인지, 게임 설명, 기대하는 결과, 이전 심사 결과. 이런 말이 들어가면 그 심사는 무효예요. 다른 `--id`로 쌍을 다시 만드세요.

심사자는 `rubric.md`의 여섯 항목(가독성, 아트 방향 일관성, 조명과 색, 디테일 밀도 일관성, UI 판독성, AI 흔적 없음)을 X와 Y에 따로 1~10점으로 매기고 JSON 하나로 답해요.

메인 세션은 `.gf/judge/`를 읽지 않아요. 훅이 심사자가 심사 폴더 밖을 읽는 것도 막아요.

## 4. 결과 기록하기

심사자가 낸 JSON을 고치지 말고 그대로 넣으세요.

```sh
gf judge record --id <쌍 이름> --winner <X|Y|tie> --scores '{"X": {...}, "Y": {...}}' --notes "<심사자의 notes>"
```

```json
{"ok": true, "files": [".gf/judge/history.jsonl"], "cost_usd": 0.0, "id": "sprite-01", "series": "sprite", "mode": "change", "winner": "a", "winner_file": ".../captures/first/shot_01_t1.00.png", "counts": {"rounds": 1, "wins": 0, "ties": 0, "losses": 1}, "stop": {"met": false, "reason": "최근 1판 연속으로 수정 후가 이기지 못했다 (기준 2판).", "stop_after": 2}, "rules": ["..."], "keep_change": false}
```

이 예시는 형식을 보여 주려고 임의의 승자를 넣어 기록한 거예요. 실제 심사 결과가 아니에요. 명령이 `Y`를 정답 대응표로 풀어 `a`(수정 전)라고 알려 줬어요.

## 5. 결과 따르기

| 값 | 뜻 | 할 일 |
|---|---|---|
| `keep_change`가 `false` | 수정 전이 이겼어요 | 변경을 되돌리세요 |
| `keep_change`가 `true` | 수정 후가 이기거나 비겼어요 | 변경을 남기세요 |
| `stop.met`이 `true` | 멈춤 조건을 채웠어요 | 그 방향은 그만 다듬고 다음 작업으로 가세요 |

멈춤 조건은 방식마다 달라요. `target` 방식은 게임 화면이 목표를 2번 이기면, `change` 방식은 최근 2판 연속으로 수정 후가 이기지 못하면 끝이에요. 기준 횟수는 `--stop-after`로 바꿔요.

지켜야 할 규칙 세 가지예요.

1. 변경은 심사에서 이기거나 비겼을 때만 남겨요. "그래도 내 생각엔 낫다"로 남기지 마세요. 사용자가 직접 보고 남기라고 하면 남겨요.
2. 목표 그림에 없다는 이유만으로 게임 화면의 요소를 지우지 마세요. 심사에서 이기려고 UI나 적을 빼면 화면은 목표와 비슷해지고 게임은 나빠져요.
3. 같은 쌍을 원하는 결과가 나올 때까지 다시 심사하지 마세요.

심사자의 `notes`에서 고칠 점 **하나**를 골라 다음 변경으로 삼으세요.

## 결과 확인하기

묶음의 승패를 확인하세요. 사용자에게 보여 줄 근거예요.

```sh
gf judge history --series <묶음 이름>
```

실제 기록의 예시는 `games/cat-angler/.gf/judge/history.jsonl`이에요. 기준 화면 대 게임 화면 심사에서 기준 화면이 이긴 판마다 심사자의 지적("물속이 한 톤의 청록", "갈매기와 모자 겹침")이 남아 있고, 그 지적이 다음 변경이 됐어요.

## 알아 둘 한계

- 심사는 정지 화면만 봐요. 움직임, 조작감, 소리, 재미는 사람이 판정해요.
- 엄격한 기준에서는 좋은 화면도 5~6점이에요. 점수가 아니라 승패와 이유를 쓰세요.
- 중요한 판정(단계 승인 전, 큰 변경)은 심사자를 두 번 따로 불러서, 결과가 갈리면 `tie`로 기록하세요.

## 더 보기

- 세 가지 검증 가운데 이 심사의 자리: [세 가지 검증의 역할](../explanations/three-checks.md)
- 원문: `harness/skills/gf-verify/blind-judging.md`, `harness/agents/blind-judge.md`
