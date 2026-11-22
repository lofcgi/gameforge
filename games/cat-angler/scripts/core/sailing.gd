class_name Sailing
extends RefCounted
## 배와 수면 위의 것들: 운항, 큰 파도와 내구도, 어군 표시, 떠다니는 물건.

const CELL := 320.0              # "화면 두 개 너비 안에 볼거리" 규칙의 칸 너비: 칸마다 하나는 있게 한다
const CREST_WIDTH := 16.0
const PICKUP_RANGE := 11.0
const DOCK_RANGE := 18.0
const SCHOOLS_WANTED := 6
const FLOTSAM_WANTED := 7

var x := 0.0
var vx := 0.0
var y := 0.0
var vy := 0.0
var tilt := 0.0
var crests: Array = []
var schools: Array = []
var flotsam: Array = []

var _crest_timer := 150
var _zone := 1
var _note := 0


static func left_limit() -> float:
	return Data.PIER_M * Data.X_PX


static func right_limit() -> float:
	return Data.SEA_END_M * Data.X_PX - 20.0


static func island_dock() -> float:
	return Sea.place_x("island") - 46.0


func _init() -> void:
	x = left_limit()
	# 첫 출항부터 바다가 비어 있지 않게 미리 채워 둔다.
	_upkeep()


func surface_y(px: float, tick: int) -> float:
	var height := Sea.ripple_y(px, tick)
	for crest in crests:
		var d: float = (px - crest["x"]) / CREST_WIDTH
		if absf(d) < 3.0:
			height -= crest_height(crest) * exp(-d * d)
	return height


func crest_height(crest: Dictionary) -> float:
	return Sea.blend(crest["x"], "crest") * crest["scale"] * minf(1.0, crest["age"] / 40.0)


## 닻을 내렸든 아니든 도는 부분: 큰 파도, 배의 오르내림, 어군과 물건의 생성.
func step_env(g: Game) -> void:
	_step_crests(g)
	var target := surface_y(x, g.tick)
	# 부력: 물이 차오르면 빨리 떠오르고, 물이 빠지면 천천히 내려앉는다.
	var stiffness := 260.0 if target < y else 70.0
	vy += ((target - y) * stiffness - vy * 12.0) / 60.0
	y += vy / 60.0
	var slope := atan2(surface_y(x + 9.0, g.tick) - surface_y(x - 9.0, g.tick), 18.0)
	tilt += (slope - tilt) * 0.12
	for school in schools:
		school["life"] -= 1
		school["age"] += 1
	schools = schools.filter(func(s): return s["life"] > 0)
	if g.tick % 60 == 0:
		_upkeep()


func step_drive(g: Game) -> void:
	var boat := g.inv.boat_data()
	var dir := int(g.held("right")) - int(g.held("left"))
	var speed: float = boat["speed"]
	if dir != 0:
		var push: float = boat["accel"] * (2.0 if signf(vx) == -dir else 1.0)
		vx += dir * push / 60.0
		if g.pressed("left") or g.pressed("right"):
			# 누른 순간 바로 움직임이 보이게 작은 첫 밀기를 준다.
			vx += dir * 10.0
			g.emit("paddle", {"dir": dir})
	else:
		vx -= vx * 1.3 / 60.0
		if absf(vx) < 1.0:
			vx = 0.0
	vx -= tilt * 14.0 / 60.0 * minf(1.0, absf(vx) / 20.0)
	vx = clampf(vx, -speed, speed)
	x += vx / 60.0
	if x < left_limit() or x > right_limit():
		x = clampf(x, left_limit(), right_limit())
		vx = 0.0
	_pick_flotsam(g)
	_announce_zone(g)
	if g.pressed("action") or g.pressed("down"):
		if at_pier():
			g.arrive_port()
		elif at_island():
			g.land.enter("island")
			g.mode = "land"
			vx = 0.0
			g.emit("dock", {})
		else:
			vx *= 0.4
			g.fishing.drop_anchor(g)


## 구간이 바뀌면 알리고, 배가 그 구간의 파도를 못 버티면 경고한다.
func _announce_zone(g: Game) -> void:
	var index := Sea.zone_index(x)
	if index == _zone or index == 0:
		return
	var entering := index > _zone
	_zone = index
	var zone: Dictionary = Data.ZONES[index]
	g.emit("zone", {"index": index})
	if entering and zone["grade"] > g.inv.boat_data()["grade"]:
		g.toast("%s: 이 배로는 파도가 버겁다. 내구도를 지켜보자." % zone["name"])
	else:
		g.toast("%s에 들어섰다." % zone["name"])


func sync_zone() -> void:
	_zone = maxi(1, Sea.zone_index(x))


func at_pier() -> bool:
	return x < left_limit() + 30.0


func at_island() -> bool:
	return absf(x - island_dock()) < DOCK_RANGE


func _step_crests(g: Game) -> void:
	_crest_timer -= 1
	if _crest_timer <= 0:
		_crest_timer = randi_range(190, 330)
		var spawn_x := x + randf_range(200.0, 270.0)
		if spawn_x < right_limit() + 200.0:
			crests.append({"x": spawn_x, "v": -randf_range(28.0, 44.0), "scale": randf_range(0.8, 1.2), "age": 0, "ahead": true})
	for crest in crests:
		crest["x"] += crest["v"] / 60.0
		crest["age"] += 1
		if crest["ahead"] and crest["x"] <= x:
			crest["ahead"] = false
			_meet_crest(g, crest)
	crests = crests.filter(func(c): return c["x"] > x - 260.0 and c["x"] > left_limit() - 40.0)


func _meet_crest(g: Game, crest: Dictionary) -> void:
	var excess: float = Sea.blend(crest["x"], "grade") - g.inv.boat_data()["grade"]
	if excess < 0.2:
		if crest_height(crest) > 2.0:
			g.emit("ride", {})
		return
	var damage := maxf(1.0, roundf(Data.WAVE_DAMAGE * excess * crest["scale"]))
	g.inv.durability = maxf(0.0, g.inv.durability - damage)
	vx -= 16.0
	vy -= 24.0
	g.freeze = 3
	g.emit("hit", {"damage": damage})
	if g.inv.durability <= 0.0:
		g.wreck()


func _pick_flotsam(g: Game) -> void:
	for item in flotsam:
		if absf(item["x"] - x) > PICKUP_RANGE:
			continue
		flotsam.erase(item)
		var rank := maxi(1, Sea.zone_index(item["x"]))
		var text := ""
		if item["kind"] == "bottle":
			var coins := 3 * rank
			g.inv.coins += coins
			text = "%s  +%d닢" % [Data.NOTES[_note % Data.NOTES.size()], coins]
			_note += 1
		elif randf() < 0.6:
			var coins := randi_range(4, 9) * rank
			g.inv.coins += coins
			text = "상자: +%d닢" % coins
		else:
			var mat: String = ["herb", "bug", "berry"][randi() % 3]
			g.inv.mats[mat] += 2
			text = "상자: %s +2" % Data.MATS[mat]["name"]
		g.picked += 1
		g.emit("pickup", {"x": item["x"], "text": text})
		g.toast(text)
		return


## 칸마다 어군·물건·장소 중 하나는 있게 채우고, 전체 수가 모자라면 더한다.
func _upkeep() -> void:
	var cells := int((right_limit() - left_limit()) / CELL) + 1
	var empty: Array = []
	for i in cells:
		var from := left_limit() + i * CELL
		if not _cell_has(from):
			empty.append(from)
	for from in empty:
		_spawn(from, randf() < 0.5)
	if schools.size() < SCHOOLS_WANTED:
		_spawn(left_limit() + (randi() % cells) * CELL, true)
	elif flotsam.size() < FLOTSAM_WANTED:
		_spawn(left_limit() + (randi() % cells) * CELL, false)


func _cell_has(from: float) -> bool:
	var inside := func(px: float) -> bool: return px >= from and px < from + CELL
	for school in schools:
		if inside.call(school["x"]):
			return true
	for item in flotsam:
		if inside.call(item["x"]):
			return true
	for id in Data.PLACES:
		if inside.call(Sea.place_x(id)):
			return true
	return false


func _spawn(from: float, school: bool) -> void:
	var px := 0.0
	for attempt in 6:
		px = clampf(from + randf_range(10.0, CELL - 10.0), left_limit() + 70.0, right_limit())
		if absf(px - x) > 190.0:
			break
	if school:
		var zone_id: String = Sea.zone_at(px)["id"]
		var options := Data.FISH.filter(func(f): return f["zone"] == zone_id and f["place"] == "")
		if options.is_empty():
			return
		var pick: Dictionary = options[randi() % options.size()]
		schools.append({"x": px, "sp": pick["id"], "life": randi_range(2700, 4800), "age": 0})
	else:
		flotsam.append({"x": px, "kind": "bottle" if randf() < 0.35 else "crate"})


func school_near(px: float, sp: String, reach := 70.0) -> bool:
	for school in schools:
		if school["sp"] == sp and absf(school["x"] - px) < reach:
			return true
	return false
