# 레퍼런스 모으고 고르기

> 문서 유형: 문제 해결 (How-to 가이드)

이 가이드를 따라 하면 여러 출처에서 모은 참고 이미지 가운데 사용자가 고른 것의 **공통 특성**을 숫자와 글로 정리할 수 있어요. 결과물은 "어느 게임처럼"이 아니라 "이 팔레트 + 이 구도 + 이 픽셀 밀도" 같은 특성 묶음이에요.

## 이럴 때 쓰세요

- 기준 화면을 만들기 전에 화면의 방향을 정해야 할 때
- "이런 느낌으로"를 말로 설명하기 어려울 때
- 참고한 작품 하나를 그대로 따라 그리게 될까 걱정될 때

레퍼런스 없이 이미지를 생성하면 어디서 본 듯한 평균적인 그림이 나와요. 반대로 한 작품만 참고하면 그 작품을 베끼게 돼요. 이 절차는 여러 출처에서 특성만 가져와서 두 문제를 함께 피해요.

## 준비하기

- 게임 프로젝트가 있어야 해요. 없으면 [튜토리얼](../tutorials/first-game.md) 3단계로 만드세요.
- 아래 명령의 `gf`는 게임 폴더를 지정한 함수예요: `gf() { uv run -q --project harness/tools gf --project <게임 폴더> "$@"; }`
- 이 가이드의 모든 명령은 무료예요. 생성 호출이 없어요.
- Pinterest나 ArtStation처럼 자동 수집을 막는 사이트에서 모으려면 에이전트가 Claude in Chrome 도구로 사용자의 Chrome을 써야 해요. 그 Chrome에 사용자가 직접 로그인해 둬야 해요.

## 1. 이미지 모으기

서로 다른 출처 3곳 이상에서 15~40장을 모으세요. 출처에 따라 명령이 달라요.

```sh
gf ref steam <appid 또는 상점 주소> --max 8                       # Steam 공개 스크린샷
gf ref frames <영상 주소 또는 파일> --count 12 --note "<볼 것>"      # 영상에서 같은 간격으로 프레임 뽑기
gf ref add <파일 또는 이미지 주소> --note "<볼 것>" --tags "<쉼표 구분>"
gf ref add <이미지 주소> --source-url <실려 있던 페이지 주소> --title "<작가·작품>" --note "<볼 것>"
gf ref add <파일> --anti --note "<왜 아닌지>"                      # 피할 예시
```

- `--note`에는 그 이미지에서 **무엇을 볼지** 적으세요(조명만, 팔레트, 캐릭터 비율). 나중에 특성을 뽑는 기준이 돼요.
- 게임 한 편에서는 8장 이하로 받고 다른 출처를 섞으세요.
- `--source-url`을 주면 메타 파일에 출처 페이지가 남아요. `--title`은 작가나 작품 이름을 알 때만 적고, 지어내지 마세요.

파일 두 장을 넣으면 이런 결과가 나와요.

```json
{"ok": true, "files": ["references/inbox/manual-e3b4b1498b6b.png", "references/inbox/manual-341aa224b989.png"], "cost_usd": 0.0, "added": ["manual-e3b4b1498b6b.png", "manual-341aa224b989.png"], "duplicates": []}
```

자동 수집을 막는 사이트는 에이전트가 사용자의 Chrome에서 검색 결과를 **읽기만** 하고, 이미지 주소를 `gf ref add`에 넘겨요. 저장, 팔로우, 좋아요는 하지 않아요. 로그인 화면이 나오면 멈추고 사용자가 직접 로그인해요(`harness/skills/gf-reference/SKILL.md`).

## 2. 모음판 만들기

모은 이미지에 번호를 붙여 한 장으로 만드세요.

```sh
gf ref sheet
```

```json
{"ok": true, "files": ["references/sheets/inbox-01.png"], "cost_usd": 0.0, "index": "references/sheets/inbox-index.json", "count": 3, "pages": 1}
```

`references/sheets/inbox-01.png`를 사용자에게 보여 주고 번호로 고르게 하세요. 두 가지를 물어요: "이런 느낌(각각 무엇이 좋은지 한마디)"과 "이런 느낌은 아님".

## 3. 고른 것 기록하기

메모가 같은 것끼리 묶어 실행하세요. 번호는 방금 만든 모음판의 번호예요.

```sh
gf ref pick 1 2 --note "팔레트"
gf ref pick 3 --anti --note "질감"
```

```json
{"ok": true, "files": ["references/picked/manual-7759296883be.png"], "cost_usd": 0.0, "index": "references/picked/picks.json", "reference": 2, "anti": 1, "warnings": []}
```

`warnings`를 꼭 확인하세요. 고른 것의 대부분이 한 작품이나 한 사이트에서 왔으면 쏠림 경고가 들어 있어요. 경고가 뜨면 그대로 진행하지 말고, 그 작품에서 가져오려던 특성을 말로 적은 뒤 다른 출처에서 같은 특성을 가진 이미지를 더 모으세요. 경고를 없애려고 `--title`을 꾸며 넣지 마세요.

잘못 골랐으면 `gf ref unpick <번호>`로 빼세요.

## 4. 측정하고 글로 정리하기

고른 묶음의 색과 밝기를 재세요.

```sh
gf ref traits --colors 6
```

```json
{"ok": true, "files": ["references/picked/traits.json", "references/picked/traits-palette.png"], "cost_usd": 0.0, "difference": {"brightness": -0.0041, "contrast": -0.0054, "saturation": 0.016, "warmth": 0.0512, "edge_density": 0.0457}, "reference": {"count": 2, "palette": ["#1e2f45", "..."], "temperature": "cool", ...}, "anti": {"count": 1, ...}}
```

`difference`는 고른 것과 피할 예시의 차이예요. 이 예시에서는 고른 쪽의 윤곽 밀도(`edge_density`)가 더 높아요.

그다음 `references/picked/analysis.md`를 쓰세요. 측정값은 근거로만 쓰고, 고른 이미지를 직접 보고 쓰세요. 네 가지를 담아요.

| 항목 | 쓰는 내용 |
|---|---|
| 공통 특성 | 팔레트, 명암 구조, 선, 형태, 카메라 거리, 주인공의 크기, UI 분위기. 어느 이미지에서 봤는지 번호와 함께 |
| 피할 것 | 측정 차이와 눈으로 본 차이 |
| 출처별로 가져오는 것 | "A에서는 색만, B에서는 카메라만". 한 출처에서 세 가지 넘게 가져오면 쏠린 거예요 |
| 가져오지 않는 것 | 고유 캐릭터, 로고, UI 배치, 레벨 구성 |

## 결과 확인하기

아래가 모두 맞으면 끝난 거예요.

- `gf ref status`의 `picked.warnings`가 비어 있거나, 남은 경고를 왜 받아들였는지 `analysis.md`에 적었어요.
- `references/picked/traits.json`, `traits-palette.png`, `analysis.md`가 있어요.
- 사용자가 `analysis.md`의 공통 특성을 읽고 "맞다"고 했어요.

실제 예시는 `games/cat-angler/references/picked/analysis.md`예요. 고른 25장 중 20장이 pinterest.com이어서 쏠림 경고가 떴고, 문서는 그 경고를 받아들인 이유를 적었어요.

## 더 보기

- 고른 특성으로 기준 화면을 만드는 절차: `harness/skills/gf-look/SKILL.md`
- 수집한 이미지를 공개 저장소에 올리지 않는 이유: [공개 저장소에 안전하게 올리기](publish-safely.md)
- 원문: `harness/skills/gf-reference/SKILL.md`
