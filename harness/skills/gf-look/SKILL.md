---
name: gf-look
description: 게임의 룩, 아트 스타일, 목업, 컨셉 화면, 아트 디렉션을 정하려 하거나 stage 가 look 이고 레퍼런스 선택이 끝났을 때는, 이미지를 생성하기 전에 먼저 이 스킬을 쓴다. gameforge 의 look 단계 뒷부분: 고른 레퍼런스의 특성으로 기준 화면(목업) 후보를 생성하고, 사용자가 하나를 고르면 design/look/ 에 고정하고 design/art-direction.md(팔레트, 선, 조명, 카메라 거리, 픽셀 밀도, UI, do/don't)를 쓴다. 이후 모든 에셋 생성과 블라인드 심사의 목표가 된다.
---

# look: 목표 화면 한 장을 고정한다

고정하지 않으면 만들 때마다 그림이 달라지고 어디서 본 듯한 평균으로 모인다. 여기서 고른 화면이 이후 모든 생성의 참조 이미지이자 심사의 목표다.

## 명령

`$GF` = `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/tools" gf --project "<게임 폴더 절대 경로>"`.
공통 규약: `${CLAUDE_PLUGIN_ROOT}/skills/gf-start/conventions.md` (아직 안 읽었으면 먼저 읽는다).

## 준비

`design/brief.md`, `references/picked/analysis.md`, `references/picked/traits.json` 을 읽는다. 고른 레퍼런스가 없으면 `gf-reference` 를 먼저 한다. 사용자가 레퍼런스 없이 말로만 가겠다고 하면 그 설명으로 진행하되 후보를 더 넓게 뽑는다.

## 1. 기준 화면 후보를 만든다

**실제 게임 화면처럼** 만든다: brief 의 카메라, 화면 비율, 주인공이 화면에서 차지하는 크기, UI 자리까지. 예쁜 일러스트가 아니라 "이 게임을 하는 중의 한 프레임"이어야 그레이박스·에셋·심사의 기준으로 쓸 수 있다.

프롬프트는 영어로, analysis.md 의 특성을 문장으로 풀어 쓴다(작품 이름을 넣지 않는다). 고른 레퍼런스 가운데 **서로 다른 출처의 2~4장**을 입력 이미지로 주고 각각에서 무엇만 가져올지 적는다.

```sh
$GF gen edit "<프롬프트: 장르와 카메라, 화면 구성, 그리고 'take only the palette from image 1, only the lighting from image 2, ...'>" \
  --image references/picked/<a> --image references/picked/<b> \
  --aspect 16:9 --resolution 0.5K --count 3 --out design/look/candidates --name look-a --dry-run
```

`--dry-run` 으로 추정 비용을 본 뒤 같은 명령에서 `--dry-run` 만 빼고 실행한다. 방향이 다른 프롬프트 2~3개(예: 더 어둡게 / 더 단순하게 / 카메라 더 멀리)로 모두 6~9장을 만든다. 레퍼런스 없이 갈 때는 `$GF gen image "<프롬프트>" --aspect 16:9 --resolution 0.5K --count 3 --out design/look/candidates --name look-a` 를 쓴다.

스타일별 주의:

- `pixel`: 이미지 모델은 진짜 픽셀 아트를 그리지 못한다(실측: 512px 에 5.12px 격자). 기준 화면은 "픽셀 아트처럼 보이는 그림"으로 받아들이고, 색 수와 기준 해상도는 art-direction.md 에 숫자로 정한다.
- `3d-code`: 코드로 그릴 수 있는 형태(단순한 도형, 평면 색, 안개, 그라디언트 하늘)인지 본다. 손으로 칠한 세부가 많은 화면은 목표로 삼지 않는다.
- `3d-gen`: 인물·소품이 화면에서 작게 보이는 카메라 거리로 잡는다.

## 2. 고르게 한다

```sh
$GF post contact design/look/candidates --out design/look/candidates.png --columns 3
```

모음판을 Read 로 보고 절대 경로를 준다. 각 후보를 한 줄씩 설명하고(무엇이 다른지) 번호로 고르게 한다. "3번인데 조명은 5번처럼" 같은 답이면 그 둘을 입력으로 한 번 더 `gen edit` 한다. 세 바퀴를 돌아도 못 고르면 레퍼런스가 엇갈린 것이다. `gf-reference` 로 돌아가 다시 고른다.

고른 한 장을 `design/look/frame.png` 로 복사한다. 필요하면 같은 룩의 다른 장면(다른 시간대, 메뉴 화면, 위험 상황)을 `frame.png` 를 입력으로 2~4장 더 만들어 `design/look/` 에 둔다. 이때부터는 명령에 `--keep` 을 붙인다. 프롬프트가 `.gf/prompts.jsonl` 에 남아 이후 에셋 생성의 바탕이 된다. 후보를 뽑는 동안에는 붙이지 않는다(채택 전의 프롬프트가 섞인다).

## 3. (선택) 룩 영상

움직임·카메라·분위기가 핵심인 게임이면 기준 화면에서 짧은 영상을 만든다. 추정 비용이 `null` 로 나오므로 직접 준다(실측 4초 480p 약 $0.9). 실행 전에 금액을 사용자에게 말한다.

```sh
$GF gen video design/look/frame.png --role video.look --prompt "<카메라와 움직임>" \
  --duration 4 --resolution 480p --no-audio --estimate-usd 0.9 --max-usd 1.5 --out design/look --name look-motion
```

## 4. `design/art-direction.md` 를 쓴다

`${CLAUDE_SKILL_DIR}/art-direction-template.md` 의 틀을 따른다. 형용사가 아니라 **지킬 수 있는 규칙과 숫자**로 쓴다. 팔레트는 기준 화면에서 뽑는다:

```sh
$GF post palette extract design/look/frame.png --colors 16 --out design/palette.json
```

(`design/palette.json` 과 같은 이름의 PNG 견본이 생긴다. 픽셀 스타일에서는 이 팔레트를 모든 스프라이트에 적용한다.)

## 5. 승인받는다

사용자에게 `design/look/frame.png`, 팔레트 견본, `design/art-direction.md` 의 절대 경로를 주고 규칙 다섯 줄을 요약한다. "이 화면을 목표로 만들겠습니다. 맞습니까?" 사용자가 승인하면:

```sh
$GF check evidence
$GF state approve --note "<룩 한 줄>"
```

다음은 `gf-graybox` 다. 그레이박스에서는 이 룩을 입히지 않는다.
