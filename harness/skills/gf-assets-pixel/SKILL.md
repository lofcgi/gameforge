---
name: gf-assets-pixel
description: 픽셀 아트 스프라이트, 도트, 타일셋, 픽셀 캐릭터 걷기 애니메이션을 만들어 달라거나 "픽셀이 뭉개진다/흐리다/크기가 안 맞는다"를 고쳐 달라는 요청에는, 직접 그리거나(SVG, Pillow, 코드) 생성 명령을 바로 부르기 전에 먼저 이 스킬을 쓴다. gameforge 의 assets 단계, 픽셀 아트 스타일(style=pixel): 단색 배경에 생성 → 크로마 → 격자 맞춤(진짜 1x 픽셀) → 공용 팔레트 → 1x 를 밝은·어두운 배경에서 검사하는 순서로 스프라이트·타일·픽셀 애니메이션을 만든다.
---

# 픽셀 에셋: 모델은 픽셀 아트를 그리지 못한다, 후처리가 만든다

이미지 모델의 "픽셀 아트"는 픽셀 아트처럼 보이는 고해상도 그림이다. 실측: 512px 로 받은 그림의 격자가 5.12px(정수가 아님), 색이 22,180개, "32x32"를 요청해도 100x100 칸으로 나왔다. 그대로 게임에 넣으면 흐리고 크기가 서로 안 맞는다. 생성물은 **원본**이고, 아래 사슬을 거친 것만 게임에 들어간다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 준비

`design/art-direction.md` 의 기준 해상도, 캐릭터 크기(예: 32x32), 색 수, 그리고 `design/palette.json` 을 확인한다. 팔레트가 없으면 `gf-look` 4절대로 만든다. 만들 에셋 목록을 brief 에서 뽑아 사용자에게 보여 주고(이름, 크기, 프레임 수) 가장 눈에 띄는 것 **하나**로 사슬 전체를 먼저 통과시킨다. 그 결과를 사용자가 승인한 뒤에 나머지를 만든다.

## 사슬 (정지 스프라이트)

```sh
# 1. 단색 배경에 생성. 배경색은 그림에 없는 색으로: 보통 마젠타 #FF00FF, 그림에 분홍·보라가 있으면 초록 #00FF00
$GF gen edit "a new game sprite in the art style of the reference image: <대상>, pixel art, chunky pixels, limited <N> colour palette, hard pixel edges, dark outline, side view, single subject centered, flat solid pure magenta #FF00FF background, no shadow, no ground, no text" \
  --image design/look/frame.png --aspect 1:1 --resolution 0.5K --out assets/raw/pix --name <이름>

# 2. 배경 제거 (픽셀용: 알파를 0/255 로만)
$GF post chroma assets/raw/pix/<이름>.png --key auto --hard --out assets/raw/keyed

# 3. 대상만 잘라(--trim) 정한 세로 크기의 1x 로 줄인다 (모델은 요청한 크기를 지키지 않는다)
$GF post pixel-snap assets/raw/keyed/<이름>.png --trim --height 24 --out assets/raw/pixel

# 4. 공용 팔레트를 입힌다 → 게임용 폴더로
$GF post palette apply assets/raw/pixel/<이름>.png --palette design/palette.json --out assets/game/sprites

# 5. 검사: pixel_art 가 true 여야 한다. 밝은·어두운 배경에 올린 확인 이미지를 만든다
$GF post inspect assets/game/sprites/<이름>.png --check captures/inspect/<이름>.png --check-scale 8
```

- 1단계: 참조 이미지를 주려면 `gen edit --image` 를 쓴다. 기본 `image.concept` 모델은 이미지 입력을 받지 않아 `gen image --ref` 는 실패한다. 참조 없이 만들 때만 `$GF gen image "<프롬프트>" --aspect 1:1 --resolution 0.5K --out assets/raw/pix --name <이름>`.
- 2단계의 `--key auto` 는 테두리 색을 배경으로 본다. 결과의 `key` 가 의도한 배경색과 다르면 `--key '#FF00FF'` 로 직접 준다.
- 3단계: 생성 그림에서 대상은 화면의 일부(실측 절반쯤)만 차지한다. `--trim` 이 보이는 부분만 자르고 `--height` 가 그 세로를 art-direction 의 크기로 맞춘다(가로는 비율대로). 결과의 `cell`(원본 몇 px 이 1칸인지)과 `size` 를 적어 둔다. 애니메이션 프레임에 같은 `cell` 을 쓴다.
- 화면을 꽉 채우는 타일은 `--trim` 없이 `--size 32x32` 로 고정한다. `--size` 는 비율이 다르면 그림을 늘리므로 캐릭터·소품에는 쓰지 않는다. 아무것도 안 주면 격자를 자동 감지하는데, 실측으로 모델의 격자는 512px 에 100칸(칸 5.12px)이라 게임 해상도보다 훨씬 촘촘하고 신뢰도가 낮으면(0.25 미만) 실패한다.
- 확대 미리보기는 결과 폴더가 아니라 `captures/inspect/pixel/<결과 폴더 이름>/` 에 따로 생긴다(결과의 `previews`). 결과 폴더에는 1x 만 있으므로 다음 단계에 폴더째 넘겨도 된다.
- **캐릭터는 처음부터 단순하게 생성한다.** 주름·패널·명암 줄이 많은 그림은 24px 로 줄이면 얼룩이 된다(실측: 우주복의 회색 음영이 흰 몸통 위의 어두운 점들로 남았고, 걷기 시트 전체가 지저분해졌다). 통한 문구: `drawn as a very low resolution 24 pixel tall sprite, big flat colour areas with only one shadow tone, no small details, thick dark outline, very chunky huge pixels, limited 8 colour palette`.
- 팔레트는 채택한 그림들(정지 + 애니메이션 프레임)에서 함께 뽑는다. 그림을 바꾸면 `palette extract` 를 다시 하고 전부에 다시 입힌다. 다른 그림에서 온 색(실측: 선인장의 어두운 초록)이 엉뚱한 그림의 음영에 박히는지 확인 이미지에서 본다.
- **1x 에서 살아남는 형태로 생성한다.** 가는 가시·줄·작은 무늬는 14~24px 로 줄이면 사라지고 색도 팔레트의 어두운 색으로 뭉친다(실측: 가시덤불의 붉은 가시가 전부 갈색이 됐다). 굵은 덩어리, 뚜렷한 색 면으로 다시 생성한다.
- 팔레트 적용에 `--dither` 는 쓰지 않는다(작은 스프라이트에서 지저분해진다). 큰 배경에서만 고려한다.

## 눈으로 확인한다 (통과 기준)

1. `inspect` 가 `pixel_art: true` (색 수 한도 안, 반투명 없음, 확대 상태 아님). `reasons` 가 있으면 그 단계로 돌아간다.
2. 확인 이미지(`captures/inspect/<이름>.png`)를 Read 로 본다: 밝은 쪽과 어두운 쪽 **모두에서** 테두리에 배경색 물이 없고, 외곽선이 끊기지 않고, 형태가 읽힌다.
3. 1x 크기에서 무엇인지 알아볼 수 있다. 확대해야만 알아볼 수 있으면 형태를 단순하게 다시 생성한다.
4. 기준 화면 옆에 놓았을 때 같은 게임 것으로 보인다.

사용자에게 확인 이미지와 게임용 파일의 절대 경로를 준다. 통과한 프롬프트는 다음 생성부터 `--keep` 을 붙여 `.gf/prompts.jsonl` 에 남기고, 같은 종류는 그 문장을 바탕으로 만든다.

## 애니메이션

짧은 동작(걷기, 대기, 공격)은 영상 한 번으로 만든다. 순서는 `${CLAUDE_SKILL_DIR}/animation.md`. 요점: 스프라이트 영상 생성 → `post frames` → `post chroma --despill 5 --erode 2` → `post align` → `post loop` → **모든 프레임에 같은 `--cell`** 로 `post pixel-snap` → `post palette apply` → `post sheet`. 실측: 3초 영상에서 12프레임(1초) 걷기 반복을 얻었다.

## 게임에 넣고 확인한다

파일을 `assets/game/` 에 두고 게임 코드에서 등록한다(게임 폴더의 `AGENTS.md` "에셋" 절: Godot 은 `post sheet` 의 `.tres` 를 `SpriteSheet.from_frames` 로, 격자 시트는 `SpriteSheet.make_sprite` 로. web 은 `src/sprites.js` 의 `SHEETS` 에 `post sheet` 의 매니페스트를 `player: { manifest: "./assets/game/sprites/player_walk.json" }` 로, 정지 그림은 `IMAGES` 에). Godot 2D 템플릿은 `assets/game/sprites/player_walk.tres` 가 있으면 플레이어에 바로 쓴다. 한 종류를 넣을 때마다:

```sh
$GF check assets          # 참조한 파일이 있는지, assets/game 의 PNG 가 전부 진짜 픽셀 아트인지
$GF engine test
$GF engine capture --out captures/assets-<이름> --at 1,3
```

스크린샷을 Read 로 보고 게임 안에서 흐려지지 않는지(정수배 확대, nearest 필터), 크기가 다른 에셋과 맞는지 본다. 화면 품질 판정은 `gf-verify` 의 블라인드 심사(목표: `design/look/frame.png`)로 한다.

에셋·UI·오디오가 모두 들어가고 사용자가 화면을 승인하면 `gf-verify` 의 승인 절차로 단계를 넘긴다.
