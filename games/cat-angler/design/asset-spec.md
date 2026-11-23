# 에셋 규격

코드와 그림을 따로 만들어도 맞물리게 하는 계약이다. 그림은 이 경로와 크기로 만들고, 코드는 이 경로에서 읽는다. 바꿔야 하면 이 문서를 먼저 고친다.

## 공통

- 기준 해상도 640×360. 모든 수치는 이 해상도의 픽셀이다.
- 전부 `design/look/palette.json` 의 24색으로 양자화한 진짜 픽셀 아트(반투명 가장자리 없음). 품질 기준은 `design/look/target.png`.
- 게임이 읽는 파일은 `assets/game/` 아래에만 둔다. 생성 원본은 `assets/raw/`.
- 스프라이트 시트는 `gf post sheet` 가 만드는 PNG + JSON + `.tres` 한 벌. 이름은 `<대상>_<동작>`. 코드는 `<폴더>/<대상>_<동작>.tres` 를 읽는다(예: `chars/cat_idle.tres`, `fish/anchovy_swim.tres`). 동작이 하나뿐인 것은 대상 이름 그대로다(`sea/bird.tres`, `sea/splash.tres`). `.tres` 가 없고 PNG + JSON 만 있어도 읽는다.
- 코드는 `scripts/assets.gd`(Assets) 한 곳에서만 이 경로들을 읽는다. 파일이 없으면 도형으로 그린 임시 그림을 쓰고, 빠진 파일 이름을 디버그 목록(F3, 브리지 `info.missing_assets`)에 올린다. 파일을 넣으면 다음 실행부터 코드 수정 없이 쓰인다.
- 옆 파일(JSON)의 좌표는 모두 그 그림의 픽셀 좌표(왼쪽 위가 0,0)다. JSON 이 없으면 코드의 기본 배치(`scripts/layout.gd`)를 쓴다.
- 캐릭터와 물체의 기준점은 발밑 가운데. 캐릭터는 오른쪽을 본다.
- 한 캐릭터의 모든 동작은 같은 캔버스 크기와 같은 발 위치를 쓴다.

## 캐릭터 `assets/game/chars/`

| 대상 | 캔버스 | 동작(프레임 수는 최소) |
|---|---|---|
| `cat` (주인공) | 80×60 (그림은 약 43×52, 낚싯대가 들어가도록 캔버스만 넓혔다. 발밑 가운데는 (40, 59)) | `idle` 4, `walk` 6, `pick` 3(줍기), `sit_fish` 4(낚싯대 들고 기다림), `reel` 4(감기), `strain` 4(버티기), `cheer` 4(낚았다), `sad` 2(놓쳤다) |
| `turtle` (별주부) | 48×48 | `idle` 4, `walk` 4, `bow` 2 |
| `king` (용왕) | 96×96 | `idle` 4(병든 모습), `better` 4(조금 나은 모습) |
| 가게 주인 4명 `keeper_bait`, `keeper_market`, `keeper_yard`, `keeper_tackle` | 48×56 | `idle` 4, `talk` 2 |

`chars/cat.json`: `{"canvas": [80, 60], "foot": [40, 59], "rod_tip": {"sit_fish": [[x, y], ...], "reel": [...], "strain": [...]}}`. 낚싯대는 낚시 동작 그림 안에 들어 있고, `rod_tip` 은 프레임별 낚싯대 끝(캔버스 좌표)이다. 낚싯줄은 여기서 내린다.

초상화 `assets/game/portraits/<대상>.png`, 96×96: `cat`, `turtle`, `king`, 가게 주인 4명.

## 배 `assets/game/boats/`

`boat1.png` 약 120×40(나룻배), `boat2.png` 약 168×72(돛단배), `boat3.png` 약 224×96(어선). 기준점은 흘수선 가운데. 고양이가 서는 자리는 각 파일 옆의 `boatN.json` 에 `{"seat": [x, y], "rod_tip": [x, y], "waterline": y}` 로 적는다.

- 배는 오른쪽을 본다. `seat` 는 고양이의 발밑 가운데(`chars/cat.json` 의 `foot`)가 놓이는 점, `rod_tip` 은 고양이가 `sit_fish` 자세로 앉았을 때 낚싯대 끝이 오는 점(낚싯줄이 여기서 내려간다), `waterline` 은 흘수선의 y 다. 그림의 가로 가운데가 배의 기준점이다.
- `boatN.json` 에 `"sink": n` 을 넣을 수 있다(없으면 8). 코드는 고양이를 `seat` 에서 n px 내려 앉히고, 배 그림의 `seat` y 아래쪽을 고양이 위에 다시 그려 발이 뱃전 뒤로 숨게 한다. 그러니 `seat` 는 고양이가 앉는 쪽 뱃전의 윗선에 둔다. **(코드 쪽에서 추가)**
- `chars/cat.json` 에 `rod_tip` 이 있으면(낚싯대가 고양이 그림 안에 있다) 낚싯줄은 `seat` + 고양이의 낚싯대 끝에서 내려가고, `boatN.json` 의 `rod_tip` 은 쓰지 않는다(생략해도 된다). `seat` 의 x 는 배 가운데에서 오른쪽으로 0~40px 사이에 둔다(그러면 미끼가 배 앞 40~80px 에 내려간다). **(코드 쪽에서 정함)**

## 물고기 `assets/game/fish/`

어종 ID는 `scripts/data.gd` 의 표를 따른다(13종). 종마다 `<id>_swim` 4프레임 시트와 도감용 큰 그림 `<id>_card.png`(96×64). 크기는 작은 것 24×16, 중간 40×24, 큰 것 72×40, 전설 160×80 이상. 전설 어종은 실루엣판 `<id>_shadow_swim` 도 만든다.

## 바다 `assets/game/sea/`

- 구간 3개(`shallow`, `open`, `deep`)마다: `sky_<구간>.png`(640×200, 가로로 이어 붙일 수 있게), 먼 배경 `far_<구간>.png`(가로 반복), 중간 배경 `mid_<구간>.png`(가로 반복), 물속 배경 `under_<구간>.png`(640×360 가로 반복), 바닥 `bed_<구간>.png`(가로 반복 띠).
- 수면 문양 `surface_pattern.png`(가로 반복, 전통 물결 문양), 파도 물마루 `wave_crest.png`.
- 겹을 놓는 규칙(항해 중 수평선은 화면 위에서 198px):
  - `sky_*`: 아래 가장자리가 수평선에 온다. 카메라가 물속으로 내려가면 함께 위로 밀려난다.
  - `far_*`, `mid_*`: 높이는 200 이하에서 자유, 너비는 640 의 배수. 아래 가장자리가 수평선에 온다. 빈 곳은 투명.
  - `under_*`: 위 가장자리가 수면선에 온다(수면 아래 0~360px). 맨 아랫줄의 색 아래로는 코드가 깊이에 따라 어두워지는 색 띠를 잇는다.
  - `bed_*`: 높이 64 의 띠, 너비 64 의 배수. 위 가장자리가 바닥선이다(윗부분 16px 안에서 울퉁불퉁해도 된다. 빈 곳은 투명). 띠 아래는 맨 아랫줄 색으로 채운다. 바닥이 기울어진 곳에서는 16px 너비로 잘라 계단처럼 놓는다.
  - `surface_pattern.png`: 64×32 타일. 아래 가장자리가 수면선에 오고 배 뒤에 그려져 천천히 흐른다. 위쪽은 물결 모양으로 뚫려 하늘이 보인다.
  - `wave_crest.png`: 약 64×24. 아래 가운데가 큰 파도의 꼭대기에 온다.
- 바다 화면 왼쪽 끝에 보이는 부두 `pier.png`(약 320×120, 오른쪽 끝이 배를 대는 자리, 아래에서 24px 위가 수면선). **(코드 쪽에서 추가)**
- 소용돌이 자리 표시 `vortex` 4프레임(96×24, 아래 가운데가 수면선). **(코드 쪽에서 추가)**
- 장소: `reef.png`, `wreck.png`, `island_far.png`(멀리서 본 섬), 유적 기둥 `ruin_1~3.png`, 용궁 누각 `pavilion.png`.
  - 기준점: `reef.png`(약 240×96, 암초 꼭대기에 여러 번 놓는다), `wreck.png`(약 256×128), `ruin_N.png`(약 64×96), `pavilion.png`(약 192×160)은 아래 가운데가 바닥선에 온다. `island_far.png`(약 320×160)은 아래에서 16px 위가 수면선이고 왼쪽 끝이 배를 대는 기슭이다.
- 어군 표시 `school_small`, `school_mid`, `school_big`(각 4프레임), 새 `bird` 4프레임.
  - 기준점 **(코드 쪽에서 정함)**: 어군 표시는 그림의 가운데가 수면선 4px 아래에 온다. 새는 어군 위 64~80px 에서 원을 그리며 돌고 가는 쪽으로 좌우가 뒤집힌다(그림은 오른쪽을 본다). `crate`·`bottle` 은 아래에서 6px 위가 수면선이고 좌우로 까딱거린다. `hook.png` 는 위 가운데가 낚싯줄 끝, `bait_<id>.png` 는 바늘 아래쪽에 겹쳐 놓인다. `splash` 는 아래 가운데가 수면선, `bubble`·`sparkle` 은 가운데가 기준점이다.
- 떠다니는 물건 `crate.png`, `bottle.png`. 미끼와 바늘 `hook.png`, `bait_<id>.png`(8×8).
- 효과 `splash` 6, `bubble` 4, `sparkle` 4.

## 장소 배경 `assets/game/places/`

| 파일 | 크기 | 내용 |
|---|---|---|
| `town.png` | 1600×360 | 항구 마을 바깥. 왼쪽부터 미끼 공방, 어시장, 조선소, 낚시 가게, 부두. 건물마다 문이 보인다. 문 위치는 `town.json` 에 `{"doors": {"bait": x, "market": x, "yard": x, "tackle": x}, "pier": x, "ground_y": y}` |
| `town_fg.png` | 1600×360 | 캐릭터 앞에 그려지는 겹(울타리, 통, 등불) |
| `forage.png` | 960×360 | 채집지. 오른쪽 끝이 마을로 이어진다. 재료 자리는 `forage.json` 에 `{"herb": [[x,y]..], "bug": [..], "berry": [..], "ground_y": y}`. 종류마다 4곳(자리의 y 는 재료 그림의 아래 가운데) |
| `island.png` | 640×360 | 섬 상륙 화면. `island.json` 에 `{"flower": [[x,y]], "dock": x, "ground_y": y, "left": x, "right": x}`. `dock` 은 배를 댄 자리(여기서 다시 탄다), `left`·`right` 는 걸을 수 있는 범위 |
| `in_bait.png`, `in_market.png`, `in_yard.png`, `in_tackle.png` | 640×360 | 실내. 주인이 서는 자리와 진열 자리는 같은 이름의 `.json` (아래 표) |

실내 `.json` 의 항목 **(코드 쪽에서 정함)**. 위 28px 는 상태 줄, 아래 96px 는 대사 창이 덮으므로 중요한 것은 y 28~264 사이에 둔다.

| 파일 | 항목 |
|---|---|
| 공통 | `"keeper": [x, y]` 주인의 발밑 가운데, `"cat": [x, y]` 고양이의 발밑 가운데 |
| `in_bait.json` | `"bench": [x, y, w, h]` 재료를 올리는 작업대 윗면, `"baskets": [[x,y]×4]` 재료 바구니(약초, 곤충, 열매, 섬꽃 순), `"out": [x, y]` 완성된 미끼가 놓이는 자리 |
| `in_market.json` | `"table": [x, y, w, h]` 물고기를 늘어놓는 진열대 윗면(가로 240 이상, 세로 80 이상), `"scale": [x, y]` 저울(팔린 물고기가 가는 곳) |
| `in_yard.json` | `"dock": [x, y]` 선거에 놓인 내 배의 흘수선 가운데(주변 240×110 을 비워 둔다), `"preview": [x, y, w, h]` 다음 배의 설계도가 걸리는 판 |
| `in_tackle.json` | `"rods": [[x,y]×3]` 벽에 걸린 낚싯대 세 자루의 가운데(대나무, 옻칠, 용골 순. 사이 간격 70 이상) |

`town.json` 에는 `"left": x, "right": x`(걸을 수 있는 범위)도 넣을 수 있다. `ground_y` 는 캐릭터의 발이 닿는 y 다. `town.json` 과 `island.json` 에 `"water_y": y` 를 넣으면 부두(선착장)에 매인 내 배의 흘수선이 그 높이에 온다(없으면 `ground_y` + 24). 배는 마을에서는 `pier` 오른쪽 34px 부터, 섬에서는 `dock` 왼쪽 30px 까지 놓인다. 타이틀의 흔들리는 나룻배는 (470, 230)에 놓이고 그 뒤로 수면 문양이 y 226 에 흐른다(`title.png` 에는 배를 그려 넣지 않는다).
| `title.png` | 640×360 | 타이틀 배경(로고 자리는 비워 둔다) |

채집 재료 `assets/game/items/`: `herb`, `bug`, `berry`, `flower`(각 16×16 아이콘과 땅에 난 모습 24×24), 미끼 4종 아이콘 16×16, 동전, 낚싯대 3종 아이콘 32×32.

파일 이름: 아이콘 `<id>.png`, 땅에 난 모습 `<id>_plant.png`, 미끼 `bait_herb.png`·`bait_bug.png`·`bait_berry.png`·`bait_legend.png`, 동전 `coin.png`(16×16), 낚싯대 아이콘 `rod1.png`~`rod3.png`, 낚시 가게 벽에 거는 낚싯대 `rod1_wall.png`~`rod3_wall.png`(24×128, 세워 둔 모습) **(벽걸이는 코드 쪽에서 추가)**.

## UI `assets/game/ui/`

9-slice 창 틀 `panel.png`(48×48, 가장자리 12), 버튼 `button.png`·`button_focus.png`, 말풍선 `bubble.png`, 게이지 틀과 채움(`gauge_frame`, `gauge_fill`), 장력 게이지 `tension_frame`·`tension_fill`, 깊이 눈금 `depth_ruler.png`, 어창 칸 `slot.png`, 도감 책 `codex_book.png`(640×360), 아이콘(내구도, 어창, 동전, 닻), 로고 `logo.png`.

크기와 쓰임 **(코드 쪽에서 정함)**:

| 파일 | 크기 | 쓰임 |
|---|---|---|
| `panel.png` | 48×48, 가장자리 12 | 창, 상태 줄, 알림. 9-slice |
| `button.png`, `button_focus.png` | 32×24, 가장자리 8 | 메뉴 항목과 키 표시. 9-slice |
| `bubble.png` | 48×48, 가장자리 12 | 대사 창(화면 아래, 초상화 옆). 9-slice |
| `gauge_frame.png`, `gauge_fill.png` | 틀 64×12(가장자리 4), 채움 4×4 | 가로 게이지(내구도, 물고기 체력). 채움은 늘려 그린다 |
| `tension_frame.png`, `tension_fill.png` | 틀 24×168(가장자리 6), 채움 4×4 | 세로 장력 게이지. 채움의 색은 코드가 입힌다(흰색 계열로 그린다) |
| `depth_ruler.png` | 24×32 타일 | 깊이 눈금의 세로 띠(위아래로 반복) |
| `slot.png`, `slot_focus.png` | 28×28, 가장자리 6 | 어창·진열대·도감의 칸. `slot_focus` 는 고른 칸 |
| `codex_book.png` | 640×360 | 도감. 쪽의 자리는 `codex_book.json` 에 `{"left": [x,y,w,h], "right": [x,y,w,h]}`(없으면 왼쪽 44,40,260,280 / 오른쪽 336,40,260,280) |
| `icon_durability.png`, `icon_hold.png`, `icon_coin.png`, `icon_anchor.png`, `icon_bait.png` | 16×16 | 상태 줄 아이콘 |
| `arrow.png` | 16×16, 아래를 가리킨다 | 길잡이 화살표와 커서 |
| `logo.png` | 400×140 이하 | 타이틀 로고(글자는 그림에 넣는다) |

글꼴: 한글이 되는 픽셀 글꼴을 `assets/game/fonts/` 에 둔다(사용 허가가 분명한 것만).

코드는 글꼴을 네 가지 역할로 쓴다 **(코드 쪽에서 정함)**: 본문 `body`(Galmuri11.ttf, 12px), 굵게 `bold`(Galmuri11-Bold.ttf, 12px. 세계 위에 테두리를 둘러 얹는 글자), 작게 `small`(Galmuri9.ttf, 10px), 크게 `large`(Galmuri14.ttf, 15px). 다른 글꼴로 바꾸려면 `fonts/font.json` 에 `{"body": ["파일.ttf", 12], "bold": [...], "small": [...], "large": [...]}` 을 둔다.

## 컷신 `assets/game/cutscenes/`

여는 컷신 `intro_01` ~ `intro_08`, 닫는 컷신 `ending_01` ~ `ending_02`. 컷마다 폴더 하나에 겹을 나눠 둔다: `bg.png`(640×360 이상, 카메라가 움직일 만큼 넓게), `mid.png`, `chars.png` 또는 캐릭터 시트, `fg.png`. 컷의 내용과 움직임은 `design/cutscene-script.md` 에 적는다.

컷신 씬과 게임이 맞물리는 규칙 **(코드 쪽에서 정함)**:

- 씬은 `scenes/cutscenes/intro.tscn`, `scenes/cutscenes/ending.tscn`. 게임(`scripts/screens/cutscene_host.gd`)이 이 씬을 자식으로 넣어 재생하고, 끝나면 지운다.
- 루트 노드는 `signal finished` 를 가진다. 마지막 컷이 끝나면 한 번 낸다.
- 건너뛰기: 플레이어가 X(Esc)를 누르면 게임이 루트의 `skip()` 을 부른다. `skip()` 은 곧바로(또는 짧게 마무리한 뒤) `finished` 를 낸다. 씬이 건너뛰기를 스스로 처리해도 된다(루트에 `skippable` 변수를 두고 `cancel` 을 길게 눌러 건너뛴다. 지금의 `CutscenePlayer` 가 이 방식이다). 둘 다 없으면 게임이 그 자리에서 끝낸다.
- 진행은 `_physics_process`(초당 60틱)에서 틱을 세어 한다. 벽시계와 `randomize()` 를 쓰지 않는다(기록 재생과 봇 때문이다). 씬이 스스로 `action` 입력을 읽어 자막을 넘기는 것은 된다.
- 화면은 640×360, 원점은 왼쪽 위. 전환(페이드)은 게임이 앞뒤로 넣는다. 음악은 컷신 씬이 스스로 튼다(지금의 `CutscenePlayer` 가 그렇다). 게임이 `assets/game/audio/cutscene_intro.wav`·`cutscene_ending.wav` 를 대신 틀게 하려면 루트에 `var plays_own_music := false` 를 둔다. 씬이 없을 때의 임시 카드에서는 게임이 튼다.
- 씬이 아직 없으면 게임은 "컷신 준비 중" 임시 카드를 보여 주고 넘어간다.

## 소리 `assets/game/audio/`

- 파일은 `assets/game/audio/<이름>.wav`(없으면 `.ogg`, `.mp3` 순으로 찾는다).
- 음악(반복용 wav): `title`, `town`, `sea_shallow`, `sea_open`, `sea_deep`, `fight`, `legend_fight`, `cutscene_intro`, `cutscene_ending`. 채집지·실내·섬은 `town` 을 쓴다.
- 효과음: `step`, `pick`, `door`, `coin`, `buy`, `craft`, `anchor_down`, `anchor_up`, `cast`, `nibble`, `bite`, `reel`, `line_strain`, `snap`, `slip`, `catch_small`, `catch_big`, `wave_hit`, `splash`, `ui_move`, `ui_ok`, `ui_cancel`, `codex_new`
- 코드 쪽에서 추가한 효과음: `talk`(대사 글자가 찍히는 짧은 소리), `page`(도감 넘기기), `repair`(수리·개조 망치질), `pickup`(떠다니는 물건 건지기), `release`(놓아주기)

## 그림 쪽에서 정한 것 (규격과 다른 점)

- 고양이 캔버스는 80×60, 발밑 가운데 (40, 59). 낚싯대가 낚시 동작 그림 안에 있어 48×56 에 들어가지 않는다. 프레임별 낚싯대 끝은 `chars/cat.json` 의 `rod_tip`.
- 배의 실제 크기: `boat1` 119×33, `boat2` 168×134, `boat3` 224×137(돛과 선실까지 그려 규격의 "약 168×72, 224×96"보다 높다). `boatN.json` 의 `seat` 는 80×60 고양이 캔버스의 발밑 가운데 기준이고 `rod_tip` = seat + (32, −44).
- 물고기 크기는 규격의 작은 것 24×16 보다 조금 키웠다(블라인드 심사에서 "물고기가 작고 물색에 묻힌다"는 지적). 멸치 30×9, 전갱이 38×17, 넙치 48×36, 고등어 44×21, 놀래기 36×18, 쏨뱅이 46×31, 참돔 50×31, 방어 73×29, 곰치 76×38, 갈치 71×30, 아귀 60×38, 산갈치 97×57, 전설 176×98. 헤엄 시트는 위아래로 여백(꼬리 흔들림 폭)이 붙는다.
- `far_<구간>.png` 는 1280 너비(640 그림을 좌우로 뒤집어 붙여 이음매를 없앴다), 높이 111~150. `mid_<구간>.png` 는 640×88.
- `bed_<구간>.png` 는 1024×64(심해는 512×64), 좌우로 뒤집어 붙인 띠.
- `school_small` 32×28, `school_mid` 48×32, `school_big` 72×40: 코드가 그림 가운데를 수면선 4px 아래에 놓는 것에 맞춰 잔물결 줄이 가운데에서 4px 위에 있다.
- `legend_shadow_swim` 은 검은색이 아니라 남보라(#2E3068) 몸에 푸른 테두리(#426A96)다. 심해의 물색이 #17121B~#1B2139 라 검은 실루엣은 보이지 않았다.
- `sea/pier.json`(`deck_y`, `waterline`, `size`)이 규격에 없이 추가됐다.
- `in_market.json` 의 `table` 높이는 46(규격 80 이상에 못 미친다). `in_yard.json` 의 `preview` 는 98×64.
- `ui/bubble.png` 는 꼬리 없는 9-slice 상자, `ui/logo.png` 는 342×129.
- 글꼴: `assets/game/fonts/Galmuri11.ttf`, `Galmuri11-Bold.ttf`, `Galmuri9.ttf`, `Galmuri14.ttf` (SIL OFL 1.1, 출처는 같은 폴더의 `SOURCE.md`).
