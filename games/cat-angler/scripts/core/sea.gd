class_name Sea
## 바다의 모양: 구간, 바닥 깊이, 잔물결. 모두 x(px)와 틱만으로 정해지는 순수 함수다.

const BLEND_M := 50.0
const TABLE_FROM := -400.0
const TABLE_STEP := 4.0
const TABLE_SIZE := 1400

static var _tables := {}


static func zone_index(x: float) -> int:
	var m := x / Data.X_PX
	for i in Data.ZONES.size():
		if m < Data.ZONES[i]["to"]:
			return i
	return Data.ZONES.size() - 1


static func zone_at(x: float) -> Dictionary:
	return Data.ZONES[zone_index(x)]


## 구간 경계에서 값이 서서히 바뀐다. 매 틱 수백 번 불리므로 표에서 읽는다.
static func blend(x: float, key: String) -> float:
	return _lookup(key, x)


static func _blend_exact(x: float, key: String) -> float:
	var m := x / Data.X_PX
	var value: float = Data.ZONES[0][key]
	for i in range(1, Data.ZONES.size()):
		var edge: float = Data.ZONES[i]["from"]
		value = lerpf(value, Data.ZONES[i][key], smoothstep(edge - BLEND_M, edge + BLEND_M, m))
	return value


static func _lookup(key: String, x: float) -> float:
	if not _tables.has(key):
		var table := PackedFloat32Array()
		for i in TABLE_SIZE:
			var px := TABLE_FROM + i * TABLE_STEP
			table.append(_bed_exact(px) if key == "bed" else _blend_exact(px, key))
		_tables[key] = table
	var values: PackedFloat32Array = _tables[key]
	var at := clampf((x - TABLE_FROM) / TABLE_STEP, 0.0, TABLE_SIZE - 1.001)
	var index := int(at)
	return lerpf(values[index], values[index + 1], at - index)


static func blend_color(x: float, key: String) -> Color:
	var m := x / Data.X_PX
	var value: Color = Data.ZONES[0][key]
	for i in range(1, Data.ZONES.size()):
		var edge: float = Data.ZONES[i]["from"]
		value = value.lerp(Data.ZONES[i][key], smoothstep(edge - BLEND_M, edge + BLEND_M, m))
	return value


## 바닥 깊이(px). 구간 경계에서 비탈로 내려가고 암초에서 솟는다.
static func bed_y(x: float) -> float:
	return _lookup("bed", x)


static func _bed_exact(x: float) -> float:
	var m := x / Data.X_PX
	var depth := 0.0
	for i in range(1, Data.ZONES.size()):
		var edge: float = Data.ZONES[i]["from"]
		depth = lerpf(depth, Data.ZONES[i]["bed"], smoothstep(edge, edge + 90.0, m))
	var reef: Dictionary = Data.PLACES["reef"]
	var half: float = reef["w"] * 0.5
	var bump := 1.0 - smoothstep(half * 0.45, half, absf(m - reef["x"]))
	depth = lerpf(depth, reef["top"], bump)
	return depth * Data.Y_PX


static func ripple_y(x: float, tick: int) -> float:
	var t := tick / 60.0
	var wave := 0.55 * sin(x * 0.045 - t * 1.6) + 0.3 * sin(x * 0.021 + t * 1.1 + 1.3) + 0.2 * sin(x * 0.09 - t * 2.3 + 4.0)
	return blend(x, "amp") * wave


static func place_x(id: String) -> float:
	return Data.PLACES[id]["x"] * Data.X_PX


static func near_place(x: float, id: String, margin_m := 0.0) -> bool:
	var place: Dictionary = Data.PLACES[id]
	return absf(x / Data.X_PX - place["x"]) <= place["w"] * 0.5 + margin_m
