class_name Data
## 균형 데이터. 구간, 어종, 미끼, 낚싯대, 배, 장소, 항구 배치를 여기서만 고친다.
## 거리와 깊이는 미터로 적는다. 화면 좌표(기준 해상도 640×360 의 픽셀)는 X_PX(가로), Y_PX(세로)를 곱한다.

const X_PX := 4.0
const Y_PX := 8.0
const SEA_END_M := 2400.0
const PIER_M := 306.0

## amp: 잔물결 높이(px), crest: 큰 파도 높이(px), grade: 이 구간을 견디는 데 필요한 배 등급
const ZONES := [
	{"id": "port", "name": "항구", "from": 0, "to": 300, "bed": 0, "amp": 1.6, "crest": 0.0, "grade": 0.0,
		"sky": Color("#E9F3E2"), "water": Color("#76D7D9"), "bed_color": Color("#D79966")},
	{"id": "shallow", "name": "얕은 바다", "from": 300, "to": 900, "bed": 30, "amp": 3.2, "crest": 6.0, "grade": 1.0,
		"sky": Color("#BAEADC"), "water": Color("#5DC5CB"), "bed_color": Color("#E5DDC8")},
	{"id": "open", "name": "먼바다", "from": 900, "to": 1800, "bed": 80, "amp": 8.0, "crest": 18.0, "grade": 2.0,
		"sky": Color("#7BAEB9"), "water": Color("#468DB4"), "bed_color": Color("#799088")},
	{"id": "deep", "name": "심해 입구", "from": 1800, "to": 2400, "bed": 150, "amp": 14.0, "crest": 28.0, "grade": 3.0,
		"sky": Color("#54608F"), "water": Color("#2E3068"), "bed_color": Color("#B8D0BF")},
]
const DEEP_WATER := Color("#1B2139")

## reach: 닿는 깊이(m), str: 버티는 힘, reel: 감는 속도(px/s)
const RODS := [
	{"name": "대나무 낚싯대", "reach": 30, "str": 3.0, "reel": 80.0, "price": 0},
	{"name": "옻칠 낚싯대", "reach": 80, "str": 7.0, "reel": 104.0, "price": 100},
	{"name": "용골 낚싯대", "reach": 150, "str": 12.0, "reel": 132.0, "price": 420},
]

## grade: 버티는 파도 등급, dur: 내구도, speed: 최고 속도(px/s), accel: 가속(px/s^2), hold: 어창 칸
const BOATS := [
	{"name": "나룻배", "grade": 1.0, "dur": 30, "speed": 124.0, "accel": 170.0, "hold": 6, "price": 0},
	{"name": "돛단배", "grade": 2.0, "dur": 50, "speed": 168.0, "accel": 200.0, "hold": 10, "price": 180},
	{"name": "큰 어선", "grade": 3.0, "dur": 80, "speed": 216.0, "accel": 230.0, "hold": 14, "price": 650},
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
		"baits": ["herb"], "str": 1.0, "speed": 44.0, "move": "school", "count": 5, "run": false, "color": Color("#B8D0BF")},
	{"id": "scad", "name": "전갱이", "shape": "round", "zone": "shallow", "place": "", "dmin": 9, "dmax": 20, "slots": 1, "price": 10,
		"baits": ["bug"], "str": 2.0, "speed": 60.0, "move": "dart", "count": 3, "run": false, "color": Color("#799088")},
	{"id": "flounder", "name": "넙치", "shape": "flat", "zone": "shallow", "place": "", "dmin": 23, "dmax": 30, "slots": 2, "price": 24,
		"baits": ["berry"], "str": 3.0, "speed": 16.0, "move": "lurk", "count": 2, "run": false, "color": Color("#B4774F")},
	{"id": "mackerel", "name": "고등어", "shape": "round", "zone": "open", "place": "", "dmin": 5, "dmax": 25, "slots": 1, "price": 14,
		"baits": ["herb"], "str": 3.0, "speed": 68.0, "move": "school", "count": 4, "run": false, "color": Color("#426A96")},
	{"id": "bream", "name": "참돔", "shape": "round", "zone": "open", "place": "", "dmin": 32, "dmax": 55, "slots": 2, "price": 36,
		"baits": ["bug"], "str": 5.0, "speed": 36.0, "move": "cruise", "count": 3, "run": false, "color": Color("#D46A7E")},
	{"id": "amberjack", "name": "방어", "shape": "round", "zone": "open", "place": "", "dmin": 45, "dmax": 78, "slots": 3, "price": 62,
		"baits": ["berry"], "str": 7.0, "speed": 80.0, "move": "patrol", "count": 2, "run": true, "color": Color("#DFB68B")},
	{"id": "wrasse", "name": "놀래기", "shape": "round", "zone": "open", "place": "reef", "dmin": 4, "dmax": 13, "slots": 1, "price": 22,
		"baits": ["berry"], "str": 3.0, "speed": 48.0, "move": "dart", "count": 3, "run": false, "color": Color("#54A9A7")},
	{"id": "rockfish", "name": "쏨뱅이", "shape": "round", "zone": "open", "place": "reef", "dmin": 10, "dmax": 20, "slots": 1, "price": 28,
		"baits": ["bug"], "str": 4.0, "speed": 12.0, "move": "lurk", "count": 3, "run": false, "color": Color("#8C533C")},
	{"id": "moray", "name": "곰치", "shape": "long", "zone": "open", "place": "wreck", "dmin": 66, "dmax": 80, "slots": 3, "price": 90,
		"baits": ["bug"], "str": 8.0, "speed": 12.0, "move": "lurk", "count": 2, "run": true, "color": Color("#546166")},
	{"id": "hairtail", "name": "갈치", "shape": "long", "zone": "deep", "place": "", "dmin": 20, "dmax": 60, "slots": 2, "price": 50,
		"baits": ["herb"], "str": 6.0, "speed": 52.0, "move": "dart", "count": 3, "run": false, "color": Color("#B8D0BF")},
	{"id": "angler", "name": "아귀", "shape": "round", "zone": "deep", "place": "", "dmin": 90, "dmax": 130, "slots": 3, "price": 115,
		"baits": ["bug"], "str": 9.0, "speed": 12.0, "move": "lurk", "count": 2, "run": true, "color": Color("#5E342B")},
	{"id": "oarfish", "name": "산갈치", "shape": "long", "zone": "deep", "place": "", "dmin": 108, "dmax": 148, "slots": 4, "price": 170,
		"baits": ["berry"], "str": 11.0, "speed": 40.0, "move": "patrol", "count": 2, "run": true, "color": Color("#7BAEB9")},
	{"id": "legend", "name": "전설의 심해어", "shape": "round", "zone": "deep", "place": "vortex", "dmin": 132, "dmax": 147, "slots": 6, "price": 0,
		"baits": ["legend"], "str": 16.0, "speed": 18.0, "move": "lurk", "count": 1, "run": true, "color": Color("#E9F3E2")},
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
	"run_speed": [28.0, 10.0],          # 버틸 때 풀려 나가는 줄(px/s): 기본 + str 배수
	"run_extra": 0.2, "limit_extra": 0.2, "follow_relief": 0.15,
}

## 가게. scene: 실내 화면 이름, panel: 브리지 상태의 panel 이름, keeper: 주인(에셋 이름은 keeper_<id>).
## hello: 들어설 때의 인사(첫 방문은 전부, 그 뒤로는 한 줄씩 돌아가며), 그 밖은 상황별 한마디.
const SHOPS := {
	"bait": {"scene": "in_bait", "panel": "bench", "title": "미끼 공방", "keeper": "너구리",
		"hello": ["어서 와. 여긴 미끼 공방이야.", "재료만 가져와. 손은 내가 빠르지.", "좌우로 미끼를 고르고 Space 로 만들어."],
		"again": ["또 왔네. 뭘 빚어 줄까?", "오늘은 물때가 좋아. 미끼를 넉넉히 챙겨."],
		"done": "자, 다 됐어. 잘 물릴 거야.", "no": "재료가 모자라. 왼쪽 채집지에서 더 주워 와.",
		"tips": {"herb": "풀떡밥. 멸치, 고등어, 갈치가 좋아해.", "bug": "벌레 미끼. 전갱이, 참돔, 쏨뱅이, 곰치, 아귀가 물어.",
			"berry": "열매 미끼. 넙치, 방어, 놀래기, 산갈치가 좋아하지.", "legend": "용궁 미끼. 네 가지 재료가 다 들어가. 섬꽃은 먼바다 섬에 피어."}},
	"market": {"scene": "in_market", "panel": "market", "title": "어시장", "keeper": "수달",
		"hello": ["어서 와! 여긴 어시장이야.", "오늘 물 좋네! 다 사 줄게.", "좌우로 고르고 Space 로 팔아. 종을 치면 한꺼번에 사 갈게."],
		"again": ["오, 어창이 묵직해 보이는데?", "먼바다 고기는 값을 더 쳐 줄게."],
		"done": "좋아, 값 쳐 줄게!", "no": "팔 고기가 없네. 바다에 다녀와.", "legend": "이건 내가 살 물건이 아니야. 용궁에 바쳐야지.",
		"tips": {}},
	"yard": {"scene": "in_yard", "panel": "shipyard", "title": "조선소", "keeper": "비버",
		"hello": ["조선소에 잘 왔어.", "배는 파도보다 튼튼해야지.", "수리도 개조도 여기서 해. 좌우로 고르고 Space."],
		"again": ["배 상태부터 보자고.", "큰 파도는 큰 배로 넘는 거야."],
		"done": "새 배다! 더 먼 파도도 견딜 거야.", "fixed": "말끔하게 고쳤어.", "no": "돈이 모자라. 고기를 더 팔고 와.",
		"max": "이보다 좋은 배는 아직 못 만들어.",
		"tips": {"repair": "부서진 곳을 고쳐 줄게. 내구도 2 에 한 닢이야.", "upgrade": "다음 배는 더 거친 파도를 버티고 더 많이 실어."}},
	"tackle": {"scene": "in_tackle", "panel": "tackle", "title": "낚시 가게", "keeper": "왜가리",
		"hello": ["어서 오게. 낚시 가게라네.", "깊은 데 고기가 크다네.", "벽의 낚싯대를 좌우로 견주어 보고 Space 로 사게."],
		"again": ["오늘은 어디까지 내려 볼 텐가?", "낚싯대가 길어야 깊은 놈을 만나지."],
		"done": "더 깊이, 더 큰 놈을 노려 보게.", "no": "돈이 모자라네. 고기를 더 팔고 오게.",
		"own": "그건 이미 자네 것이라네.", "skip": "앞의 것부터 써 보게. 순서가 있다네.",
		"tips": {}},
}
const SHOP_ORDER := ["bait", "market", "yard", "tackle"]

## 첫 출항 길잡이. 화면 위 띠에 한 줄씩 나오고 조건이 되면 다음으로 넘어간다. 일시정지 메뉴에서 끌 수 있다.
const GUIDE := [
	{"id": "gather", "text": "마을 왼쪽 끝으로 나가 채집지에서 재료를 줍자"},
	{"id": "craft", "text": "미끼 공방에 들어가 미끼를 만들자"},
	{"id": "board", "text": "마을 오른쪽 끝 부두에서 배를 타자"},
	{"id": "school", "text": "오른쪽으로 나가 새가 도는 곳(어군)을 찾자"},
	{"id": "anchor", "text": "여기다! Space 로 닻을 내리자"},
	{"id": "lower", "text": "↓ 로 미끼를 물고기가 있는 깊이까지 내리자"},
	{"id": "fight", "text": "버틸 땐 Space 를 떼고, 지치면 꾹 눌러 감자"},
	{"id": "return", "text": "더 낚아도 좋다. 어창이 차면 X 로 닻을 올리고 왼쪽 부두로 돌아가자"},
	{"id": "sell", "text": "어시장에서 물고기를 팔자"},
	{"id": "upgrade", "text": "돈을 모아 낚시 가게에서 더 긴 낚싯대를 사자"},
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

const WRECKED := "큰 파도에 배가 떠밀려 항구로 돌아왔다.\n어창의 절반을 잃었다. 조선소에서 배를 고치자."
const DELIVERED := "전설의 심해어를 용궁에 바쳤다.\n데모는 여기까지다. 바다는 열려 있으니 도감을 마저 채워도 좋다."

## 도감의 설명 한 줄.
const FISH_NOTES := {
	"anchovy": "얕은 물에 떼 지어 다닌다. 작지만 미끼로도 밥상으로도 귀하다.",
	"scad": "빠르게 치고 빠진다. 벌레를 보면 참지 못한다.",
	"flounder": "모래 바닥에 납작 엎드려 지나가는 것을 기다린다.",
	"mackerel": "먼바다 위쪽을 무리 지어 달린다.",
	"bream": "붉은 비늘이 고운 먼바다의 귀한 손님.",
	"amberjack": "크고 힘이 세다. 물면 옆으로 내달린다.",
	"wrasse": "암초의 얕은 틈을 들락거리는 알록달록한 녀석.",
	"rockfish": "암초 그늘에 가만히 숨어 있다. 가시를 조심.",
	"moray": "가라앉은 배 밑에 사는 뱀 같은 놈. 좀처럼 나오지 않는다.",
	"hairtail": "칼처럼 긴 은빛 몸. 심해 입구의 중간 물을 선 채로 떠다닌다.",
	"angler": "어둠 속에서 등불을 흔들어 먹이를 부른다.",
	"oarfish": "깊은 바닥 가까이를 길게 흐르는 심해의 사자.",
	"legend": "자개빛 비늘의 심해어. 용왕의 병을 고칠 단 하나의 영약.",
}


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
