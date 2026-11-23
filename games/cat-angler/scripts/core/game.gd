class_name Game
extends RefCounted
## 결정적 게임 코어. 고정 틱마다 step 을 한 번 부른다. 화면은 이 상태와 events 를 읽기만 한다.
## 벽시계를 읽지 않고 난수는 전역 시드(브리지가 정한다)를 따른다.
##
## scene 이 지금 화면이다: title, intro, town, forage, in_bait, in_market, in_yard, in_tackle, sea, island, ending.
## 화면을 바꿀 때는 goto 를 부른다. 전환 연출의 앞 절반이 지나 화면이 가려진 틱에 scene 이 바뀐다.

const TRANS_HALF := 14
const IDLE_KEYS := {"sail": ["up"], "fish": [], "fight": ["up", "down", "bait"]}

var tick := 0
var scene := "title"
var mode := "title"           # title, cut(컷신), land(걷기), shop(가게 안), sail(운항), fish(닻 내림)
var trans := {}               # 진행 중인 전환 {to, kind, t, args}
var freeze := 0               # 히트스톱: 남은 틱 동안 세계가 멈춘다
var events: Array = []        # 이번 틱에 일어난 일. 화면 연출이 읽고 main 이 비운다
var deaths := 0
var delivered := false
var picked := 0
var shrugs := 0
var taps := 0
var debug := false
var cut := {"kind": "", "skip": false, "done": false}

var inv := Inventory.new()
var sailing := Sailing.new()
var shoal := Shoal.new()
var fishing := Fishing.new()
var walk := Walk.new()
var shop := Shop.new()
var menu := Menu.new()
var guide := Guide.new()

var _held := {}
var _pressed := {}


func _init() -> void:
	menu.open(self, "title")


func held(action: String) -> bool:
	return _held.get(action, false)


func pressed(action: String) -> bool:
	return _pressed.get(action, false)


func emit(type: String, data: Dictionary) -> void:
	data["type"] = type
	events.append(data)


func toast(text: String) -> void:
	emit("toast", {"text": text})


func step(held_now: Dictionary, pressed_now: Dictionary) -> void:
	_held = held_now
	# 히트스톱 중에 누른 키를 잃지 않게 모아 둔다.
	for action in pressed_now:
		if pressed_now[action]:
			_pressed[action] = true
	if freeze > 0:
		freeze -= 1
		return
	tick += 1
	if pressed("debug"):
		debug = not debug
	_advance()
	guide.advance(self)
	_pressed = {}


func _advance() -> void:
	if not trans.is_empty():
		_step_trans()
		return
	if menu.busy():
		menu.step(self)
		return
	match scene:
		"intro", "ending":
			_step_cut()
		"town", "forage", "island":
			_step_walk()
		"sea":
			_step_sea()
		_:
			_step_shop()


# ---- 화면 전환 ----

func goto(to: String, kind := "fade", args := {}) -> void:
	if not trans.is_empty():
		return
	trans = {"to": to, "kind": kind, "t": 0, "args": args}
	emit("transition", {"kind": kind, "to": to})


## 이번 틱에 눌린 키 가운데 names 에 없는 것이 있는가(하는 일이 없는 키에도 반응을 주려고 쓴다).
func pressed_other(names: Array) -> bool:
	for action in _pressed:
		if action != "debug" and not names.has(action):
			return true
	return false


func transitioning() -> bool:
	return not trans.is_empty()


## 전환 중에는 입력을 받지 않는다(누른 횟수만 센다). 가운데 틱에 화면이 바뀐다.
func _step_trans() -> void:
	for action in _pressed:
		if action != "debug":
			taps += 1
	trans["t"] += 1
	if trans["t"] == TRANS_HALF:
		_enter(trans["to"], trans["args"])
	elif trans["t"] >= TRANS_HALF * 2:
		trans = {}


func _enter(to: String, args: Dictionary) -> void:
	scene = to
	match to:
		"title":
			mode = "title"
			menu.open(self, "title")
		"intro", "ending":
			mode = "cut"
			cut = {"kind": to, "skip": false, "done": false}
		"town", "forage", "island":
			mode = "land"
			if to == "town":
				sailing.x = Sailing.left_limit()
				sailing.vx = 0.0
				sailing.sync_zone()
				sailing.crests.clear()
			if args.has("spawn"):
				walk.enter(to, args["spawn"])
			else:
				walk.area = to
				walk.x = clampf(walk.x, walk.bounds().x, walk.bounds().y)
			# 닫는 컷신에서 돌아왔다: 전설의 심해어를 바친 것으로 적는다(화면이 마을로 넘어온 뒤에야 목표 달성이 된다).
			if args.get("delivered", false):
				delivered = true
			if to == "town":
				Save.write(self)
			if args.has("notice"):
				menu.open(self, "notice", args["notice"])
		"sea":
			mode = "sail"
			match args.get("at", ""):
				"pier":
					sailing.x = Sailing.left_limit()
				"island":
					sailing.x = Sailing.island_dock()
			sailing.vx = 0.0
			sailing.sync_zone()
			fishing.reset()
			emit("board", {})
		_:
			mode = "shop"
			for id in Data.SHOPS:
				if Data.SHOPS[id]["scene"] == to:
					shop.enter(self, id)
	emit("enter", {"scene": to})


func new_game() -> void:
	inv = Inventory.new()
	sailing = Sailing.new()
	shoal = Shoal.new()
	fishing = Fishing.new()
	walk = Walk.new()
	shop = Shop.new()
	guide = Guide.new()
	deaths = 0
	delivered = false
	picked = 0
	goto("intro", "fade", {})


func continue_game() -> void:
	var data := Save.read()
	if data.is_empty():
		new_game()
		return
	goto(Save.apply(self, data), "iris", {})


# ---- 컷신 ----

## 컷신 씬이 finished 를 냈을 때 화면(CutsceneHost)이 부른다.
func cut_done() -> void:
	cut["done"] = true


func _step_cut() -> void:
	for action in _pressed:
		if action != "debug":
			taps += 1
	if pressed("cancel") and not cut["skip"]:
		cut["skip"] = true
		emit("skip", {})
	if pressed("action"):
		emit("cut_action", {})
	if not cut["done"]:
		return
	if cut["kind"] == "intro":
		goto("town", "fade", {"spawn": "start"})
	else:
		goto("town", "fade", {"spawn": "pier", "notice": Data.DELIVERED, "delivered": true})


# ---- 걷는 화면과 가게 ----

func _step_walk() -> void:
	if pressed("pause") or pressed("cancel"):
		menu.open(self, "pause")
		return
	if pressed("codex"):
		menu.open(self, "codex")
		return
	if pressed("hold"):
		menu.open(self, "hold")
		return
	if pressed("bait"):
		swap_bait()
	var at_door: bool = walk.near != null and walk.near["kind"] == "door"
	if pressed("down") or (pressed("up") and not at_door):
		shrug()
	walk.step(self)


func _step_shop() -> void:
	if pressed("pause"):
		menu.open(self, "pause")
		return
	if pressed("codex"):
		menu.open(self, "codex")
		return
	if pressed("hold") or pressed("bait"):
		shrug()
	shop.step(self)


func shrug() -> void:
	shrugs += 1
	emit("shrug", {})


# ---- 바다 ----

func _step_sea() -> void:
	if pressed("pause") or (mode == "sail" and pressed("cancel")):
		menu.open(self, "pause")
		return
	if pressed("codex") or pressed("hold"):
		if fishing.fighting:
			menu.denied += 1
			emit("deny", {})
		else:
			menu.open(self, "codex" if pressed("codex") else "hold")
		return
	if pressed("bait") and mode != "fish":
		swap_bait()
	# 지금 하는 일이 없는 키에도 반응은 준다(고양이가 귀를 움찔한다).
	for action in IDLE_KEYS[("fight" if fishing.fighting else mode)]:
		if pressed(action):
			shrug()
	sailing.step_env(self)
	if not trans.is_empty():
		return
	shoal.step(self)
	if mode == "sail":
		sailing.step_drive(self)
	elif mode == "fish":
		fishing.step(self)


func swap_bait() -> void:
	if inv.cycle_bait():
		emit("bait", {})
	else:
		shrug()
		toast("바꿀 다른 미끼가 없다.")


func arrive_port() -> void:
	sailing.vx = 0.0
	walk.regrow()
	emit("dock", {})
	if inv.hold.has("legend"):
		inv.hold.erase("legend")
		goto("ending", "fade", {})
	else:
		goto("town", "iris", {"spawn": "pier"})


func dock_island() -> void:
	emit("dock", {})
	goto("island", "iris", {"spawn": "dock"})


## 내구도가 바닥났다: 항구로 떠밀려 오고 어창의 절반을 잃는다.
func wreck() -> void:
	deaths += 1
	for i in ceili(inv.hold.size() / 2.0):
		inv.hold.remove_at(randi() % inv.hold.size())
	inv.durability = inv.boat_data()["dur"] * 0.5
	fishing.reset()
	mode = "sail"
	walk.regrow()
	emit("wreck", {})
	goto("town", "fade", {"spawn": "pier", "notice": Data.WRECKED})


## 디버그 시작 설정. 형식과 키는 design/play-guide.md 에 있다. 타이틀과 여는 컷신을 건너뛴다.
func apply_start(config: Dictionary) -> void:
	if config.is_empty():
		return
	menu.kind = ""
	inv.coins = int(config.get("coins", "0"))
	inv.rod = clampi(int(config.get("rod", "1")) - 1, 0, Data.RODS.size() - 1)
	inv.boat = clampi(int(config.get("boat", "1")) - 1, 0, Data.BOATS.size() - 1)
	inv.durability = float(config.get("dur", str(inv.boat_data()["dur"])))
	for id in inv.baits:
		inv.baits[id] = int(config.get("baits", str(inv.baits[id])))
	if config.has("legendbait"):
		inv.baits["legend"] = int(config["legendbait"])
	for id in inv.mats:
		inv.mats[id] = int(config.get("mats", "0"))
	if config.has("bait"):
		inv.bait = config["bait"]
	for id in config.get("hold", "").split("+", false):
		inv.hold.append(id)
	for id in config.get("caught", "").split("+", false):
		inv.caught[id] = 1
	if config.get("guide", "1") == "0":
		guide.on = false
	var where: String = config.get("scene", "town")
	var args := {"spawn": config.get("spawn", "start" if where == "town" else ("dock" if where == "island" else "right"))}
	if config.has("x"):
		where = "sea"
		sailing.x = clampf(float(config["x"]) * Data.X_PX, Sailing.left_limit(), Sailing.right_limit())
	if config.get("intro", "0") == "1":
		where = "intro"
	_enter(where, args)
	events.clear()


func snapshot() -> Dictionary:
	var at_sea := scene == "sea"
	var goal: Dictionary = Data.fish("legend")
	var schools := sailing.schools.map(func(s): return {"x": s["x"], "sp": s["sp"]})
	var hooked: String = fishing.engaged["id"] if fishing.fighting else ""
	var interest: String = fishing.engaged["state"] if fishing.engaged != null else ""
	var in_shop := mode == "shop"
	var panel := menu.kind
	if panel == "" and in_shop and not shop.talking() and trans.is_empty():
		panel = shop.data()["panel"]
	var list: Array = menu.items if menu.kind != "" else (shop.items if in_shop else [])
	var state := {
		"level": Sea.zone_at(sailing.x)["id"] if at_sea else scene,
		"player": {
			"pos": [sailing.x, snappedf(fishing.hook_y, 0.1)] if at_sea else [snappedf(walk.x, 0.1), 0.0],
			"vel": [sailing.vx, fishing.hook_v] if at_sea else [walk.vx, 0.0],
		},
		"goal": {"pos": [Sea.place_x("vortex"), goal["dmin"] * Data.Y_PX], "reached": delivered},
		"deaths": deaths,
		"scene": scene, "mode": mode, "transition": not trans.is_empty(),
		"panel": panel, "cursor": menu.cursor if menu.kind != "" else (shop.cursor if in_shop else 0),
		"items_ok": list.map(func(item): return item["ok"]),
		"talking": in_shop and shop.talking(), "talk_steps": shop.steps, "pending": menu.pending,
		"cut_skip": cut["skip"], "taps": taps,
		"near": walk.near["id"] if mode == "land" and walk.near != null else "",
		"stock": {"herb": walk.remaining("herb"), "bug": walk.remaining("bug"), "berry": walk.remaining("berry"),
			"flower": walk.remaining("flower")},
		"spots": walk.stock.duplicate(true),
		"boat": {"x": snappedf(sailing.x, 0.1), "m": snappedf(sailing.x / Data.X_PX, 0.1), "tier": inv.boat + 1,
			"durability": inv.durability, "at_pier": sailing.at_pier(), "at_island": sailing.at_island()},
		"rod": inv.rod + 1, "coins": inv.coins,
		"hold": inv.hold.duplicate(), "hold_used": inv.hold_used(), "hold_cap": inv.hold_cap(),
		"mats": inv.mats.duplicate(), "baits": inv.baits.duplicate(), "bait": inv.bait,
		"depth": snappedf(fishing.hook_y / Data.Y_PX, 0.1), "reach": inv.rod_data()["reach"],
		"bed": snappedf(Sea.bed_y(fishing.hook_x(self)) / Data.Y_PX, 0.1),
		"interest": interest, "hooked": hooked, "phase": fishing.phase if fishing.fighting else "",
		"tension": snappedf(fishing.tension, 0.001), "stamina": snappedf(fishing.stamina, 0.001) if fishing.fighting else 1.0,
		"off": snappedf(fishing.off, 0.1) if fishing.fighting else 0.0, "reeling": fishing.reeling,
		"caught": inv.caught.size(), "caught_ids": inv.caught.keys(), "catches": fishing.catches, "snaps": fishing.snaps, "slips": fishing.slips,
		"picked": picked, "jigs": fishing.jigs, "nudges": fishing.nudges, "limit_hits": fishing.limit_hits,
		"hops": walk.hops, "denied": menu.denied + shop.denied, "shrugs": shrugs,
		"schools": schools, "flotsam": sailing.flotsam.map(func(f): return f["x"]),
		"guide": guide.id() if guide.on else "", "debug": debug,
		"missing_count": Assets.missing.size(),
	}
	if debug:
		state["missing_assets"] = Assets.missing_list()
	return state
