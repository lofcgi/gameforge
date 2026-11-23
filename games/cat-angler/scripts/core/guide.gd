class_name Guide
extends RefCounted
## 첫 출항 길잡이: 줍기 → 미끼 → 배 타기 → 어군 → 닻 → 내리기 → 줄다리기 → 귀항 → 팔기 → 낚싯대.
## 화면 위에 할 일 한 줄을 띄우고 갈 곳을 화살표로 가리킨다. 규칙에는 영향을 주지 않는다.

const NEAR_SCHOOL := 150.0

var on := true
var step := 0
var gathered := 0
var crafted := false
var sold := false
var changed := 0              # 할 일이 바뀐 틱(띠를 잠깐 반짝이게 한다)

var _note := ""               # 지금 상황에 맞춰 바꿔 쓴 할 일(미끼를 내릴 깊이처럼 상황마다 다른 것)


func done() -> bool:
	return step >= Data.GUIDE.size()


func id() -> String:
	return "" if done() else Data.GUIDE[step]["id"]


func text() -> String:
	if done() or not on:
		return ""
	return _note if _note != "" else Data.GUIDE[step]["text"]


func advance(g: Game) -> void:
	if done():
		return
	for e in g.events:
		match e["type"]:
			"gather":
				gathered += 1
			"craft":
				crafted = true
			"sell":
				sold = true
	var before := step
	# 조건이 이미 채워진 단계는 한꺼번에 넘긴다(바로 배를 타 버린 사람에게 줍기를 다시 시키지 않는다).
	for i in Data.GUIDE.size():
		if done() or not _passed(g):
			break
		step += 1
	# 물고기를 놓쳤으면 다시 미끼를 내리는 단계로, 어군에서 멀어졌으면 다시 찾는 단계로 돌아간다.
	if id() == "fight" and not g.fishing.fighting and g.fishing.catches == 0:
		step = _index("lower")
	if id() == "lower" and g.mode != "fish":
		step = _index("school")
	if id() == "anchor" and g.mode == "sail" and nearest_school(g) > NEAR_SCHOOL:
		step = _index("school")
	if step != before:
		changed = g.tick
	_note = _lower_note(g) if id() == "lower" else ""


## 지금 고른 미끼를 무는 어종(이 자리에 살고 낚싯대가 닿는 것). 어군이 있는 어종이 먼저다.
func biting(g: Game) -> Array:
	var x := g.sailing.x
	var zone: String = Sea.zone_at(x)["id"]
	var reach: float = g.inv.rod_data()["reach"]
	var found: Array = []
	for sp in Data.FISH:
		if sp["zone"] != zone or not sp["baits"].has(g.inv.bait) or sp["dmin"] >= reach:
			continue
		if sp["place"] != "" and not Sea.near_place(x, sp["place"], 20.0):
			continue
		if sp["dmin"] * Data.Y_PX >= Sea.bed_y(x):
			continue
		if g.sailing.school_near(x, sp["id"]):
			found.push_front(sp)
		else:
			found.append(sp)
	return found


## "미끼를 내리자"를 상황에 맞게: 어느 깊이까지인지, 미끼가 없거나 안 맞으면 어떻게 할지.
func _lower_note(g: Game) -> String:
	if g.inv.baits[g.inv.bait] <= 0:
		for other in g.inv.baits:
			if g.inv.baits[other] > 0:
				return "이 미끼는 다 썼다. Q 로 다른 미끼를 고르자"
		return "미끼가 없다. X 로 닻을 올리고 항구로 돌아가 미끼를 만들자"
	var list := biting(g)
	if list.is_empty():
		return "여기서는 이 미끼를 무는 고기가 없다. Q 로 미끼를 바꾸거나 X 로 자리를 옮기자"
	var sp: Dictionary = list[0]
	return "↓ 로 미끼를 %d~%dm 까지 내리자 (%s)" % [sp["dmin"], mini(sp["dmax"], int(g.inv.rod_data()["reach"])), sp["name"]]


func _index(name: String) -> int:
	for i in Data.GUIDE.size():
		if Data.GUIDE[i]["id"] == name:
			return i
	return Data.GUIDE.size()


func _passed(g: Game) -> bool:
	var at_sea := g.scene == "sea"
	match id():
		"gather":
			return gathered >= 3 or crafted or at_sea
		"craft":
			return crafted or at_sea
		"board":
			return at_sea
		"school":
			return g.mode == "fish" or (at_sea and nearest_school(g) <= NEAR_SCHOOL) or g.fishing.catches > 0
		"anchor":
			return g.mode == "fish" or g.fishing.catches > 0
		"lower":
			return g.fishing.fighting or g.fishing.catches > 0
		"fight":
			return g.fishing.catches > 0
		"return":
			return g.scene == "town" or g.scene.begins_with("in_") or sold
		"sell":
			return sold or (g.scene == "town" and g.inv.hold.is_empty())
		"upgrade":
			return g.inv.rod > 0
	return false


func nearest_school(g: Game) -> float:
	var best := INF
	for school in g.sailing.schools:
		best = minf(best, absf(school["x"] - g.sailing.x))
	return best


## 지금 화면에서 가리킬 곳. {"x": 화면 안의 x} 또는 {"dir": -1/1}(화면 끝 쪽) 또는 빈 사전.
func target(g: Game) -> Dictionary:
	if done() or not on:
		return {}
	var step_id := id()
	var town := Layout.of("places/town")
	match g.scene:
		"town":
			match step_id:
				"gather":
					return {"dir": -1}
				"craft":
					return {"x": town["doors"]["bait"]}
				"board", "school":
					return {"x": town["pier"]}
				"sell", "return":
					return {"x": town["doors"]["market"]} if not g.inv.hold.is_empty() else {}
				"upgrade":
					return {"x": town["doors"]["tackle"]} if g.inv.coins >= Data.RODS[1]["price"] else {"x": town["pier"]}
		"forage":
			if step_id == "gather":
				var best := {}
				for spot in g.walk.spots():
					if g.walk.stock[spot["mat"]][spot["index"]] and (best.is_empty() or absf(spot["x"] - g.walk.x) < absf(best["x"] - g.walk.x)):
						best = spot
				return {"x": best["x"]} if not best.is_empty() else {"dir": 1}
			return {"dir": 1}
		"sea":
			if step_id == "school" and g.mode == "sail":
				# 가진 미끼로 낚을 수 있는 어군을 먼저 가리킨다(없으면 가장 가까운 것).
				var best_x := INF
				var best_score := INF
				for school in g.sailing.schools:
					var sp := Data.fish(school["sp"])
					var usable := false
					for bait in sp["baits"]:
						usable = usable or g.inv.baits[bait] > 0
					var score: float = absf(school["x"] - g.sailing.x) + (0.0 if usable and sp["dmin"] < g.inv.rod_data()["reach"] else 4000.0)
					if score < best_score:
						best_score = score
						best_x = school["x"]
				return {"x": best_x} if best_x != INF else {"dir": 1}
			if step_id in ["sell", "upgrade"] or (step_id == "return" and g.mode == "sail" and g.inv.hold_used() >= g.inv.hold_cap()):
				return {"dir": -1}
	return {}
