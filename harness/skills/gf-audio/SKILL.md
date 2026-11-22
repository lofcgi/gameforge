---
name: gf-audio
description: 게임에 효과음, SFX, 사운드, BGM, 음악, 음성, 대사, TTS 를 만들거나 넣어 달라는 요청, "소리가 안 난다/너무 크다/작다/안 어울린다"를 고쳐 달라는 요청에는, 코드를 고치거나 소리 파일을 구하기 전에 먼저 이 스킬을 쓴다. 소리 없는 빌드를 막을 때도 쓴다. gameforge 의 assets·polish 단계: 효과음·음성·배경음악을 생성해 게임에 넣고, 에이전트는 소리를 듣지 못하므로 길이·음량을 측정으로 확인하고 느낌은 사람에게 들려 묻는다.
---

# 오디오: 만들고, 재고, 사람이 듣는다

에이전트는 듣지 못한다. 할 수 있는 것은 ① 생성 ② 파일이 있고 소리가 나는지·길이와 음량이 맞는지 **측정** ③ 게임에서 재생 코드가 그 파일을 가리키는지 확인이다. 어울리는지, 거슬리는지는 **사람이 듣고** 판정한다. "소리 넣었습니다"라고 말하기 전에 측정값과 파일 경로를 함께 준다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 1. 소리 목록

brief 의 핵심 루프에서 **플레이어의 행동과 결과마다 소리 하나**를 뽑아 표로 사용자에게 보여 준다. 빠지면 가장 티 나는 순서: 주 행동(점프·발사·타격) → 맞음/죽음 → 획득 → 승리/패배 → UI 클릭 → 배경음악 → 환경음.

| 이름 | 언제 | 길이 | 느낌 (영어 프롬프트) |
|---|---|---|---|
| `jump` | 점프 순간 | 0.3초 | short soft whoosh, light, cartoon |

art-direction 의 분위기와 맞춘다(픽셀 게임 → chiptune/8-bit, 차분한 게임 → 부드럽고 낮은 음).

## 2. 생성

```sh
$GF gen sfx "<소리 설명, 영어>" --duration 0.5 --out assets/raw/audio --name <이름>
$GF gen sfx "<환경음 설명>" --duration 8 --loop --out assets/raw/audio --name <이름>       # 매끄럽게 반복
$GF gen music "<분위기, 악기, 빠르기, loopable>" --duration 30 --instrumental --out assets/raw/audio --name <이름> --dry-run
$GF gen tts "<대사>" --language <ISO 639-1> --out assets/raw/audio --name <이름>
```

- `--duration` 을 꼭 준다. 빼면 모델이 길이를 정해 비용을 추정할 수 없고, 그런 호출은 `--estimate-usd` 없이는 거부된다. 실측 단가: 효과음 초당 $0.002, 음악 분당 $0.6, 음성 1,000자당 $0.1.
- 음악은 `--dry-run` 으로 금액을 보고 실행한다. 30초짜리로 방향을 확인한 뒤 긴 곡을 만든다. 게임 음악은 `--instrumental` 로 보컬을 뺀다.
- 음성의 `--voice` 값은 추측하지 않는다. `$GF fal schema fal-ai/elevenlabs/tts/eleven-v3` 으로 받는 값을 확인한다.
- 특정 게임·곡·작곡가의 이름을 프롬프트에 넣지 않는다. 악기, 빠르기, 분위기로 설명한다.
- 같은 종류(타격음 3종)는 한 번에 변형을 만들어 번갈아 재생하면 덜 지루하다.

## 3. 측정한다

```sh
$GF check audio assets/raw/audio/<이름>.mp3 assets/raw/audio/<다른 것>.mp3
```

파일마다 `duration_s`, `mean_db`(평균 음량), `max_db`(최대 음량), `rms_db`, `lufs`, `clipped_runs`(파형이 잘린 곳), `dc_offset`, `lead_silence_ms`/`tail_silence_ms`(앞뒤 무음)가 나온다. 반복 재생할 파일(이름이 theme/music/bgm/loop/ambient 이거나 코드에서 `loop` 와 같은 줄에 있거나 `--loop <파일>` 로 준 것)은 `seam`(끝에서 처음으로 넘어가는 이음매)도 잰다. 고칠 만한 것은 `warnings` 에 모이고 `--strict` 를 주면 실패로 끝난다. 통과 기준:

| 볼 것 | 기준 | 어긋나면 |
|---|---|---|
| 소리가 있는가 | `max_db` 가 -60 dB 보다 크다 (이하면 명령이 실패한다) | 다시 생성 |
| 길이 | 요청한 길이와 비슷하다. 효과음은 1초 안쪽이 대부분 | `--duration` 을 고쳐 다시 생성 |
| 최대 음량 | -1 dB 이하 (0 dB 에 붙으면 찢어진다), -12 dB 보다는 크다 | 엔진에서 볼륨을 조정하거나 다시 생성 |
| 서로의 균형 | 효과음끼리 `mean_db` 차이가 6 dB 안쪽, 음악은 효과음보다 6~10 dB 낮게 재생 | 엔진의 재생 볼륨으로 맞춘다. 게임 안의 실제 균형은 4절의 `engine audio` 로 본다 |
| 잘림·치우침 | `clipped_runs` 0, `dc_offset` 0.01 이하 | 다시 생성 |
| 효과음 앞 무음 | `lead_silence_ms` 30 이하 (넘으면 누른 뒤 늦게 들린다) | 앞 무음을 자른다 |
| 반복 이음매 | `seam.seamless` 가 true: 앞뒤 무음 합 10ms 이하, 이음매의 파형 꺾임이 주변의 4배 이하, 처음·끝 0.5초가 곡보다 12 dB 넘게 작지 않음, 이음매의 음색 차이가 곡 안 변화의 1.5배 이하 | `post audio-loop` 로 다듬는다 |

생성한 음악은 대개 이음매 검사에 걸린다(실측: 데모 음악 4곡 모두 앞뒤 무음 11~26ms, 한 곡은 끝이 18 dB 잦아들었다). 반복할 소리는 다듬어서 **.wav** 로 넣는다:

```sh
$GF post audio-loop assets/raw/audio/theme.mp3 --out assets/game/audio/theme.wav [--fade 0.5]
```

앞뒤 무음을 자르고 꼬리를 머리와 겹쳐 섞는다(겹침 길이는 `--fade`, 없으면 꼬리와 머리의 박자가 가장 잘 맞는 0.25~2초를 고른다. 곡은 그만큼 짧아진다). 결과의 `before`/`after` 가 같은 이음매 측정이고, 쓴 파일이 기준을 넘으면 명령이 실패한다. mp3 로 쓰면 압축이 이음매를 흐트러뜨려 실패할 수 있다(실측: 4곡 중 1곡). 숫자는 "튀는 곳이 없다"까지만 말한다. 박자가 맞게 이어지는지, 듣기 좋은지는 사람이 들어야 안다.

앞뒤의 무음이나 형식 변환이 필요하면 ffmpeg 를 직접 쓴다(예: 앞 무음 제거 `ffmpeg -i in.mp3 -af silenceremove=start_periods=1:start_threshold=-50dB out.ogg`). 바꾼 뒤 다시 측정한다.

## 4. 게임에 넣는다

통과한 파일만 `assets/game/audio/` 로 옮기고 게임 코드에서 재생한다.

- Godot: 템플릿의 `Sound.player(경로, 볼륨 dB, 반복 여부, 버스)`(`scripts/sound.gd`)로 `AudioStreamPlayer` 를 만든다. 음악과 효과음을 다른 버스로 나눈다(godot-3d 템플릿에는 `default_bus_layout.tres` 가 있다). 반복 설정은 형식마다 달라(.wav 는 `loop_mode`, mp3·ogg 는 `loop`) 이 도우미가 처리한다. 음악이 재생 중일 때 게임이 끝나면 Godot 이 종료 정리 중에 "resources still in use at exit" 를 낼 수 있는데, 하네스는 이것을 오류가 아니라 경고로 센다.
- web: **브라우저는 사용자의 첫 입력 전에는 소리를 내지 않는다.** 그 전에 `AudioContext` 를 만들거나 `play()` 를 부르면 콘솔 경고·오류가 나서 `engine test` 가 실패한다. web-2d 템플릿은 `src/audio.js` 가 이것을 처리한다: `SOUNDS` 에 `jump: { url: "./assets/game/audio/jump.mp3", volume: 0.4 }`, `theme: { url, volume: 0.25, loop: true }` 처럼 등록하면 파일은 미리 받아 두고 첫 키·클릭에서 오디오를 열어, 규칙의 사건(`jump`, `death`, `goal`)과 같은 이름의 소리를 내고 `theme` 을 반복 재생한다. 자동 실행(Playwright 의 키 입력)도 같은 경로로 풀린다. web-3d 는 같은 방식으로 직접 만든다.
- Godot 2D 템플릿의 점프는 `Player.jumped` 시그널에 건다.
- 재생은 게임 규칙의 **결과**로만 한다. 소리 재생이 게임 상태를 바꾸지 않게 한다(재생·봇의 결정성이 깨진다).

```sh
$GF check audio --require     # 게임 코드가 가리키는 오디오가 전부 있고 소리가 나는가. 하나도 없으면 실패
$GF engine test               # 없는 파일(404, 로드 실패)은 콘솔 오류로 잡힌다
```

`check audio` 는 코드에 적힌 경로와 파일만 본다. 게임을 돌렸을 때 소리가 **실제로 나는지**는 실행해서 잰다:

```sh
$GF engine audio --expect jump=jump --expect goal=goal     # 결과: captures/audio/result.json
```

게임을 실시간으로 돌리며(기본으로 `bot/clear.json` 을 입력한다) 브리지가 엔진 안의 최종 신호를 잰다. 게임 코드에 세는 변수를 넣을 필요가 없다. 읽을 것:

| 결과 | 뜻 |
|---|---|
| `checks.audible` | 실행 중 신호가 -60 dB 를 넘었다 (`peak_db`, `rms_db`) |
| `checks.silent_before_input`, `no_autoplay_warnings` (web) | 첫 입력 전에는 `AudioContext` 도 소리도 없고, 자동 재생 경고가 없다 |
| `sounds`, `responses` | 어떤 파일이 몇 번 시작됐는지, 입력·사건(`goal`, `death`)마다 0.25초 안에 시작된 소리와 그 앞뒤의 피크. `--expect <액션이나 사건>=<파일 이름 일부>` 로 준 짝이 없으면 실패한다 |
| `loops`, `checks.loop_continues` | 반복 소리가 제 길이를 넘겨서도 나는지(`continues`), 반복 지점에서 신호가 끊긴 길이(`quiet_ms_at_wrap`). 곡이 길면 `--seconds` 나 `--max-seconds` 를 곡 길이보다 길게 준다 |
| `gaps` | 반복 소리가 나는 동안 20ms 넘게 끊긴 곳 |

효과음이 음악보다 얼마나 큰지는 `responses` 의 `peak_db_after − peak_db_before` 로 본다(6~12 dB 가 무난하다). 이 측정은 스피커가 아니라 엔진 안의 신호다(Godot: 마스터 버스, web: `destination` 직전). 기기 음량, 출력 장치, 실제로 귀에 들리는지는 모른다. 사용자에게 보고할 때 "실행 중 신호를 쟀다, 듣지는 못했다"고 말한다.

## 5. 사람이 듣는다

사용자에게 `assets/game/audio/` 의 절대 경로와 측정표를 주고, 게임을 직접 켜서 듣게 한다.

```sh
$GF engine run
```

묻는다: ① 빠진 소리가 있나 ② 거슬리거나 너무 큰 것 ③ 음악이 게임과 어울리나, 30초 뒤에도 괜찮나. 답을 `design/playtest-notes.md` 에 적고 하나씩 고친다. 사용자가 듣고 괜찮다고 하기 전에는 오디오를 끝났다고 하지 않는다.

polish·publish 단계의 승인은 `check audio --require` 와 같은 검사를 통과해야 한다(`warnings` 와 `engine audio` 는 승인을 막지 않는다. 그래도 둘 다 돌려 결과를 사용자에게 보여 준다). 일부러 소리 없는 게임이면 사용자에게 확인받은 뒤 `.gf/config.toml` 에 `[check]` 절의 `allow_silent = true` 를 적는다. 사용자 확인 없이 적지 않는다.
