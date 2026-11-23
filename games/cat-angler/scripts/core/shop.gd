class_name Shop
extends RefCounted
## 가게 안에서 일어나는 일: 주인의 대사(한 글자씩 찍힌다)와 가게마다 다른 거래.
## bait 미끼 공방(작업대), market 어시장(진열대), yard 조선소(선거), tackle 낚시 가게(벽의 낚싯대).

const TYPE_SPEED := 0.75      # 틱마다 찍히는 글자 수
const ANIM_TICKS := 48

var id := ""
var talk: Array = []          # 아직 남은 인사말. 비면 거래를 할 수 있다
var line := ""                # 대사 창의 글
var shown := 0.0              # 찍힌 글자 수
var cursor := 0
var items: Array = []         # {ok, do, arg}
var visits := {}
var anim := {}                # 화면 연출용 {kind, t, arg}. 틱으로 진행한다
var denied := 0
var steps := 0                # 대사를 넘긴 횟수


func data() -> Dictionary:
	return Data.SHOPS[id]


func talking() -> bool:
	return not talk.is_empty()


func typed() -> bool:
	return shown >= line.length()


func enter(g: Game, shop_id: String) -> void:
	id = shop_id
	cursor = 0
	anim = {}
	var seen: int = visits.get(id, 0)
	visits[id] = seen + 1
	if seen == 0:
		talk = data()["hello"].duplicate()
	else:
		talk = [data()["again"][(seen - 1) % data()["again"].size()]]
	_rebuild(g)
	_say(talk[0])


func _say(text: String) -> void:
	line = text
	shown = 0.0


func step(g: Game) -> void:
	shown = minf(line.length(), shown + TYPE_SPEED)
	if not anim.is_empty():
		anim["t"] += 1
		if anim["t"] >= ANIM_TICKS:
			anim = {}
	if talking():
		_step_talk(g)
		return
	var move := int(g.pressed("right") or g.pressed("down")) - int(g.pressed("left") or g.pressed("up"))
	if move != 0 and items.size() > 1:
		cursor = posmod(cursor + move, items.size())
		_say(_tip(g))
		g.emit("cursor", {})
	elif move != 0:
		denied += 1
		g.emit("deny", {})
	if g.pressed("action"):
		var item: Dictionary = items[cursor]
		if item["ok"]:
			_do(g, item)
			_rebuild(g)
		else:
			denied += 1
			_say(_refusal(g, item))
			g.emit("deny", {})
	if g.pressed("cancel"):
		g.emit("door", {})
		g.goto("town", "iris", {"spawn": id})


func _step_talk(g: Game) -> void:
	if g.pressed("cancel") or g.pressed("action"):
		steps += 1
	if g.pressed("cancel"):
		talk = []
	elif g.pressed("action"):
		if not typed():
			shown = line.length()
			g.emit("cursor", {})
			return
		talk.pop_front()
		g.emit("cursor", {})
	else:
		if g.pressed_other(["hold", "bait"]):
			denied += 1
			g.emit("deny", {})
		return
	_say(talk[0] if talking() else _tip(g))


func _rebuild(g: Game) -> void:
	var inv := g.inv
	items = []
	match id:
		"bait":
			for bait in Data.BAIT_ORDER:
				items.append({"ok": inv.can_craft(bait), "do": "craft", "arg": bait})
		"market":
			items.append({"ok": inv.hold_value() > 0, "do": "sell_all", "arg": ""})
			for fish in stacks(inv):
				items.append({"ok": fish != "legend", "do": "sell", "arg": fish})
		"yard":
			var cost := inv.repair_cost()
			items.append({"ok": cost > 0 and inv.coins >= cost, "do": "repair", "arg": ""})
			var next := inv.boat + 1
			items.append({"ok": next < Data.BOATS.size() and inv.coins >= Data.BOATS[mini(next, Data.BOATS.size() - 1)]["price"],
				"do": "upgrade", "arg": ""})
		"tackle":
			for tier in Data.RODS.size():
				items.append({"ok": tier == inv.rod + 1 and inv.coins >= Data.RODS[tier]["price"], "do": "buy_rod", "arg": tier})
	cursor = clampi(cursor, 0, items.size() - 1)


static func stacks(inv: Inventory) -> Array:
	var seen := []
	for fish in inv.hold:
		if not seen.has(fish):
			seen.append(fish)
	return seen


## 고른 것에 대한 주인의 한마디.
func _tip(g: Game) -> String:
	var item: Dictionary = items[cursor]
	var inv := g.inv
	match item["do"]:
		"craft":
			return data()["tips"][item["arg"]]
		"sell_all":
			if inv.hold_value() <= 0:
				return data()["no"]
			return "종을 치면 전부 사 갈게. 모두 %d닢이야." % inv.hold_value()
		"sell":
			if item["arg"] == "legend":
				return data()["legend"]
			var fish := Data.fish(item["arg"])
			return "%s(이)로군. 한 마리에 %d닢 쳐 줄게." % [fish["name"], fish["price"]]
		"repair":
			if inv.repair_cost() <= 0:
				return "배는 멀쩡해. 고칠 데가 없어."
			return "%s %d닢이면 돼." % [data()["tips"]["repair"], inv.repair_cost()]
		"upgrade":
			if inv.boat + 1 >= Data.BOATS.size():
				return data()["max"]
			var boat: Dictionary = Data.BOATS[inv.boat + 1]
			return "%s. %s %d닢이야." % [boat["name"], data()["tips"]["upgrade"], boat["price"]]
		"buy_rod":
			var rod: Dictionary = Data.RODS[item["arg"]]
			if item["arg"] <= inv.rod:
				return "%s. %s" % [rod["name"], data()["own"]]
			return "%s. %dm 깊이까지 닿고 힘은 %d이라네. %d닢일세." % [rod["name"], rod["reach"], rod["str"], rod["price"]]
	return ""


func _refusal(g: Game, item: Dictionary) -> String:
	var inv := g.inv
	match item["do"]:
		"sell":
			return data()["legend"]
		"repair":
			return "배는 멀쩡해. 고칠 데가 없어." if inv.repair_cost() <= 0 else data()["no"]
		"upgrade":
			return data()["max"] if inv.boat + 1 >= Data.BOATS.size() else data()["no"]
		"buy_rod":
			if item["arg"] <= inv.rod:
				return data()["own"]
			return data()["skip"] if item["arg"] > inv.rod + 1 else data()["no"]
	return data()["no"]


func _do(g: Game, item: Dictionary) -> void:
	var inv := g.inv
	anim = {"kind": item["do"], "t": 0, "arg": item["arg"]}
	match item["do"]:
		"craft":
			inv.craft(item["arg"])
			if inv.baits[inv.bait] <= 0:
				inv.bait = item["arg"]
			g.emit("craft", {"id": item["arg"]})
			_say(data()["done"])
		"sell_all":
			anim["fish"] = inv.hold.filter(func(fish): return fish != "legend")
			g.emit("sell", {"coins": inv.sell_all()})
			_say(data()["done"])
		"sell":
			g.emit("sell", {"coins": inv.sell_one(item["arg"])})
			_say(data()["done"])
		"repair":
			anim["from"] = inv.durability
			inv.coins -= inv.repair_cost()
			inv.durability = inv.boat_data()["dur"]
			g.emit("repair", {})
			_say(data()["fixed"])
		"upgrade":
			inv.boat += 1
			inv.coins -= inv.boat_data()["price"]
			inv.durability = inv.boat_data()["dur"]
			g.emit("buy", {"what": "boat"})
			_say(data()["done"])
		"buy_rod":
			inv.rod += 1
			inv.coins -= inv.rod_data()["price"]
			g.emit("buy", {"what": "rod"})
			_say(data()["done"])
