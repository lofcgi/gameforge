class_name Data
## 균형 데이터. 구간, 어종, 미끼, 낚싯대, 배, 장소, 항구 배치를 여기서만 고친다.
## 거리와 깊이는 미터로 적는다. 화면 좌표는 X_PX(가로), Y_PX(세로)를 곱한다.

const X_PX := 2.0
const Y_PX := 4.0
const SEA_END_M := 2400.0
const PIER_M := 306.0

## amp: 잔물결 높이(px), crest: 큰 파도 높이(px), grade: 이 구간을 견디는 데 필요한 배 등급
const ZONES := [
	{"id": "port", "name": "항구", "from": 0, "to": 300, "bed": 0, "amp": 0.8, "crest": 0.0, "grade": 0.0,
		"sky": Color("#E9F3E2"), "water": Color("#76D7D9"), "bed_color": Color("#D79966")},
	{"id": "shallow", "name": "얕은 바다", "from": 300, "to": 900, "bed": 30, "amp": 1.6, "crest": 3.0, "grade": 1.0,
		"sky": Color("#BAEADC"), "water": Color("#5DC5CB"), "bed_color": Color("#E5DDC8")},
	{"id": "open", "name": "먼바다", "from": 900, "to": 1800, "bed": 80, "amp": 4.0, "crest": 9.0, "grade": 2.0,
		"sky": Color("#7BAEB9"), "water": Color("#468DB4"), "bed_color": Color("#799088")},
	{"id": "deep", "name": "심해 입구", "from": 1800, "to": 2400, "bed": 150, "amp": 7.0, "crest": 14.0, "grade": 3.0,
		"sky": Color("#54608F"), "water": Color("#2E3068"), "bed_color": Color("#B8D0BF")},
]
const DEEP_WATER := Color("#1B2139")

## reach: 닿는 깊이(m), str: 버티는 힘, reel: 감는 속도(px/s)
const RODS := [
	{"name": "대나무 낚싯대", "reach": 30, "str": 3.0, "reel": 40.0, "price": 0},
	{"name": "옻칠 낚싯대", "reach": 80, "str": 7.0, "reel": 52.0, "price": 100},
	{"name": "용골 낚싯대", "reach": 150, "str": 12.0, "reel": 66.0, "price": 420},
]

## grade: 버티는 파도 등급, dur: 내구도, speed: 최고 속도(px/s), accel: 가속(px/s^2), hold: 어창 칸
const BOATS := [
	{"name": "나룻배", "grade": 1.0, "dur": 30, "speed": 62.0, "accel": 85.0, "hold": 6, "price": 0},
	{"name": "돛단배", "grade": 2.0, "dur": 50, "speed": 84.0, "accel": 100.0, "hold": 10, "price": 180},
	{"name": "큰 어선", "grade": 3.0, "dur": 80, "speed": 108.0, "accel": 115.0, "hold": 14, "price": 650},
]
const WAVE_DAMAGE := 6.0      # 큰 파도 한 번의 피해 = WAVE_DAMAGE * (파도 등급 - 배 등급)
const REPAIR_PER_COIN := 2.0  # 동전 하나로 고치는 내구도

const MATS := {
	"herb": {"name": "약초", "color": Color("#96B89D")},
	"bug": {"name": "곤충", "color": Color("#B4774F")},
	"berry": {"name": "열매", "color": Color("#D46A7E")},
	"flower": {"name": "섬꽃", "color": Color("#E9D36B")},
}
const GATHER_YIELD := 4

const BAIT_ORDER := ["herb", "bug", "berry", "legend"]
const BAITS := {
	"herb": {"name": "풀떡밥", "cost": {"herb": 1}, "color": Color("#96B89D")},
	"bug": {"name": "벌레 미끼", "cost": {"bug": 1}, "color": Color("#B4774F")},
	"berry": {"name": "열매 미끼", "cost": {"berry": 1}, "color": Color("#D46A7E")},
	"legend": {"name": "용궁 미끼", "cost": {"herb": 1, "bug": 1, "berry": 1, "flower": 1}, "color": Color("#E9D36B")},
}
const START_BAITS := {"herb": 4}

## 장소. x, w 는 미터. reef.top 은 암초 꼭대기 깊이.
const PLACES := {
	"reef": {"name": "암초", "x": 1200.0, "w": 130.0, "top": 16.0},
	"island": {"name": "작은 섬", "x": 1440.0, "w": 64.0},
	"wreck": {"name": "난파선", "x": 1640.0, "w": 80.0},
	"vortex": {"name": "소용돌이 자리", "x": 2250.0, "w": 70.0},
}

## 어종. shape: 그레이박스의 몸 모양(round/flat/long), zone: 사는 구간, place: 장소 전용이면 장소 id, dmin~dmax: 사는 깊이(m), slots: 어창 칸,
## str: 힘(낚싯대의 str 과 비교), speed: 헤엄 속도(px/s), move: school/dart/lurk/cruise/patrol,
## count: 배 주변에 유지할 마릿수, run: 줄다리기 때 옆으로 달아나는가
const FISH := [
	{"id": "anchovy", "name": "멸치", "shape": "round", "zone": "shallow", "place": "", "dmin": 2, "dmax": 10, "slots": 1, "price": 5,
		"baits": ["herb"], "str": 1.0, "speed": 22.0, "move": "school", "count": 5, "run": false, "color": Color("#B8D0BF")},
	{"id": "scad", "name": "전갱이", "shape": "round", "zone": "shallow", "place": "", "dmin": 9, "dmax": 20, "slots": 1, "price": 10,
		"baits": ["bug"], "str": 2.0, "speed": 30.0, "move": "dart", "count": 3, "run": false, "color": Color("#799088")},
	{"id": "flounder", "name": "넙치", "shape": "flat", "zone": "shallow", "place": "", "dmin": 23, "dmax": 30, "slots": 2, "price": 24,
		"baits": ["berry"], "str": 3.0, "speed": 8.0, "move": "lurk", "count": 2, "run": false, "color": Color("#B4774F")},
	{"id": "mackerel", "name": "고등어", "shape": "round", "zone": "open", "place": "", "dmin": 5, "dmax": 25, "slots": 1, "price": 14,
		"baits": ["herb"], "str": 3.0, "speed": 34.0, "move": "school", "count": 4, "run": false, "color": Color("#426A96")},
	{"id": "bream", "name": "참돔", "shape": "round", "zone": "open", "place": "", "dmin": 32, "dmax": 55, "slots": 2, "price": 36,
		"baits": ["bug"], "str": 5.0, "speed": 18.0, "move": "cruise", "count": 3, "run": false, "color": Color("#D46A7E")},
	{"id": "amberjack", "name": "방어", "shape": "round", "zone": "open", "place": "", "dmin": 45, "dmax": 78, "slots": 3, "price": 62,
		"baits": ["berry"], "str": 7.0, "speed": 40.0, "move": "patrol", "count": 2, "run": true, "color": Color("#DFB68B")},
	{"id": "wrasse", "name": "놀래기", "shape": "round", "zone": "open", "place": "reef", "dmin": 4, "dmax": 13, "slots": 1, "price": 22,
		"baits": ["berry"], "str": 3.0, "speed": 24.0, "move": "dart", "count": 3, "run": false, "color": Color("#54A9A7")},
	{"id": "rockfish", "name": "쏨뱅이", "shape": "round", "zone": "open", "place": "reef", "dmin": 10, "dmax": 20, "slots": 1, "price": 28,
		"baits": ["bug"], "str": 4.0, "speed": 6.0, "move": "lurk", "count": 3, "run": false, "color": Color("#8C533C")},
	{"id": "moray", "name": "곰치", "shape": "long", "zone": "open", "place": "wreck", "dmin": 66, "dmax": 80, "slots": 3, "price": 90,
		"baits": ["bug"], "str": 8.0, "speed": 6.0, "move": "lurk", "count": 2, "run": true, "color": Color("#546166")},
	{"id": "hairtail", "name": "갈치", "shape": "long", "zone": "deep", "place": "", "dmin": 20, "dmax": 60, "slots": 2, "price": 50,
		"baits": ["herb"], "str": 6.0, "speed": 26.0, "move": "dart", "count": 3, "run": false, "color": Color("#B8D0BF")},
	{"id": "angler", "name": "아귀", "shape": "round", "zone": "deep", "place": "", "dmin": 90, "dmax": 130, "slots": 3, "price": 115,
		"baits": ["bug"], "str": 9.0, "speed": 6.0, "move": "lurk", "count": 2, "run": true, "color": Color("#5E342B")},
	{"id": "oarfish", "name": "산갈치", "shape": "long", "zone": "deep", "place": "", "dmin": 108, "dmax": 148, "slots": 4, "price": 170,
		"baits": ["berry"], "str": 11.0, "speed": 20.0, "move": "patrol", "count": 2, "run": true, "color": Color("#7BAEB9")},
	{"id": "legend", "name": "전설의 심해어", "shape": "round", "zone": "deep", "place": "vortex", "dmin": 132, "dmax": 147, "slots": 6, "price": 0,
		"baits": ["legend"], "str": 16.0, "speed": 9.0, "move": "lurk", "count": 1, "run": true, "color": Color("#E9F3E2")},
]

## 줄다리기. 장력은 0~1 이고 목표값을 따라간다. ratio = 물고기 str / 낚싯대 str.
const TUG := {
	"up": 2.2, "down": 1.3,            # 장력이 목표값으로 오르는/내리는 빠르기(1/s)
	"reel_pull": [0.5, 0.6],           # 버틸 때 감으면: 기본 + ratio 배수. 1 을 넘으면 끊어진다
	"reel_tired": [0.4, 0.3],          # 지쳤을 때 감으면
	"slack_pull": [0.25, 0.25],        # 버틸 때 풀면
	"cap": 1.22,                       # 목표값 상한
	"warn": 0.38,                      # 버티기 직전 예고 시간(s)
	"slack_at": 0.15, "slack_time": [1.0, 3.0],  # 느슨함 한계와 바늘이 빠지기까지(s): 큰 물고기, 작은 물고기
	"run_speed": [14.0, 5.0],          # 버틸 때 풀려 나가는 줄(px/s): 기본 + str 배수
	"run_extra": 0.2, "limit_extra": 0.2, "follow_relief": 0.15,
}

## 항구(육지) 배치. x 는 px.
const PORT_LEFT := 12.0
const PORT_RIGHT := 600.0
const PORT_SPAWN := 44.0
const STATIONS := [
	{"id": "herb", "kind": "gather", "x": 44.0, "name": "약초밭"},
	{"id": "bug", "kind": "gather", "x": 92.0, "name": "풀숲"},
	{"id": "berry", "kind": "gather", "x": 140.0, "name": "열매나무"},
	{"id": "bench", "kind": "panel", "x": 214.0, "name": "미끼 작업대", "say": "너구리: 재료만 가져와. 손은 내가 빠르지."},
	{"id": "market", "kind": "panel", "x": 304.0, "name": "어시장", "say": "수달: 오늘 물 좋네! 다 사 줄게."},
	{"id": "shipyard", "kind": "panel", "x": 394.0, "name": "조선소", "say": "비버: 배는 파도보다 튼튼해야지."},
	{"id": "tackle", "kind": "panel", "x": 484.0, "name": "낚시 가게", "say": "왜가리: 깊은 데 고기가 크다네."},
	{"id": "pier", "kind": "board", "x": 588.0, "name": "부두"},
]
const ISLAND_STATIONS := [
	{"id": "dock", "kind": "board", "x": -40.0, "name": "배"},
	{"id": "flower", "kind": "gather", "x": 34.0, "name": "섬꽃"},
]

const NOTES := [
	"쪽지: \"암초의 물고기는 얕은 데 숨는다.\"",
	"쪽지: \"섬 꼭대기에 달 닮은 꽃이 핀다.\"",
	"쪽지: \"가라앉은 배 밑에 뱀 같은 놈이 산다.\"",
	"쪽지: \"소용돌이 아래, 자개빛 그림자를 보았다.\"",
	"쪽지: \"버틸 땐 풀고, 지치면 감아라.\"",
	"쪽지: \"새가 도는 물 밑엔 고기가 모인다.\"",
	"쪽지: \"용왕님은 육지의 맛을 그리워하신다.\"",
	"쪽지: \"큰 파도는 큰 배로 넘는다.\"",
]

const INTRO := [
	"깊은 바다 용궁.\n용왕이 병들어 누웠다.",
	"영약은 단 하나,\n전설의 심해어.",
	"그 물고기는 육지의 재료로 만든\n미끼에만 입질한다.",
	"별주부가 사냥꾼을 찾아\n육지로 올라왔다.",
	"\"세상 모든 물고기를 낚게 해 준다고?\"\n고양이의 귀가 섰다.",
	"거래 성립.\n작은 나룻배가 바다로 나간다.",
]
const ENDING := [
	"전설의 심해어를 용궁에 바쳤다.\n용왕의 숨이 조금 편해졌다.",
	"\"더 먼 바다에 다음 전설이 있다네.\"\n고양이는 벌써 낚싯대를 닦고 있다.\n\n- 데모 끝 -",
]
const WRECKED := ["큰 파도에 배가 떠밀려\n항구로 돌아왔다.\n\n어창의 절반을 잃었다."]


static func fish(id: String) -> Dictionary:
	for entry in FISH:
		if entry["id"] == id:
			return entry
	push_error("없는 어종: " + id)
	return {}


static func zone(id: String) -> Dictionary:
	for entry in ZONES:
		if entry["id"] == id:
			return entry
	push_error("없는 구간: " + id)
	return {}
