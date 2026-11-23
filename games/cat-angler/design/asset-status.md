# 에셋 상태 (2026-11-23 그림·소리 제작)

`design/asset-spec.md` 의 항목별 상태다. 완료 = 규격 경로에 있고 팔레트 24색·반투명 없음 검사를 통과했다. 약함 = 쓸 수는 있으나 눈에 띄는 흠이 있다. 소리는 측정만 했고 아무도 듣지 않았다.

만든 방법은 `assets/raw/_tools/` 의 스크립트에 그대로 남아 있다(`gfx.py` 공용, `cat_*.py`, `sea_*.py`, `land_*.py`, `ui_*.py`, `story_build.py`, `audio_*.sh`). 원본은 `assets/raw/`, 확인용 모음판은 `captures/assets/`.

## 캐릭터 `assets/game/chars/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `cat_idle` 4, `cat_walk` 6, `cat_pick` 3, `cat_sit_fish` 4, `cat_reel` 4, `cat_strain` 4, `cat_cheer` 4, `cat_sad` 2, `cat.json` | 완료 | 기준 스프라이트 한 장을 참조로 자세 시트 3장을 편집 생성, 숨쉬기·깜박임·떨림·뛰기는 픽셀 이동. 캔버스 80×60(규격 48×56 과 다름) |
| 〃 `cat_reel` 의 뒤로 젖힌 두 프레임 | 약함 | 얼굴이 다른 프레임보다 흐리다. 그 자세만 다시 생성하면 된다 |
| 〃 꼬리 흔들림, 귀 움찔 | 없음 | 아트 디렉션의 "꼬리가 느리게 흔들린다"는 프레임에 없다. 꼬리만 다른 자세 2장을 편집 생성해 대기 동작에 넣으면 된다 |
| `turtle_idle` 4, `turtle_walk` 4, `turtle_bow` 2 | 약함 | 컷신의 별주부 디자인과 맞췄다. 44px 에서 등딱지와 얼굴이 조금 뭉개진다. 더 단순한 형태로 다시 생성 |
| `king_idle` 4, `king_better` 4 | 완료 | 방석 위에 똬리를 튼 청록 용. `better` 프레임에서 가는 수염이 점으로 끊긴다 |
| `keeper_bait`(너구리), `keeper_market`(수달), `keeper_yard`(비버), `keeper_tackle`(왜가리) `idle` 4 | 완료 | 고양이와 같은 비율·외곽선 |
| 〃 `talk` 2 | 약함 | 머리가 1px 까딱일 뿐 입이 움직이지 않는다. 주인마다 입 벌린 프레임 한 장을 편집 생성 |

## 초상화 `assets/game/portraits/` (96×96)

| 항목 | 상태 | 메모 |
|---|---|---|
| `cat`, `turtle`, `king`, `keeper_bait`, `keeper_market`, `keeper_yard`, `keeper_tackle` | 완료 | 스프라이트를 참조로 생성해 같은 디자인이다. `turtle` 은 전신 그림에서 잘랐다 |

## 배 `assets/game/boats/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `boat1` 119×33, `boat2` 168×134, `boat3` 224×137, 각 `.json` | 완료 | 돛과 선실까지 그려 2·3단계는 규격보다 높다. `seat`·`waterline` 은 그림을 보고 정한 값이고 게임 화면에서 1·3단계만 확인했다. `boat2` 의 자리는 게임에서 확인하지 못했다 |

## 물고기 `assets/game/fish/`

| 항목 | 상태 | 메모 |
|---|---|---|
| 13종 `<id>_swim` 4프레임, `<id>_card.png` 96×64 | 완료 | 헤엄은 꼬리 쪽 열을 위아래로 미는 절차적 프레임. 크기는 규격보다 조금 크다(spec 끝 절) |
| 〃 `anchovy`, `scad` | 약함 | 작고 옅어서 밝은 물색에서 눈에 덜 띈다. 외곽선이 얇다. 더 짙은 등 색으로 다시 생성 |
| 〃 `hairtail`, `oarfish` | 약함 | 몸이 굽은 자세로 생성돼 꼬리 흔들림이 어색하다. 곧게 편 자세로 다시 생성 |
| `legend_swim`, `legend_shadow_swim`, `legend_card` | 완료 | 실루엣은 남보라 몸에 푸른 테두리(검은색은 심해 물색에 묻혔다) |

## 바다 `assets/game/sea/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `sky_shallow/open/deep` 640×200 | 완료 | 색 띠와 물결 경계를 계산으로 그렸다 |
| `far_shallow/open/deep` | 완료 | 생성 후 640×160 으로 줄이고 좌우를 뒤집어 붙였다(1280 너비). 얕은 바다는 외곽선을 빼고 얼룩을 지웠다. 뒤집어 붙인 것이라 가운데가 대칭이다 |
| `mid_shallow/open/deep` 640×88 | 약함 | 소나무 바위섬의 아랫부분이 수면 문양에 가려 나무가 떠 보인다. 섬을 더 높게 그리거나 코드에서 문양 뒤가 아니라 위로 올린다 |
| `under_shallow/open/deep` 640×360 | 완료 | 색 띠 + 빛줄기, 계산으로 그렸다. 빛줄기 끝이 조금 딱 끊긴다 |
| `bed_shallow/open/deep` | 완료 | 생성 후 64 높이 띠로 줄이고 좌우를 뒤집어 붙였다. 게임에서는 얕은 바다와 심해만 확인 |
| `surface_pattern.png` 64×32 | 완료 | 반원을 겹친 물결 문양, 계산으로 그렸다. 이음매 없음 |
| `wave_crest.png` 64×30 | 완료 | 생성 |
| `reef` 240×79, `wreck` 257×132, `ruin_1~3`, `pavilion` 192×140, `island_far` 319×107 | 완료 | `reef`·`wreck`·`ruin`·`island_far` 는 게임 화면에서 확인하지 못했다 |
| `pier.png` 321×117, `pier.json` | 완료 | 마을의 부두와 같은 그림. 비스듬히 본 시점이다 |
| `school_small/mid/big` 4프레임, `vortex` 4프레임 | 약함 | 계산으로 찍은 점선 고리와 튀는 물고기. 기능은 하지만 그린 그림만큼 예쁘지 않다. 물거품 시트를 생성해 바꾸면 된다 |
| `bird` 4프레임 | 완료 | 생성한 세 자세로 날갯짓 |
| `crate.png` | 약함 | 22px 에서 형태가 뭉개진다. 더 단순한 상자로 다시 생성 |
| `bottle.png`, `hook.png` | 완료 | |
| `bait_herb/bug/berry/legend.png` 8×8 | 완료 | 손으로 찍은 점 |
| `splash` 6, `bubble` 4, `sparkle` 4 | 완료 | 계산으로 그린 효과 |

## 장소 `assets/game/places/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `town.png` 1600×360, `town.json`, `town_fg.png` | 완료 | 건물 4채·배경·바닥·소품·부두를 따로 생성해 조립. 문 위치는 최종 그림에서 쟀다 |
| `in_bait`, `in_market`, `in_yard`, `in_tackle` + `.json` | 약함 | 방이 캐릭터에 비해 크고 원근이 조금 있다. `in_market` 진열대 높이 46(규격 80 이상), `in_yard` 설계도 판 98×64. 정면 시점으로 다시 생성하면 된다 |
| `forage.png` 960×360, `forage.json` | 완료 | 재료 자리는 모랫길 위에 뒀다(풀숲 안에서는 24px 재료가 묻혔다) |
| `island.png`, `island.json` | 완료 | 꽃 자리는 언덕 꼭대기가 아니라 걷는 줄 위다 |
| `title.png` | 완료 | 배 없는 바다 배경(게임이 배와 고양이를 그린다) |

## 아이템 `assets/game/items/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `herb`, `bug`, `berry` 아이콘과 `_plant`, 미끼 4종, `coin`, `rod1~3`, `rod1_wall~rod3_wall` | 완료 | `herb`, `bait_legend` 는 밝은 배경에서 외곽선이 얇다 |
| `flower.png` / `flower_plant.png` | 약함 | 아이콘은 다섯 잎 꽃, 땅에 난 모습은 초승달 모양 꽃이라 서로 다르다. 한쪽을 다시 생성 |

## UI `assets/game/ui/`

| 항목 | 상태 | 메모 |
|---|---|---|
| `panel`, `button`, `button_focus`, `slot`, `slot_focus`, `gauge_frame`, `gauge_fill`, `tension_frame`, `tension_fill` | 완료 | 생성한 틀을 크기에 맞춰 자르고 가장자리를 고르게 다듬었다. 모서리 물결 장식은 8px 에서 뭉개져 계산으로 다시 그렸다. 포커스 판은 색만 바꾼 것 |
| `bubble.png` | 약함 | 패널에서 만든 것이라 말풍선 꼬리가 없다 |
| `depth_ruler.png` | 약함 | 코드로 그린 눈금 띠다. 대나무나 밧줄 자 모양으로 생성해 바꾼다 |
| `icon_durability` | 약함 | 7px 높이의 배 모양이라 잘 안 읽힌다 |
| `icon_hold`, `icon_coin`, `icon_anchor`, `icon_bait`, `arrow` | 완료 | |
| `codex_book.png`, `codex_book.json` | 완료 | 쪽 자리는 그림에서 눈으로 쟀다 |
| `logo.png` 342×129 | 약함 | Galmuri11-Bold 를 4배로 찍고 테두리와 물결 띠, 고양이 머리를 붙였다. 글자는 정확하지만 밋밋하다. 뒤에 장식 판을 생성해 깔면 나아진다 |

## 글꼴 `assets/game/fonts/`

| 항목 | 상태 | 메모 |
|---|---|---|
| Galmuri v2.40.4 (`Galmuri11`, `Galmuri11-Bold`, `Galmuri9`, `Galmuri14`) | 완료 | SIL OFL 1.1. 출처와 날짜는 `SOURCE.md`, 허가서는 `Galmuri-LICENSE.txt`. 현대 한글 11,172자 포함 |

## 소리 `assets/game/audio/`

| 항목 | 상태 | 메모 |
|---|---|---|
| 효과음 23개 | 완료(측정만) | 전부 최대 −3 dB, 앞 무음 0.2ms 이하. `pick` 은 평균 −32 dB 로 거의 안 들릴 수 있다 |
| 음악 9곡 | 완료(측정만) | 28~38초, `gf post audio-loop` 로 이음매 처리, 이음매 검사 통과. `fight`, `sea_open` 은 통과했지만 이음매 수치가 가장 높으니 먼저 들어 본다. −12~−18 LUFS 라 게임에서 8~10 dB 낮춰 튼다 |

## 컷신 `assets/game/cutscenes/`

다른 작업자의 범위다. 여기서는 만들지 않았다.

## 확인한 것과 못 한 것

- `assets/game/` 의 PNG 195장 전부 팔레트 24색 안이고 반투명 픽셀이 없다(직접 센 값).
- `gf check assets` 는 실패한다. 코드가 `boats/boat1.png` 처럼 `assets/game/` 를 뺀 경로로 적어서 검사기가 못 찾는 것이고, 파일은 모두 있다. 코드나 검사기 쪽에서 맞춰야 한다.
- `gf check audio` 는 코드에서 참조를 0개로 읽는다(경로를 조합해 만들기 때문). 파일별 측정은 따로 했다.
- 게임 화면으로 본 것: 타이틀, 얕은 바다(항해·낚시), 심해 입구(항해·낚시). 먼바다, 마을, 실내, 채집지, 섬, 도감은 게임 안에서 보지 못했다.
- 블라인드 심사(새 맥락의 심사자): 그레이박스 대 새 화면은 새 화면 승(`sea-art-02`). 목표 그림 대 게임 화면은 목표 승(`sea-art-01`). 지적: 물고기가 작고 옅다, 물속이 단조롭다, 산의 질감이 캐릭터와 따로 논다. 그 뒤 물고기를 키우고 물색 단계를 늘리고 산의 얼룩을 지웠으나 다시 심사하지는 않았다.
