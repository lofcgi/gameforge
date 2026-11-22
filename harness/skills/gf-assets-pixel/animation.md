# 픽셀 애니메이션: 영상 한 번 → 프레임 → 시트

프레임을 한 장씩 생성하면 장마다 캐릭터가 달라진다. 정지 스프라이트 한 장을 첫 프레임으로 영상을 한 번 만들고, 스크립트로 나눈다. 실측: 3초 영상에서 37프레임, 약 $0.34.

## 1. 원본 영상

첫 프레임은 **후처리 전의 큰 원본**(단색 배경 그대로)을 쓴다. 1x 로 줄인 것을 넣으면 영상 모델이 뭉갠다.

```sh
$GF gen video assets/raw/pix/<이름>.png --role video.sprite \
  --prompt "the character walks in place, side view, static camera, background stays flat solid magenta, no camera movement, no new objects" \
  --duration 3 --out assets/raw/video --name <이름>-walk --dry-run
```

추정 비용을 보고 `--dry-run` 을 빼고 실행한다. 길이는 모델이 받는 가장 짧은 값(기본 모델은 3초)으로 한다. 마지막 프레임을 지정하는 옵션은 쓰지 않는다(기본 `video.sprite` 모델이 받지 않아 실패한다). 반복 구간은 아래 `post loop` 로 찾는다.

걷기는 프롬프트에 **제자리 걷기, 옆모습, 다리가 번갈아 크게 움직인다, 화면 가운데에 머문다**를 모두 적는다. 실측으로 통한 문장: `side view walk cycle animation loop of <캐릭터> walking in place toward the right, legs alternate stepping with clear big steps, knees lifting, body bobs up and down slightly, stays in the center of the frame and does not travel, static locked camera, background stays flat solid magenta`. 프레임 모음판에서 다리가 거의 안 움직이면 그렇다고 사용자에게 말하고 문장을 한 번만 고쳐 다시 만든다.

## 2. 프레임 → 배경 제거 → 정렬 → 반복 구간

```sh
$GF post frames assets/raw/video/<이름>-walk.mp4 --fps 12 --out assets/raw/frames/<이름>-walk
$GF post chroma assets/raw/frames/<이름>-walk --key auto --despill 5 --erode 2 --hard --out assets/raw/keyed/<이름>-walk
$GF post align assets/raw/keyed/<이름>-walk --anchor bbox --out assets/raw/aligned/<이름>-walk
$GF post loop assets/raw/aligned/<이름>-walk --min-length 6 --max-length 12 --out assets/raw/loop/<이름>-walk
```

- 영상 프레임은 압축 때문에 가장자리에 배경색이 번진다. 정지 그림의 기본값으로는 남는다. `--despill 5 --erode 2` 가 실측으로 필요했던 값이다.
- `align` 은 발 기준선과 가로 기준점을 맞추고 캔버스를 통일한다. 팔을 크게 휘두르는 동작이면 `--anchor mass` 가 덜 흔들린다.
- `loop` 는 가장 매끄럽게 이어지는 구간을 골라 낸다. 결과의 구간과 점수를 보고, 고른 프레임들을 모음판으로 확인한다:
  `$GF post contact assets/raw/loop/<이름>-walk --out captures/inspect/<이름>-walk-loop.png --columns 8`

## 3. 픽셀로 만든다 (전 프레임 같은 격자, 같은 팔레트)

```sh
$GF post pixel-snap assets/raw/loop/<이름>-walk --cell <칸 크기> --out assets/raw/pixel/<이름>-walk
```

`--cell` 은 **모든 프레임에 똑같이** 준다. 프레임마다 자동 감지하거나 `--trim --height` 를 쓰면 프레임마다 크기가 달라진다. 값은 정지 스프라이트의 `cell` 에 해상도 비율을 곱한다: `정지 cell × (영상 가로 ÷ 정지 원본 가로)`. 실측: 정지 원본 512px 에서 cell 13.58 → 960px 영상에서 `--cell 25.47`, 프레임 21x25. 확대 미리보기는 `captures/inspect/pixel/` 에 따로 생기므로 결과 폴더를 그대로 다음 단계에 넘긴다.

```sh
$GF post palette apply assets/raw/pixel/<이름>-walk --palette design/palette.json --out assets/raw/paletted/<이름>-walk
$GF post sheet assets/raw/paletted/<이름>-walk --name <이름>_walk --fps 12 --out assets/game/sprites
```

`sheet` 는 시트 PNG, JSON 매니페스트(프레임 좌표, fps, loop), Godot `SpriteFrames`(.tres)를 만든다. 반복하지 않는 동작(공격, 사망)은 `--no-loop`.

## 4. 확인

```sh
$GF post inspect assets/game/sprites/<이름>_walk.png
```

- `pixel_art: true`.
- 모음판에서 프레임 사이에 캐릭터의 색·크기·장비가 바뀌지 않는다. 바뀌는 프레임은 뺀다(영상 모델이 흔히 소품을 바꾼다).
- Godot 2D 템플릿은 시트를 `--name player_walk --out assets/game/sprites` 로 만들면 플레이어가 바로 쓴다(`SpriteSheet.from_frames`: 첫 프레임이 대기 자세). 그림은 오른쪽을 보게 만든다.
- 게임에 넣고 `$GF engine capture --out captures/anim-<이름> --script bot/<걷는 입력>.json --at 0.5,0.6,0.7,0.8` 로 연속 화면을 찍어 발이 미끄러지지 않는지, 기준선이 튀지 않는지 본다.
- 움직임의 느낌은 사람이 본다. `$GF engine run` 으로 사용자에게 보여 주고 묻는다.

두 번 다시 만들어도 어색하면 동작을 단순하게 바꾼다(프레임 수를 줄인다, 2~4프레임 손그림식 동작으로 간다). 같은 영상을 계속 다시 뽑지 않는다.

## 여러 캐릭터를 한 번에

캐릭터 여러 명을 격자(예: 5x2)로 한 장에 놓고 영상을 한 번 만든 뒤 칸별로 자른다.

```sh
$GF post frames <영상> --grid 5x2 --names a,b,c,d,e,f,g,h,i,j --inset 4 --fps 12 --out assets/raw/frames/crowd
```

칸별 폴더가 생긴다. 이후는 캐릭터마다 위와 같다. 캐릭터당 비용이 열 배쯤 싸지지만 해상도도 그만큼 줄어든다. 게임에서 작게 보이는 캐릭터에만 쓴다.
