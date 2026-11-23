# gf 명령 모음

> 문서 유형: 참조

`gf`의 명령 그룹과 하위 명령을 한 표로 정리했어요. `gf`는 gameforge 하네스의 CLI예요. 생성, 후처리, 엔진 실행, 레퍼런스, 심사, 검사를 맡아요. 이 표는 2026-11-23에 `gf --help`와 각 그룹의 `--help` 출력을 대조해서 만들었어요. 옵션 전체는 `gf <그룹> <명령> --help`로 확인하세요.

## 부르는 형태

```sh
uv run -q --project <저장소>/harness/tools gf --project <게임 폴더> <그룹> <명령> [옵션]
```

- `--project <게임 폴더>`는 `gf` 바로 뒤, 그룹 앞에 와요. 생략하면 현재 폴더예요.
- 명령에 주는 상대 경로(입력과 출력 모두)는 현재 폴더가 아니라 **게임 폴더 기준**이에요.
- zsh에서는 변수 대신 함수로 줄이세요. 변수에 담으면 명령 전체를 파일 이름 하나로 읽어서 실패해요.

```sh
gf() { uv run -q --project harness/tools gf --project <게임 폴더> "$@"; }
```

## 출력 형식

| 결과 | 종료 코드 | 표준 출력의 마지막 줄 |
|---|---|---|
| 성공 | 0 | `{"ok": true, "files": [...], "cost_usd": 0.0, ...}` |
| 실패 | 0이 아님 | `{"ok": false, "error": "..."}` |

`files`는 그 명령이 만든 파일이고 게임 폴더 기준 경로예요.

## 명령 그룹

| 그룹 | 하위 명령 | 하는 일 | 비용 |
|---|---|---|---|
| (루트) | `init` | 템플릿으로 게임 프로젝트를 만들어요. `--engine {godot,web}`, `--dim {2d,3d}`, `--style {pixel,2d,3d-code,3d-gen}` 필수 | 무료 |
| (루트) | `doctor` | 필요한 도구와 `FAL_KEY`가 있는지 점검해요 | 무료 |
| `state` | `show`, `set`, `approve` | 단계 상태를 보고, 현재 단계를 승인해 다음 단계로 넘어가요 | 무료 |
| `fal` | `search`, `price`, `schema`, `run` | 모델 검색, 단가 조회, 입력 스키마 조회, 임의 모델 호출 | `run`만 유료 |
| `gen` | `image`, `edit`, `rembg`, `video`, `model3d`, `rig`, `sfx`, `tts`, `music` | 역할 이름으로 이미지, 영상, 3D 모델, 소리를 생성해요 | 유료 (`--dry-run`은 무료) |
| `post` | `chroma`, `pixel-snap`, `resize`, `palette extract`, `palette apply`, `frames`, `align`, `loop`, `audio-loop`, `sheet`, `contact`, `inspect` | 생성물을 후처리하고 숫자로 검사해요. 네트워크를 쓰지 않아요 | 무료 |
| `blender` | `info`, `clean`, `decimate`, `rescale`, `turntable`, `run` | 3D 모델을 정리하고 미리보기를 렌더해요 | 무료 |
| `engine` | `run`, `record`, `capture`, `bot`, `replay`, `perf`, `audio`, `test` | 게임을 실행하고, 스크린샷을 찍고, 플레이 봇을 돌리고, 입력을 기록·재생하고, 성능과 소리를 재요 | 무료 |
| `ref` | `steam`, `frames`, `add`, `sheet`, `pick`, `unpick`, `traits`, `status` | 레퍼런스를 모으고, 모음판을 만들고, 고르고, 측정해요 | 무료 |
| `judge` | `pair`, `record`, `history` | 블라인드 심사용 쌍을 만들고 결과를 기록해요 | 무료 |
| `check` | `evidence`, `assets`, `audio` | 단계 승인 근거, 에셋 참조, 소리 파일을 검사해요 | 무료 |

## 자주 쓰는 명령

### 실행과 확인 (`engine`)

| 명령 | 하는 일 | 결과가 남는 곳 |
|---|---|---|
| `gf engine test` | 스모크 테스트: 부팅, 브리지 계약, 첫 화면, 입력 반응, 콘솔 오류 | `captures/test/result.json` |
| `gf engine capture --out <폴더> --at 1,3 [--script <액션.json>]` | 지정한 시점의 실제 화면과 상태를 저장해요 | `<폴더>/shot_*.png`, `capture.json` |
| `gf engine bot --policy <파일 또는 goal\|random\|idle> [--require-goal]` | 플레이 봇이 실제 입력 경로로 플레이해요 | `captures/bot/<id>/` |
| `gf engine run [--record]` | 사람이 플레이하도록 게임을 띄워요. `--record`는 입력을 기록해요 | `captures/sessions/<id>.jsonl` |
| `gf engine replay <id>` | 기록한 입력을 재생하고 반응 없는 입력 후보를 보고해요 | `captures/replays/<id>/` |
| `gf engine perf --seconds 5 [--out <파일.json>]` | 프레임 시간, 드로우 콜, 메모리, 로딩 시간을 재요 | `--out`으로 지정한 파일 (예: `captures/perf/base.json`) |
| `gf engine audio [--expect 입력=소리]` | 실시간으로 돌리며 소리가 실제로 나는지 재요 | `captures/audio/result.json` |

### 픽셀 후처리 (`post`)

| 명령 | 하는 일 |
|---|---|
| `gf post chroma <입력> --key auto --hard --out <폴더>` | 단색 배경을 투명하게 빼요 |
| `gf post pixel-snap <입력> --trim --height <픽셀> --out <폴더>` | 격자에 맞춰 1배 픽셀 아트로 줄여요 |
| `gf post palette extract <입력> --colors <수> --out <팔레트.json>` | 그림에서 팔레트를 뽑아요 |
| `gf post palette apply <입력> --palette <팔레트.json> --out <폴더>` | 팔레트의 색으로만 칠해요 |
| `gf post inspect <입력> [--check <확인 이미지>]` | 크기, 투명도, 색 수, 픽셀 아트 여부를 보고해요 |
| `gf post sheet <입력> --name <이름> --fps <수> --out <폴더>` | 스프라이트 시트 PNG, JSON, Godot `.tres`를 만들어요 |
| `gf post audio-loop <입력> --out <파일.wav>` | 음악의 앞뒤 무음을 자르고 꼬리를 머리에 섞어요 |

### 생성 (`gen`) 공통 옵션

| 옵션 | 뜻 |
|---|---|
| `--dry-run` | 호출하지 않고 추정 비용과 보낼 인자만 보여 줘요 |
| `--max-usd <값>` | 추정 비용이 이 값을 넘으면 실행하지 않아요. 기본 한도는 호출당 $3이에요 |
| `--estimate-usd <값>` | 단가로 계산할 수 없는 모델에 대략의 비용을 알려 주고 한도와 비교하게 해요 |
| `--allow-unknown-cost` | 비용을 모르는 채로 호출해요(한도 확인 없음) |
| `--keep` | 채택한 프롬프트를 `.gf/prompts.jsonl`에 남겨요 |
| `--out <폴더>`, `--name <이름>` | 결과 폴더와 파일 이름 |

## 더 보기

- 단계마다 어떤 명령이 쓰이는지: [단계별 스킬과 산출물](stages-and-outputs.md)
- 생성 단가: [생성 비용표](costs.md)
- 직접 실행해 보기: [첫 게임 실행하고 캐릭터 넣기](../tutorials/first-game.md)
- 원문: `harness/AGENTS.md`의 "명령 규약"
