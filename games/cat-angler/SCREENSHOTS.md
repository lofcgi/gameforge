# 화면 모음 (2026-11-23, 다듬기 뒤)

그림·소리·컷신·화면 구조를 다시 만든 뒤 다듬기까지 마친 실제 게임 화면이다. 전부 `gf engine capture` 로 실행 중인 게임에서 찍었다. 기준 해상도 640×360. 다시 찍으려면 `zsh bot/capture_all.sh`.

목표로 삼은 기준 화면은 [`design/look/target.png`](design/look/target.png) 이다.

## 기준 화면과 게임 화면 비교

![기준 화면과 게임 화면](captures/assets/sea_vs_target.png)

왼쪽이 기준 화면, 오른쪽이 닻을 내린 직후의 게임 화면이다. 바다 화면은 세계를 2배로 당겨 그린다(고양이·배·물고기가 기준 화면의 비율이 된다. HUD 와 글자는 1배).

맥락 없는 심사 에이전트(매번 새 맥락, 두 그림과 채점표만 본다)에게 일곱 번 물었다. 앞의 다섯 번은 기준 화면이 이겼고(물속이 한 톤이다, 잔고기가 얼룩 같다, 타일 이음매 등 지적을 차례로 고쳤다), 마지막 두 번(`polish-06`, `polish-07`)은 게임 화면이 근소하게 이겼다. 기록은 `.gf/judge/history.jsonl`, 심사에 쓴 그림은 `captures/judge_src/`.

## 타이틀과 여는 컷신

![타이틀](captures/screens/title/shot_01_t1.00.png)

여는 컷신은 10컷, 닫는 컷신은 3컷이다. 아래는 컷마다 시작·중간·끝을 찍은 모음이다.

| | |
|---|---|
| ![1 심해로](captures/cutscenes/intro_01.png) | ![2 용궁](captures/cutscenes/intro_02.png) |
| ![3 병든 용왕](captures/cutscenes/intro_03.png) | ![4 전설의 물고기](captures/cutscenes/intro_04.png) |
| ![5 별주부가 나섬](captures/cutscenes/intro_05.png) | ![6 뭍으로](captures/cutscenes/intro_06.png) |
| ![7 부두의 고양이](captures/cutscenes/intro_07.png) | ![8 거래](captures/cutscenes/intro_08.png) |
| ![9 맞잡은 손](captures/cutscenes/intro_09.png) | ![10 출항](captures/cutscenes/intro_10.png) |
| ![닫는 1](captures/cutscenes/ending_01.png) | ![닫는 2](captures/cutscenes/ending_02.png) |
| ![닫는 3](captures/cutscenes/ending_03.png) | ![전설의 그림자, 0.3초 간격](captures/cutscenes/proof_legend.png) |

걷는 프레임 확인: [여는 3컷](captures/cutscenes/proof_walk_intro03.png), [닫는 1컷](captures/cutscenes/proof_walk_ending01.png). 용왕의 숨과 깜빡임: [proof_king](captures/cutscenes/proof_king.png).

## 항구 마을과 채집지

![마을](captures/screens/town/shot_01_t1.10.png)
![채집지](captures/screens/forage/shot_02_t3.40.png)

## 가게 (각각 따로 들어가는 실내 화면)

| 미끼 공방 | 어시장 |
|---|---|
| ![미끼 공방](captures/screens/in_bait/shot_03_t2.00.png) | ![어시장](captures/screens/in_market/shot_03_t2.00.png) |

| 조선소 | 낚시 가게 |
|---|---|
| ![조선소](captures/screens/in_yard/shot_02_t0.90.png) | ![낚시 가게](captures/screens/in_tackle/shot_03_t2.00.png) |

## 바다

| 얕은 바다 | 먼바다 | 심해 입구 |
|---|---|---|
| ![얕은 바다](captures/screens/sea_shallow/shot_02_t6.00.png) | ![먼바다](captures/screens/sea_open/shot_02_t6.00.png) | ![심해 입구](captures/screens/sea_deep/shot_02_t6.00.png) |

닻을 내린 직후와 줄다리기(카메라가 미끼를 따라 내려간다):

![닻을 내린 직후](captures/screens/anchored/shot_01_t4.40.png)
![낚시](captures/screens/fishing/shot_03_t6.00.png)

구간마다의 바닥:

| 얕은 바다 30m | 먼바다 80m | 심해 입구 150m |
|---|---|---|
| ![얕은 바다 바닥](captures/screens/seabed_shallow/shot_01_t5.00.png) | ![먼바다 바닥](captures/screens/seabed_open/shot_01_t13.00.png) | ![심해 바닥](captures/screens/seabed_deep/shot_01_t14.50.png) |

| 암초 | 난파선 |
|---|---|
| ![암초](captures/screens/reef/shot_01_t6.00.png) | ![난파선](captures/screens/wreck_site/shot_01_t13.00.png) |

타이틀부터 닫는 컷신까지 봇이 한 번에 깬 실행의 화면은 `captures/bot/` 의 가장 최근 `full_run-*` 폴더에 60초 간격으로 있다.

## 섬과 도감

![섬](captures/screens/island/shot_02_t3.30.png)
![도감](captures/screens/codex/shot_01_t1.50.png)

## 에셋

![고양이 대기 동작(꼬리·귀·깜박임)](captures/assets/cat_idle_polish.png)
![물고기 12종](captures/assets/fish_all.png)
![갈치·산갈치 헤엄](captures/assets/longfish_swim.png)
![가게 주인의 말하는 동작](captures/assets/keepers_talk.png)
![바닥 장식](captures/assets/sea_deco.png)
![전설 어종](captures/assets/fish_legend.png)
![배 3단계](captures/assets/boats.png)

## 아직 약한 것

- 바다만 2배다. 마을·채집지·섬·실내는 1배라 화면을 오갈 때 고양이 크기가 두 배로 달라진다. 실내는 방이 캐릭터에 비해 커서 주인과 고양이가 작다(2배로 올리려면 가게 네 곳의 자리와 거래 화면을 다시 잡아야 해서 하지 않았다).
- 바다의 세계는 2배 픽셀, HUD 와 글자는 1배 픽셀이라 한 화면에 픽셀 굵기가 두 가지다.
- 한 화면에 보이는 깊이는 약 22m 다. 기준 화면처럼 수면에서 용궁까지 한눈에 들어오지는 않는다(먼 윤곽 겹으로 깊이감만 냈다). 심사자는 이긴 판에서도 "물속 아래쪽이 비어 보인다", "같은 물고기가 반복된다"를 약점으로 적었다.
- 돛 달린 배(2·3단계)는 2배에서 돛 꼭대기가 상태 줄 뒤로 들어간다. 큰 어선은 화면 너비의 70%를 차지한다. 화면 가로가 80m 로 줄어 어군이 화면 밖에 있을 때가 많다(가까운 어군의 쪽과 거리를 화면 가장자리에 띄운다).
- 얕은 바다도 12m 아래는 남보라까지 어두워진다. 아트 디렉션의 "얕은 바다는 밝은 청록"보다 어둡고, 구간마다의 물색 차이가 줄었다.
- 얕은 바다에서 먼바다로 내려가는 비탈은 무늬 없는 넓은 모래 면이다.
- 고양이의 꼬리·귀 움직임은 픽셀을 옮긴 것이라 폭이 작다(±2px). 걷기와 감기 동작에는 없다.
- 산갈치의 볏이 점으로 끊겨 지저분하다. 갈치·산갈치의 도감 카드는 예전(굽은 자세) 그림이다.
- 별주부의 게임용 스프라이트(`turtle_*`)는 쓰이지 않아 손대지 않았다.
- 컷신: 큰 캐릭터는 다시 그린 것이 아니라 확대해 다듬은 것이다. 7컷의 앉은 고양이와 10컷의 배는 아직 정수배가 아니다. 걷기는 4프레임이라 발이 한 프레임에 15px 쯤 미끄러졌다 돌아온다. 전설의 그림자는 몸이 물결치지만 지느러미가 따로 움직이지는 않는다. 자세한 것은 [`design/cutscene-script.md`](design/cutscene-script.md) 의 "알려진 한계".
- 소리는 측정만 했고 아무도 귀로 듣지 않았다. 먼저 들어 볼 것: `talk`(대사 글자 소리), `pick`(줍기. 측정상 음악과 비슷한 크기다), 새로 만든 `bite`, 음악의 반복 지점. `legend_fight` 와 닫는 컷신의 음량은 실행 중에 재지 못했다.
- 성능: 60Hz·120Hz 화면에서는 다섯 화면 모두 느린 프레임(p95) 기준 74fps 이상이다. 창이 75Hz 세로 화면에 뜨는 기본 측정에서는 타이틀을 포함해 p95 가 53~64fps 로 나온다(게임의 틱은 평균 1ms 안팎, 드로우 콜 19~78. 화면 주사와 맞물린 프레임 간격이다).
- 로고는 글꼴을 키운 글자에 고양이 머리와 문양 한 칸을 붙인 것이라 소박하다.

세부는 [`design/asset-status.md`](design/asset-status.md), 조작법은 [`design/play-guide.md`](design/play-guide.md).
