---
name: gf-assets-2d
description: 픽셀이 아닌 2D 일러스트풍 스프라이트, 배경, 소품, 캐릭터 걷기·공격 애니메이션, 스프라이트 시트를 만들어 달라거나 "그림마다 스타일이 다르다/테두리에 색이 남는다"를 고쳐 달라는 요청에는, 직접 그리거나 생성 명령을 바로 부르기 전에 먼저 이 스킬을 쓴다. gameforge 의 assets 단계, 2D 스타일(style=2d): 기준 화면을 참조로 캐릭터·소품·배경을 생성하고 배경을 제거해 게임에 넣으며, 스프라이트 애니메이션은 영상 한 번 → 프레임 → 크로마 → 정렬 → 반복 구간 → 시트로 만든다.
---

# 2D 에셋: 기준 화면을 참조로, 한 종류씩

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 준비

**화면 설정을 먼저 확인한다.** 2D 템플릿의 좌표는 레벨 단위(320x180)이고, `gf init --style 2d` 는 화면을 창 해상도로 부드럽게 그리며 그림을 **단위당 4픽셀**로 놓는다(Godot: `project.godot` 의 `window/stretch/mode="canvas_items"`, `gameforge/art/pixels_per_unit=4` / web: `src/view.js` 의 `ppu: 4, smooth: true`). 그래서 그림의 픽셀 크기 = 화면에서의 단위 크기 × 4 다(26 단위 높이 캐릭터 → 104px, 32 단위 타일 → 128px. 1280x720 창에서 1:1). 설정이 픽셀용(`viewport`, `ppu: 1`)으로 남아 있으면 그림이 320x180 으로 뭉개지므로 게임 폴더 `AGENTS.md` 의 표대로 먼저 바꾼다.

`design/art-direction.md`(선, 조명 방향, 스프라이트 기준 높이, 공통 문구)와 `.gf/prompts.jsonl`(채택된 프롬프트)을 읽는다. brief 에서 에셋 목록(이름, 화면에서의 크기, 정지/애니메이션)을 뽑아 사용자에게 보여 준다. 화면에서 가장 큰 비중인 것 **하나**를 끝까지 만들어 게임 안 스크린샷으로 승인받은 뒤 나머지를 만든다.

## 정지 스프라이트 (캐릭터, 소품)

```sh
# 1. 기준 화면을 참조로, 그림에 없는 단색 배경에 생성 (초록 #00FF00 또는 마젠타 #FF00FF)
$GF gen edit "a new game sprite in the art style of the reference image: <대상>, <아트 디렉션 공통 문구>, full body, side view, single subject centered, flat solid pure green #00FF00 background, no shadow, no ground, no text" \
  --image design/look/frame.png --aspect 1:1 --resolution 1K --out assets/raw/2d --name <이름>

# 2. 배경 제거
$GF post chroma assets/raw/2d/<이름>.png --key auto --out assets/raw/keyed

# 3. 대상만 잘라(--trim) 화면에서 쓸 크기로 줄인다 (세로 px = 화면에서의 단위 높이 × 4. 알파가 보존된다)
$GF post resize assets/raw/keyed/<이름>.png --trim --height 104 --out assets/game/sprites

# 4. 검사 (밝은·어두운 배경에 올린 확인 이미지)
$GF post inspect assets/game/sprites/<이름>.png --check captures/inspect/<이름>.png
```

- 참조 이미지를 주려면 `gen edit --image` 를 쓴다(여러 번 줄 수 있다). 기본 `image.concept` 모델은 이미지 입력을 받지 않아 `gen image --ref` 는 실패한다. `gen image` 는 참조 없이 만들 때만 쓴다.
- 시험은 `--resolution 0.5K` 로 하고 방향이 맞으면 올린다. 여러 안이 필요하면 `--count 3`.
- 기존 그림의 일부만 고칠 때는 다시 생성하지 않고 `$GF gen edit "<바꿀 것만, keep everything else>" --image <원본> --out assets/raw/2d --name <이름>-v2` 를 쓴다. 같은 캐릭터의 다른 자세도 이렇게 만든다(원본을 `--image` 로).
- 단색 배경으로 받지 못한 그림(머리카락, 연기, 반투명)은 `$GF gen rembg <이미지> --estimate-usd 0.01 --out assets/raw/2d --name <이름>-cut` 을 쓴다(이 모델은 비용을 미리 계산할 수 없어 `--estimate-usd` 가 없으면 호출이 거부된다).
- 확인 이미지에서 테두리에 배경색이 남으면 `--despill` 과 `--erode` 를 올린다(기본 3, 1). 안쪽까지 깎이면 `--tolerance` 를 낮춘다.
- 생성 그림에서 대상은 화면의 일부만 차지한다(실측 1024px 중 세로 476~852px). **정지 그림에는 `--trim` 을 붙여야** `--height` 가 그림 전체가 아니라 대상의 세로가 된다. 그림마다 따로 실행한다(한 번에 넣으면 가장 큰 것 기준의 같은 배율이 되어 나머지가 작아진다).
- 바닥 타일은 배경 제거 없이 `$GF post resize assets/raw/2d/<타일>.png --inset <px> --height 128 --out assets/game/sprites`. 모델은 "이음매 없는 타일"에 테두리 선을 둘러 주곤 한다(실측 1024px 에 22px). `--inset` 으로 그만큼 잘라 내지 않으면 타일마다 세로줄이 보인다. 위쪽에만 풀·이끼가 있는 타일은 위 절반과 아래 절반을 따로 깐다(게임 폴더 `AGENTS.md` 의 `tiled`/`drawTiled`).
- `post resize` 는 `--height`/`--width`/`--fit 가로x세로`/`--scale` 중 하나를 받고, 여러 입력에는 **같은 배율**을 쓴다(가장 큰 입력 기준). 한 화면의 스프라이트는 같은 배율 규칙으로 줄인다. 원본(1K)을 그대로 넣고 엔진에서 크게 줄이면 가장자리가 지글거리고 메모리를 낭비한다. `--canvas 가로x세로` 는 결과를 캔버스 아래 가운데에 놓는다.

## 배경

배경은 투명 처리 없이 화면 비율로 만든다. 전경이 읽히도록 채도와 대비를 낮춘다(art-direction 의 전경/배경 분리 규칙).

```sh
$GF gen edit "a new game background in the art style of the reference image: <장소>, <공통 문구>, no characters, no UI, no text, low contrast, empty space in the lower middle for gameplay" \
  --image design/look/frame.png --aspect 16:9 --resolution 1K --out assets/game/backgrounds --name <이름>
```

스크롤 배경은 층(먼 산, 중간, 가까운 풀)을 따로 만들고 가까운 층만 단색 배경 → 크로마로 투명하게 한다.

## 애니메이션: 영상 한 번 → 시트

프레임을 한 장씩 생성하면 장마다 캐릭터가 달라진다. 정지 스프라이트 원본(단색 배경)을 첫 프레임으로 영상을 한 번 만든다. 실측: 3초에 37프레임, 약 $0.34.

```sh
$GF gen video assets/raw/2d/<이름>.png --role video.sprite \
  --prompt "the character walks in place, side view, static camera, background stays flat solid green, no camera movement" \
  --duration 3 --out assets/raw/video --name <이름>-walk --dry-run          # 비용 확인 후 --dry-run 을 빼고 실행
$GF post frames assets/raw/video/<이름>-walk.mp4 --fps 12 --out assets/raw/frames/<이름>-walk
$GF post chroma assets/raw/frames/<이름>-walk --key auto --despill 5 --erode 2 --out assets/raw/keyed/<이름>-walk
$GF post align assets/raw/keyed/<이름>-walk --anchor bbox --out assets/raw/aligned/<이름>-walk
$GF post loop assets/raw/aligned/<이름>-walk --min-length 6 --max-length 16 --out assets/raw/loop/<이름>-walk
$GF post contact assets/raw/loop/<이름>-walk --out captures/inspect/<이름>-walk-loop.png --columns 8
$GF post resize assets/raw/loop/<이름>-walk --height 104 --out assets/raw/resized/<이름>-walk     # 모든 프레임 같은 배율, 같은 캔버스. --trim 은 붙이지 않는다
$GF post sheet assets/raw/resized/<이름>-walk --name <이름>_walk --fps 12 --out assets/game/sprites
```

- **영상 프레임에는 `--despill 5 --erode 2`** 를 쓴다. 압축 때문에 가장자리에 배경색이 번져 정지 그림의 기본값으로는 초록 테두리가 남는다(실측).
- `align` 은 발 기준선과 가로 기준점을 맞추고 캔버스를 통일한다. 팔다리를 크게 움직이면 `--anchor mass`.
- 영상 모델은 걷기 시작하면서 자세를 바꾼다(실측: 정면에 가깝던 여우가 옆으로 돌아 꼬리가 반대쪽으로 갔다). 그래서 정지 스프라이트와 걷기 프레임을 섞어 쓰지 않고, 대기 자세도 걷기 시트의 첫 프레임을 쓴다(템플릿의 기본 동작).
- 프레임에는 `--trim` 을 쓰지 않는다. `align` 이 맞춘 발 기준선과 공통 캔버스가 깨진다. `--height` 는 캔버스 세로(= 가장 큰 프레임의 대상 높이 + 여백 1px)에 적용된다.
- 다리 사이처럼 배경이 좁게 끼는 곳은 움직임 번짐 때문에 배경색이 섞인 점이 한두 프레임 남을 수 있다(실측: 초록 배경, 부츠 사이). 시트를 밝은·어두운 배경에 올려 확대해 보고, 눈에 띄면 그 프레임을 뺀다.
- `loop` 가 고른 구간을 모음판으로 Read 해서 본다: 프레임 사이에 얼굴·옷·소품이 바뀌는 것, 발이 미끄러지는 것을 찾는다. 바뀌는 프레임은 빼고 다시 `sheet` 한다.
- `sheet` 는 PNG + JSON 매니페스트 + Godot `SpriteFrames`(.tres)를 만든다. 반복하지 않는 동작은 `--no-loop`. 영상 프레임은 크게 나온다(실측 778x765). 시트로 묶기 전에 `post resize` 로 줄인다(결과의 `uniform_canvas` 가 true 인지 본다). `--columns` 로 가로 폭을 정하고 프레임 수는 8~12장으로 한다.
- 여러 캐릭터를 한 영상에 격자로 놓고 `post frames --grid 5x2 --names a,b,... --inset 4` 로 칸별로 자르면 캐릭터당 비용이 크게 준다. 게임에서 작게 보이는 캐릭터에만 쓴다.
- 영상 생성으로 복잡한 동작(격투 콤보, 정밀한 손동작)을 얻으려 하지 않는다. 두 번 다시 만들어도 어색하면 동작을 단순하게 바꾸거나 코드 연출(흔들림, 스쿼시·스트레치, 파티클)로 대신한다.

## 게임에 넣고 확인한다

`assets/game/` 에 둔 것만 게임 코드가 참조한다. 등록 방법은 게임 폴더의 `AGENTS.md` "에셋" 절(Godot: `player_walk.tres` 는 자동, 정지 그림은 `SpriteSheet.standing`/`tiled` + `Graybox.dress`. web: `src/sprites.js` 의 `SHEETS`(매니페스트)·`IMAGES` + `drawStanding`/`drawTiled`). 그림을 직접 늘리거나 줄여 그리지 않는다. 크기가 안 맞으면 `post resize` 의 `--height` 를 고친다. 한 종류를 넣을 때마다:

```sh
$GF check assets
$GF engine test
$GF engine capture --out captures/assets-<이름> --at 1,3
```

스크린샷을 Read 로 보고 판단한다: 가장자리가 지글거리거나 계단지지 않는가(그렇다면 화면 설정이 픽셀용이다), 기준 화면과 같은 게임으로 보이는가, 선 굵기·조명 방향·디테일 밀도가 다른 에셋과 맞는가, 전경이 배경에서 분리되는가. 채택한 프롬프트는 다음 생성부터 `--keep` 으로 남긴다. 화면 품질은 `gf-verify` 의 블라인드 심사(목표: `design/look/frame.png`)로 판정하고, 움직임의 느낌은 `$GF engine run` 으로 사용자에게 보여 주고 묻는다.

에셋·UI(`gf-ui`)·오디오(`gf-audio`)가 모두 들어가고 사용자가 화면을 승인하면 `gf-verify` 의 승인 절차로 단계를 넘긴다.
