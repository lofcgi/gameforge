class_name Layout
## 그림 옆의 JSON(문, 재료 자리, 고양이가 앉는 자리)을 읽는다. 파일이 없거나 항목이 빠지면 아래 기본 배치를 쓴다.
## 규격은 design/asset-spec.md. 좌표는 그 그림의 픽셀(왼쪽 위가 0,0)이다.

const DEFAULTS := {
	"boats/boat1": {"size": [120, 40], "seat": [62, 20], "rod_tip": [118, -18], "waterline": 28},
	"boats/boat2": {"size": [168, 72], "seat": [98, 48], "rod_tip": [150, 6], "waterline": 58},
	"boats/boat3": {"size": [224, 96], "seat": [136, 66], "rod_tip": [188, 22], "waterline": 80},
	"chars/cat": {"canvas": [48, 56], "foot": [24, 55], "hand": [33, 34]},
	"places/town": {"size": [1600, 360], "doors": {"bait": 330, "market": 620, "yard": 930, "tackle": 1220}, "pier": 1500,
		"ground_y": 300, "left": 16, "right": 1560},
	"places/forage": {"size": [960, 360], "ground_y": 300,
		"herb": [[120, 300], [200, 300], [280, 300], [350, 300]],
		"bug": [[430, 300], [500, 300], [570, 300], [640, 300]],
		"berry": [[710, 300], [770, 300], [830, 300], [890, 300]]},
	"places/island": {"size": [640, 360], "ground_y": 270, "dock": 110, "left": 70, "right": 590, "flower": [[480, 270]]},
	"places/in_bait": {"keeper": [530, 250], "cat": [190, 256], "bench": [250, 186, 170, 22],
		"baskets": [[70, 130], [120, 130], [170, 130], [220, 130]], "out": [460, 176]},
	"places/in_market": {"keeper": [540, 250], "cat": [80, 256], "table": [140, 140, 260, 96], "scale": [460, 170]},
	"places/in_yard": {"keeper": [560, 256], "cat": [60, 256], "dock": [230, 206], "preview": [400, 56, 190, 110]},
	"places/in_tackle": {"keeper": [540, 250], "cat": [100, 256], "rods": [[230, 128], [320, 128], [410, 128]]},
	"ui/codex_book": {"left": [44, 40, 260, 280], "right": [336, 40, 260, 280]},
}

static var _cache := {}


## name 은 assets/game 아래의 경로에서 확장자를 뺀 것(예: "places/town").
static func of(name: String) -> Dictionary:
	if _cache.has(name):
		return _cache[name]
	var merged: Dictionary = DEFAULTS.get(name, {}).duplicate(true)
	var path := "res://assets/game/%s.json" % name
	if FileAccess.file_exists(path):
		var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if parsed is Dictionary:
			for key in parsed:
				merged[key] = parsed[key]
		else:
			push_error("JSON 을 읽지 못했다: " + path)
	_cache[name] = merged
	return merged


static func point(name: String, key: String) -> Vector2:
	var value: Array = of(name)[key]
	return Vector2(value[0], value[1])


static func area(name: String, key: String) -> Rect2:
	var value: Array = of(name)[key]
	return Rect2(value[0], value[1], value[2], value[3])


static func points(name: String, key: String) -> Array:
	var list: Array = []
	for value in of(name).get(key, []):
		list.append(Vector2(value[0], value[1]))
	return list


## 배의 기준점(그림의 가로 가운데, 흘수선)에서 본 자리들. 배가 오른쪽을 볼 때의 값이다.
static func boat(tier: int) -> Dictionary:
	var name := "boats/boat%d" % (tier + 1)
	var data := of(name)
	var size := Vector2(data["size"][0], data["size"][1])
	var tex_path := "boats/boat%d.png" % (tier + 1)
	if Assets.exists(tex_path):
		size = Assets.tex(tex_path).get_size()
	var pivot := Vector2(floorf(size.x / 2.0), data["waterline"])
	# sink: 고양이를 이만큼 내려 앉혀 발이 뱃전 뒤로 숨게 한다.
	var seat := point(name, "seat") - pivot + Vector2(0, data.get("sink", 8))
	# 낚싯대가 고양이 그림 안에 있으면(chars/cat.json 의 rod_tip) 낚싯대 끝은 앉은 자리에서 정해진다.
	var tip = cat_rod_tip("sit_fish", 0)
	return {"size": size, "pivot": pivot, "seat": seat, "rim": point(name, "seat").y,
		"rod_tip": seat + tip if tip != null else point(name, "rod_tip") - pivot}


static func cat_foot() -> Vector2:
	return point("chars/cat", "foot")


## 고양이 그림 속 낚싯대 끝(발밑에서 본 자리). 그림에 낚싯대가 없으면 null.
static func cat_rod_tip(action: String, frame: int):
	var tips: Dictionary = of("chars/cat").get("rod_tip", {})
	if tips.is_empty():
		return null
	var list: Array = tips.get(action, tips.get("sit_fish", []))
	if list.is_empty():
		return null
	var at: Array = list[clampi(frame, 0, list.size() - 1)]
	return Vector2(at[0], at[1]) - cat_foot()


static var _reach := {}


## 낚싯대 끝이 배의 가운데에서 오른쪽으로 얼마나 나가 있는가(px). 미끼가 내려가는 자리다.
static func boat_reach(tier: int) -> float:
	if not _reach.has(tier):
		_reach[tier] = boat(tier)["rod_tip"].x
	return _reach[tier]


## 장소 그림의 너비. 진짜 그림이 있으면 그 크기를 따른다.
static func width(name: String) -> float:
	if Assets.exists(name + ".png"):
		return Assets.tex(name + ".png").get_width()
	return of(name)["size"][0]
