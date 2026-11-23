# 듣지 않고 소리 검증하기

> 문서 유형: 문제 해결 (How-to 가이드)

이 가이드를 따라 하면 소리를 듣지 못하는 에이전트가 "소리 파일이 멀쩡한가", "음악이 끊기지 않고 반복되는가", "게임을 돌렸을 때 실제로 소리가 나는가"를 숫자로 확인할 수 있어요. 귀로만 판정할 수 있는 것은 따로 남겨 사람에게 넘겨요.

## 이럴 때 쓰세요

- 에이전트가 소리를 넣었다고 하는데 정말 나는지 확인할 방법이 없을 때
- 배경음악이 반복될 때마다 "뚝" 끊길 때
- 효과음이 음악에 묻히거나 너무 클 때

에이전트는 소리를 듣지 못해요. 그래서 측정할 수 있는 것과 없는 것을 먼저 나눠요.

| 측정으로 확인하는 것 | 사람이 들어야 하는 것 |
|---|---|
| 파일의 길이, 음량, 잘림, 앞뒤 무음 | 듣기 좋은가, 게임과 어울리는가 |
| 음악 이음매의 무음과 파형 꺾임 | 이음매에서 박자가 자연스러운가 |
| 실행 중 엔진이 내보내는 신호의 크기 | 스피커로 실제로 들리는가 |
| 입력 직후 어떤 소리가 시작됐는가 | 그 소리의 느낌이 맞는가 |

## 준비하기

- ffmpeg가 설치돼 있어야 해요.
- 게임 코드가 소리 파일을 `assets/game/audio/` 경로로 가리키고 있어야 해요.
- 아래 명령의 `gf`는 게임 폴더를 지정한 함수예요.
- 이 가이드의 명령은 모두 무료예요. 소리를 새로 생성하는 `gf gen sfx`와 `gf gen music`만 유료예요(효과음 초당 약 $0.002, 음악 분당 약 $0.6. `harness/README.md`).
- **무료로 연습하기**: `demo-check/pixel-godot` 폴더를 다른 곳에 복사해 게임 폴더로 지정하면 그대로 따라 할 수 있어요. 아래 예시 출력은 그렇게 실행한 결과예요.

## 1. 소리 파일 재기

게임 코드가 가리키는 소리 파일이 모두 있고 소리가 들어 있는지 검사하세요.

```sh
gf check audio --require
```

파일마다 이런 값이 나와요.

```json
{"file": "assets/game/audio/jump.mp3", "exists": true, "duration_s": 0.48, "mean_db": -19.2, "max_db": -1.2, "clipped_runs": 0, "dc_offset": 0.0003, "lead_silence_ms": 0.0, "tail_silence_ms": 243.2, "lufs": -15.6, "loop": false}
```

| 값 | 보는 것 |
|---|---|
| `exists`, `duration_s` | 파일이 있고 길이가 0이 아닌가 |
| `max_db`, `clipped_runs` | 소리가 넘쳐서 잘린 곳이 있는가(0이어야 해요) |
| `lead_silence_ms` | 앞에 무음이 길면 입력보다 소리가 늦게 나요 |
| `mean_db` | 효과음끼리 차이가 6 dB 안쪽이면 고른 편이에요 |

결과 끝의 `problems`와 `warnings`가 비어 있는지 확인하세요.

## 2. 음악의 이음매 재기

반복 재생할 음악은 끝과 처음이 만나는 이음매를 재야 해요. 생성한 원본 파일을 `--loop`로 지정해 검사하세요.

```sh
gf check audio --loop assets/raw/audio/theme.mp3 assets/raw/audio/theme.mp3
```

검증용 데모의 원본 음악은 이렇게 나와요.

```json
{"file": "assets/raw/audio/theme.mp3", "duration_s": 10.03, "lead_silence_ms": 7.6, "tail_silence_ms": 3.7, "loop": true, "seam": {"edge_silence_ms": 11.2, "click_db": -99.0, "spectral_ratio": 0.84, "seamless": false, "problems": ["앞뒤 무음 11.2ms (기준 10.0ms 이하): 반복마다 끊긴다"]}}
```

`seam.seamless`가 `false`예요. 앞뒤 무음을 합치면 11.2ms라서 반복할 때마다 짧게 끊겨요. 하네스 검증에서 데모 음악 네 곡이 모두 이 검사에 걸렸어요(`demo-check/EVIDENCE.md` H절).

## 3. 이음매 다듬기

`gf post audio-loop`는 앞뒤 무음을 자르고 곡의 꼬리를 머리에 겹쳐 섞어요. 결과는 `.wav`로 쓰세요. mp3는 압축이 이음매를 다시 흐트러뜨릴 수 있어요.

```sh
gf post audio-loop assets/raw/audio/theme.mp3 --out assets/game/audio/theme.wav
```

```json
{"ok": true, "files": ["assets/game/audio/theme.wav"], "cost_usd": 0.0, "trimmed_lead_ms": 7.6, "trimmed_tail_ms": 3.7, "fade_s": 1.52, "beat_match": 0.782, "duration_s": 8.501, "source_duration_s": 10.032, "before": {"edge_silence_ms": 11.2, "seamless": false, "...": "..."}, "after": {"edge_silence_ms": 0.0, "click_db": -61.1, "seamless": true, "problems": []}}
```

`after.seamless`가 `true`로 바뀌었어요. 1.52초를 겹쳤기 때문에 곡이 10.03초에서 8.50초로 짧아졌어요. `beat_match`는 겹친 구간의 박자가 얼마나 맞는지예요. 이 값이 낮으면(다른 데모에서는 0.39) 이음매가 숫자로는 통과해도 박자가 어긋나게 들릴 수 있으니 사람에게 들어 보라고 하세요.

## 4. 실행 중에 소리가 나는지 재기

파일이 멀쩡해도 게임이 그 파일을 재생하지 않을 수 있어요. 게임을 실시간으로 돌리면서 엔진이 내보내는 신호를 재세요. `--expect 입력=소리`는 "이 입력 직후에 이 소리가 시작돼야 한다"는 조건이에요.

```sh
gf engine audio --script bot/clear.json --expect jump=jump
```

```json
{"ok": true, "files": ["captures/audio/result.json"], "measured": "엔진 안의 최종 신호 (Godot: 마스터 버스, web: destination 직전). 스피커 소리가 아니다", "seconds": 10.32, "peak_db": -6.8, "rms_db": -25.6, "sounds": {"assets/game/audio/theme.wav": {"starts": 1, "loop": true, "length_s": 8.501}, "assets/game/audio/jump.mp3": {"starts": 3, "loop": false, "length_s": 0.48}, "assets/game/audio/goal.mp3": {"starts": 1, "loop": false, "length_s": 1.2}}, "responses": [{"t": 2.417, "kind": "input", "name": "jump", "sounds": ["assets/game/audio/jump.mp3"], "peak_db_before": -16.2, "peak_db_after": -9.0}, "..."], "loops": [{"sound": "assets/game/audio/theme.wav", "wraps": 1, "continues": true, "quiet_ms_at_wrap": 0.0}], "checks": {"audible": "ok", "loop_continues": "ok", "...": "..."}}
```

읽는 법이에요.

- `sounds`: 점프 소리가 3번 시작됐어요. 스크립트의 점프 입력도 3번이에요.
- `responses`: 점프 입력 직후 신호의 피크가 −16.2 dB에서 −9.0 dB로 올라갔어요. 효과음이 음악 위로 들릴 만큼 커요.
- `loops`: 음악이 반복 지점을 한 번 넘었고(`wraps: 1`) 계속 재생됐고, 그 지점의 무음은 0.0ms예요.
- `measured`: 이 값은 엔진 안의 신호예요. **스피커에서 난 소리가 아니에요.**

## 결과 확인하기

- `gf check audio --require`의 `problems`와 `warnings`가 비어 있어요.
- 반복하는 음악의 `seam.seamless`가 `true`예요.
- `gf engine audio`의 `checks`가 모두 `ok`이고, 기대한 입력마다 소리가 시작됐어요.
- 보고에 "소리는 측정만 했고 사람이 듣지 않았다"를 적었어요.

마지막 줄이 가장 중요해요. 저장소의 문서들은 소리를 다룰 때마다 이 문장을 적어요(`harness/README.md`, `games/cat-angler/SCREENSHOTS.md`, `games/cat-angler/design/asset-status.md`). cat-angler의 음악 다섯 곡은 박이 또렷하지 않아 이음매에서 박자가 밀리는지 잴 수 없었고, 상태 문서는 그 칸에 "모름. 들어 봐야 안다"고 적었어요.

## 사람에게 넘기기

측정이 끝나면 `gf engine run`으로 게임을 띄워 사용자에게 들려주고, 무엇을 들어 달라는지 좁혀서 물으세요.

- 음악이 반복되는 순간이 거슬리는가
- 가장 자주 나는 효과음이 거슬리는가
- 효과음이 음악에 묻히는가

## 더 보기

- 검증을 셋으로 나눈 이유: [세 가지 검증의 역할](../explanations/three-checks.md)
- 원문: `harness/skills/gf-audio/SKILL.md`
