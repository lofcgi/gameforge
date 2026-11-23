# 화면 모음 (2026-11-23)

그림·소리·컷신·화면 구조를 다시 만든 뒤의 실제 게임 화면이다. 전부 `gf engine capture` 로 실행 중인 게임에서 찍었다. 기준 해상도 640×360.

목표로 삼은 기준 화면은 [`design/look/target.png`](design/look/target.png) 이다.

## 기준 화면과 게임 화면 비교

![기준 화면과 게임 화면](captures/assets/sea_vs_target.png)

맥락 없는 심사 에이전트는 예전 색 덩어리 버전보다는 새 화면을, 새 화면보다는 기준 화면을 골랐다. 남은 차이는 아래 "아직 약한 것"에 적었다.

## 타이틀과 여는 컷신

![타이틀](captures/screens/title/shot_01_t1.00.png)

여는 컷신은 10컷 89.6초, 닫는 컷신은 3컷 30.4초다. 아래는 컷마다 시작·중간·끝을 찍은 모음이다.

| | |
|---|---|
| ![1 심해로](captures/cutscenes/intro_01.png) | ![2 용궁](captures/cutscenes/intro_02.png) |
| ![3 병든 용왕](captures/cutscenes/intro_03.png) | ![4 전설의 물고기](captures/cutscenes/intro_04.png) |
| ![5 별주부가 나섬](captures/cutscenes/intro_05.png) | ![6 뭍으로](captures/cutscenes/intro_06.png) |
| ![7 부두의 고양이](captures/cutscenes/intro_07.png) | ![8 거래](captures/cutscenes/intro_08.png) |
| ![9 맞잡은 손](captures/cutscenes/intro_09.png) | ![10 출항](captures/cutscenes/intro_10.png) |
| ![닫는 1](captures/cutscenes/ending_01.png) | ![닫는 2](captures/cutscenes/ending_02.png) |

## 항구 마을과 채집지

![마을](captures/screens/town/shot_01_t1.10.png)
![채집지](captures/screens/forage/shot_02_t3.40.png)

## 가게 (각각 따로 들어가는 실내 화면)

| 미끼 공방 | 어시장 |
|---|---|
| ![미끼 공방](captures/screens/in_bait/shot_03_t2.00.png) | ![어시장](captures/screens/in_market/shot_03_t2.00.png) |

| 조선소 | 낚시 가게 |
|---|---|
| ![조선소](captures/screens/in_yard/shot_03_t2.00.png) | ![낚시 가게](captures/screens/in_tackle/shot_03_t2.00.png) |

## 바다

| 얕은 바다 | 먼바다 | 심해 입구 |
|---|---|---|
| ![얕은 바다](captures/screens/sea_shallow/shot_02_t6.00.png) | ![먼바다](captures/screens/sea_open/shot_02_t6.00.png) | ![심해 입구](captures/screens/sea_deep/shot_02_t6.00.png) |

낚시(카메라가 미끼를 따라 내려간다):

![낚시](captures/screens/fishing/shot_03_t6.00.png)

전설의 심해어와 닫는 장면까지:

![전설](captures/screens/legend_run/shot_008.png)

## 섬과 도감

![섬](captures/screens/island/shot_02_t3.30.png)
![도감](captures/screens/codex/shot_01_t1.50.png)

## 에셋

![고양이 동작](captures/assets/cat_anims.png)
![물고기 12종](captures/assets/fish_all.png)
![전설 어종](captures/assets/fish_legend.png)
![배 3단계](captures/assets/boats.png)
![가게 주인](captures/assets/land_keepers.png)

## 아직 약한 것

- 바다 화면의 고양이와 배가 기준 화면보다 작게 보이고, 물고기가 작고 드물다.
- 얕은 바다의 물속이 단조롭다(유적·해파리는 다른 구간에 있다).
- 고양이의 꼬리·귀 움직임 프레임이 없다. 가게 주인의 말하는 동작이 1픽셀 까딱임이다.
- 컷신의 용궁 안 장면은 걷는 프레임 없이 통통 튀며 이동한다. 4컷과 닫는 3컷이 정적이다.
- 갈치·산갈치의 헤엄 동작이 어색하다.
- 소리는 측정만 했고 사람이 듣지 않았다. 효과음 5개(`talk`, `page`, `repair`, `pickup`, `release`)가 아직 없다.
- 성능: 평균 75fps지만 느린 프레임 기준 60fps를 이 환경에서 입증하지 못했다.

세부는 [`design/asset-status.md`](design/asset-status.md), 조작법은 [`design/play-guide.md`](design/play-guide.md).
