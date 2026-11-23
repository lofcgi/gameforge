class_name Walk
extends RefCounted
## 걸어 다니는 화면 셋: 항구 마을(town), 채집지(forage), 섬(island). 문 들어가기, 줍기, 배 타기, 화면 끝으로 나가기.
## 배치는 그림 옆의 JSON(Layout)에서 온다.

const SPEED := 150.0
const REACH := 26.0
const PICK_TICKS := 16
const DOOR_ORDER := ["bait", "market", "yard", "tackle"]

var area := "town"
var x := 420.0
var vx := 0.0
var facing := 1.0
var near = null               # 닿는 거리 안의 것 하나 {id, kind, x, y, mat, index}
var hops := 0
var pick_t := 0               # 줍는 동작이 끝날 때까지 남은 틱
var stock := {}               # 재료 -> 자리마다 남았는가

var _spots := {}


func _init() -> void:
	regrow()


func layout() -> Dictionary:
	return Layout.of("places/" + area)


func ground() -> float:
	return layout()["ground_y"]


func bounds() -> Vector2:
	var data := layout()
	return Vector2(data.get("left", 16.0), data.get("right", Layout.width("places/" + area) - 16.0))


## 이 화면에서 손댈 수 있는 것들.
func spots() -> Array:
	if _spots.has(area):
		return _spots[area]
	var data := layout()
	var list: Array = []
	match area:
		"town":
			for id in DOOR_ORDER:
				list.append({"id": id, "kind": "door", "x": float(data["doors"][id]), "y": ground()})
			list.append({"id": "pier", "kind": "board", "x": float(data["pier"]), "y": ground()})
		"forage":
			for mat in ["herb", "bug", "berry"]:
				_add_gather(list, data, mat)
		"island":
			list.append({"id": "dock", "kind": "board", "x": float(data["dock"]), "y": ground()})
			_add_gather(list, data, "flower")
	_spots[area] = list
	return list


func _add_gather(list: Array, data: Dictionary, mat: String) -> void:
	var points: Array = data.get(mat, [])
	for i in points.size():
		list.append({"id": mat, "kind": "gather", "x": float(points[i][0]), "y": float(points[i][1]), "mat": mat, "index": i})


static func spot_count(mat: String) -> int:
	var name := "places/island" if mat == "flower" else "places/forage"
	return Layout.of(name).get(mat, []).size()


## 한 자리에서 줍는 양. 종류마다 한 번 나갈 때 GATHER_YIELD 개가 되게 나눈다(섬꽃은 자리마다 하나).
static func spot_yield(mat: String) -> int:
	if mat == "flower":
		return 1
	return maxi(1, ceili(Data.GATHER_YIELD / float(maxi(1, spot_count(mat)))))


func regrow() -> void:
	for mat in ["herb", "bug", "berry", "flower"]:
		var fresh: Array = []
		fresh.resize(spot_count(mat))
		fresh.fill(true)
		stock[mat] = fresh


func remaining(mat: String) -> int:
	return stock[mat].count(true) * spot_yield(mat)


func enter(where: String, spawn: String) -> void:
	area = where
	vx = 0.0
	pick_t = 0
	near = null
	var data := layout()
	var edge := bounds()
	match spawn:
		"left":
			x = edge.x + 12.0
			facing = 1.0
		"right":
			x = edge.y - 12.0
			facing = -1.0
		"pier":
			x = data["pier"] - 30.0
			facing = -1.0
		"dock":
			x = data["dock"] + 24.0
			facing = 1.0
		"start":
			x = data["doors"]["bait"] + 70.0
			facing = -1.0
		_:
			if where == "town" and data["doors"].has(spawn):
				x = data["doors"][spawn]
				facing = 1.0


func step(g: Game) -> void:
	if pick_t > 0:
		pick_t -= 1
		vx = 0.0
		# 줍는 동안 누른 키는 받지 않지만 누른 것은 센다.
		if g.pressed("action") or g.pressed("left") or g.pressed("right"):
			g.taps += 1
		return
	var dir := int(g.held("right")) - int(g.held("left"))
	if dir != 0:
		facing = dir
	vx += (dir * SPEED - vx) * 0.35
	if absf(vx) < 1.0:
		vx = 0.0
	var edge := bounds()
	x += vx / 60.0
	# 화면 끝: 마을 왼쪽은 채집지로, 채집지 오른쪽은 마을로 이어진다.
	if area == "town" and x <= edge.x and dir < 0:
		g.goto("forage", "fade", {"spawn": "right"})
	elif area == "forage" and x >= edge.y and dir > 0:
		g.goto("town", "fade", {"spawn": "left"})
	x = clampf(x, edge.x, edge.y)
	near = null
	var best := REACH
	for spot in spots():
		var d := absf(spot["x"] - x)
		if d >= best or (spot["kind"] == "gather" and not stock[spot["mat"]][spot["index"]]):
			continue
		best = d
		near = spot
	var enter_door: bool = g.pressed("up") and near != null and near["kind"] == "door"
	if not (g.pressed("action") or enter_door):
		return
	if near == null:
		hops += 1
		g.emit("hop", {})
		return
	match near["kind"]:
		"gather":
			_gather(g, near)
		"door":
			g.emit("door", {})
			g.goto(Data.SHOPS[near["id"]]["scene"], "iris", {})
		"board":
			g.goto("sea", "iris", {"at": "island" if area == "island" else "pier"})


func _gather(g: Game, spot: Dictionary) -> void:
	var mat: String = spot["mat"]
	var amount := spot_yield(mat)
	stock[mat][spot["index"]] = false
	g.inv.mats[mat] += amount
	pick_t = PICK_TICKS
	facing = 1.0 if spot["x"] >= x else -1.0
	g.emit("gather", {"id": mat, "amount": amount, "x": spot["x"], "y": spot["y"]})
