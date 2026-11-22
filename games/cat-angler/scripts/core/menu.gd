class_name Menu
extends RefCounted
## 화면을 덮는 것: 가게·작업대·어창·도감 패널과 이야기 카드. 열려 있는 동안 바다는 멈춘다.

const TITLES := {"bench": "미끼 작업대", "market": "어시장", "shipyard": "조선소", "tackle": "낚시 가게",
	"hold": "어창", "codex": "도감"}

var panel := ""
var cursor := 0
var items: Array = []     # {text, right, ok, do, arg}
var say := ""
var pending := ""         # 어창이 가득 차 자리를 기다리는 방금 낚은 물고기
var cards: Array = []
var card := 0
var card_kind := ""
var denied := 0
var lock := 0             # 줄다리기 직후 감던 손이 그대로 "놓아주기"를 누르지 않게 잠깐 선택을 막는다


func busy() -> bool:
	return panel != "" or not cards.is_empty()


func show_cards(kind: String, texts: Array) -> void:
	card_kind = kind
	cards = texts
	card = 0


func open(g: Game, id: String) -> void:
	panel = id
	cursor = 0
	say = ""
	for station in Data.STATIONS:
		if station["id"] == id:
			say = station.get("say", "")
	_rebuild(g)
	g.emit("open", {})


func open_hold(g: Game, waiting := "") -> void:
	pending = waiting
	open(g, "hold")
	if waiting != "":
		lock = 45
		var fish := Data.fish(waiting)
		say = "가득! 놓아줄 것을 고른다. X: 방금 낚은 %s(%d닢) 놓아주기" % [fish["name"], fish["price"]]


func step(g: Game) -> void:
	if not cards.is_empty():
		_step_cards(g)
		return
	var move := int(g.pressed("down")) - int(g.pressed("up"))
	if move != 0 and not items.is_empty():
		cursor = posmod(cursor + move, items.size())
		g.emit("cursor", {})
	lock = maxi(0, lock - 1)
	if g.pressed("action") and not items.is_empty():
		var item: Dictionary = items[cursor]
		if item["ok"] and lock == 0:
			_do(g, item)
			if panel != "":
				_rebuild(g)
		else:
			denied += 1
			g.emit("deny", {})
	var toggle := (panel == "codex" and g.pressed("codex")) or (panel == "hold" and g.pressed("hold"))
	if g.pressed("cancel") or toggle:
		_close(g)


func _close(g: Game) -> void:
	if pending != "":
		g.toast("%s 놓아주었다." % Data.fish(pending)["name"])
		pending = ""
	panel = ""
	g.emit("close", {})


func _step_cards(g: Game) -> void:
	if g.pressed("cancel"):
		card = cards.size()
	elif g.pressed("action") or g.pressed("right") or g.pressed("down"):
		card += 1
		g.emit("card", {})
	if card >= cards.size():
		cards = []
		card = 0
		if card_kind == "ending":
			g.delivered = true
		g.emit("close", {})


func _item(text: String, right := "", ok := true, action := "", arg = null) -> Dictionary:
	return {"text": text, "right": right, "ok": ok, "do": action, "arg": arg}


func _rebuild(g: Game) -> void:
	var inv := g.inv
	items = []
	match panel:
		"bench":
			for id in Data.BAIT_ORDER:
				var bait: Dictionary = Data.BAITS[id]
				var need := []
				for mat in bait["cost"]:
					need.append("%s%d/%d" % [Data.MATS[mat]["name"], inv.mats[mat], bait["cost"][mat]])
				items.append(_item("%s x%d" % [bait["name"], inv.baits[id]], " ".join(need), inv.can_craft(id), "craft", id))
		"market":
			items.append(_item("모두 팔기", "+%d닢" % inv.hold_value(), inv.hold_value() > 0, "sell_all"))
			for id in _stacks(inv):
				var fish := Data.fish(id)
				if id == "legend":
					items.append(_item(fish["name"], "용궁에 바친다", false))
				else:
					items.append(_item("%s x%d" % [fish["name"], inv.hold.count(id)], "%d닢" % fish["price"], true, "sell", id))
		"shipyard":
			var cost := inv.repair_cost()
			items.append(_item("수리 %d/%d" % [inv.durability, inv.boat_data()["dur"]], "%d닢" % cost,
				cost > 0 and inv.coins >= cost, "repair"))
			for tier in range(inv.boat + 1, Data.BOATS.size()):
				var boat: Dictionary = Data.BOATS[tier]
				var sea: String = Data.ZONES.filter(func(z): return z["grade"] == boat["grade"])[0]["name"]
				items.append(_item("%s(%s) 내구%d 어창%d" % [boat["name"], sea, boat["dur"], boat["hold"]], "%d닢" % boat["price"],
					tier == inv.boat + 1 and inv.coins >= boat["price"], "buy_boat"))
		"tackle":
			for tier in range(inv.rod + 1, Data.RODS.size()):
				var rod: Dictionary = Data.RODS[tier]
				items.append(_item("%s %dm 힘%d" % [rod["name"], rod["reach"], rod["str"]], "%d닢" % rod["price"],
					tier == inv.rod + 1 and inv.coins >= rod["price"], "buy_rod"))
			if items.is_empty():
				items.append(_item("가장 좋은 낚싯대를 쓰고 있다", "", false))
		"hold":
			for i in inv.hold.size():
				var fish := Data.fish(inv.hold[i])
				items.append(_item("%s (%d칸)" % [fish["name"], fish["slots"]],
					"놓아주기" if inv.hold[i] == "legend" else "%d닢 · 놓아주기" % fish["price"], true, "release", i))
			if items.is_empty():
				items.append(_item("비어 있다", "", false))
		"codex":
			for fish in Data.FISH:
				items.append(_item(fish["name"] if inv.caught.has(fish["id"]) else "???", "", false, "", fish["id"]))
	cursor = clampi(cursor, 0, maxi(0, items.size() - 1))


func _stacks(inv: Inventory) -> Array:
	var seen := []
	for id in inv.hold:
		if not seen.has(id):
			seen.append(id)
	return seen


func _do(g: Game, item: Dictionary) -> void:
	var inv := g.inv
	match item["do"]:
		"craft":
			inv.craft(item["arg"])
			if inv.baits[inv.bait] <= 0:
				inv.bait = item["arg"]
			g.emit("craft", {})
		"sell_all":
			g.emit("sell", {"coins": inv.sell_all()})
		"sell":
			g.emit("sell", {"coins": inv.sell_one(item["arg"])})
		"repair":
			inv.coins -= inv.repair_cost()
			inv.durability = inv.boat_data()["dur"]
			g.emit("buy", {})
		"buy_boat":
			inv.boat += 1
			inv.coins -= inv.boat_data()["price"]
			inv.durability = inv.boat_data()["dur"]
			say = "비버: 새 배다! 더 먼 파도도 견딜 거야."
			g.emit("buy", {})
		"buy_rod":
			inv.rod += 1
			inv.coins -= inv.rod_data()["price"]
			say = "왜가리: 더 깊이, 더 큰 놈을 노려 보게."
			g.emit("buy", {})
		"release":
			var id: String = inv.hold[item["arg"]]
			inv.hold.remove_at(item["arg"])
			g.emit("release", {})
			if pending != "" and inv.fits(pending):
				inv.hold.append(pending)
				g.toast("%s 놓아주고 %s 실었다." % [Data.fish(id)["name"], Data.fish(pending)["name"]])
				pending = ""
				panel = ""
				g.emit("close", {})
