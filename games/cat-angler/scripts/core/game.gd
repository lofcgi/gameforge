class_name Game
extends RefCounted
## 결정적 게임 코어. 고정 틱마다 step 을 한 번 부른다. 화면은 이 상태와 events 를 읽기만 한다.
## 벽시계를 읽지 않고 난수는 전역 시드(브리지가 정한다)를 따른다.

const IDLE_KEYS := {
	"land": ["up", "down", "cancel"], "sail": ["up", "cancel"], "fish": [], "fight": ["up", "down", "bait"],
}

var tick := 0
var mode := "land"            # land(항구·섬), sail(운항), fish(닻 내림)
var freeze := 0               # 히트스톱: 남은 틱 동안 세계가 멈춘다
var events: Array = []        # 이번 틱에 일어난 일. 화면 연출이 읽고 main 이 비운다
var deaths := 0
var delivered := false
var picked := 0
var shrugs := 0

var inv := Inventory.new()
var sailing := Sailing.new()
var shoal := Shoal.new()
var fishing := Fishing.new()
var land := Land.new()
var menu := Menu.new()

var _held := {}
var _pressed := {}


func _init() -> void:
	menu.show_cards("intro", Data.INTRO)


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
	_advance()
	_pressed = {}


func _advance() -> void:
	if menu.busy():
		menu.step(self)
		return
	if pressed("codex") or pressed("hold"):
		if fishing.fighting:
			menu.denied += 1
			emit("deny", {})
		elif pressed("codex"):
			menu.open(self, "codex")
		else:
			menu.open_hold(self)
		return
	if pressed("bait") and mode != "fish":
		swap_bait()
	# 지금 모드에서 하는 일이 없는 키에도 반응은 준다(고양이가 귀를 움찔한다).
	for action in IDLE_KEYS[("fight" if fishing.fighting else mode)]:
		if pressed(action):
			shrugs += 1
			emit("shrug", {})
	match mode:
		"land":
			land.step(self)
		"sail":
			sailing.step_env(self)
			shoal.step(self)
			sailing.step_drive(self)
		"fish":
			sailing.step_env(self)
			shoal.step(self)
			if mode == "fish":
				fishing.step(self)


func swap_bait() -> void:
	if inv.cycle_bait():
		emit("bait", {})
	else:
		shrugs += 1
		emit("shrug", {})
		toast("바꿀 다른 미끼가 없다.")


func arrive_port() -> void:
	sailing.vx = 0.0
	mode = "land"
	land.enter("port")
	land.regrow()
	emit("dock", {})
	if inv.hold.has("legend"):
		inv.hold.erase("legend")
		menu.show_cards("ending", Data.ENDING)


## 내구도가 바닥났다: 항구로 떠밀려 오고 어창의 절반을 잃는다.
func wreck() -> void:
	deaths += 1
	for i in ceili(inv.hold.size() / 2.0):
		inv.hold.remove_at(randi() % inv.hold.size())
	inv.durability = inv.boat_data()["dur"] * 0.5
	fishing.reset()
	sailing.x = Sailing.left_limit()
	sailing.vx = 0.0
	sailing.sync_zone()
	sailing.crests.clear()
	mode = "land"
	land.enter("port")
	land.regrow()
	emit("wreck", {})
	menu.show_cards("wrecked", Data.WRECKED)


## 디버그 시작 설정. 형식과 키는 design/graybox-play.md 에 있다.
func apply_start(config: Dictionary) -> void:
	if config.is_empty():
		return
	menu.cards = [] if config.get("intro", "0") == "0" else menu.cards
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
	if config.has("x"):
		sailing.x = clampf(float(config["x"]) * Data.X_PX, Sailing.left_limit(), Sailing.right_limit())
		sailing.sync_zone()
		mode = "sail"


func snapshot() -> Dictionary:
	var on_land := mode == "land"
	var goal: Dictionary = Data.fish("legend")
	var schools := sailing.schools.map(func(s): return {"x": s["x"], "sp": s["sp"]})
	var hooked: String = fishing.engaged["id"] if fishing.fighting else ""
	var interest: String = fishing.engaged["state"] if fishing.engaged != null else ""
	return {
		"level": Sea.zone_at(land.x if on_land else sailing.x)["id"],
		"player": {
			"pos": [land.x, 0.0] if on_land else [sailing.x, snappedf(fishing.hook_y, 0.1)],
			"vel": [land.vx, 0.0] if on_land else [sailing.vx, fishing.hook_v],
		},
		"goal": {"pos": [Sea.place_x("vortex"), goal["dmin"] * Data.Y_PX], "reached": delivered},
		"deaths": deaths,
		"mode": mode, "area": land.area if on_land else "sea",
		"panel": menu.panel, "cursor": menu.cursor,
		"items_ok": menu.items.map(func(item): return item["ok"]) if menu.panel != "" else [],
		"pending": menu.pending,
		"card": menu.card if not menu.cards.is_empty() else -1, "card_kind": menu.card_kind if not menu.cards.is_empty() else "",
		"near": land.near["id"] if on_land and land.near != null else "",
		"stock": land.stock.duplicate(),
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
		"hops": land.hops, "denied": menu.denied, "shrugs": shrugs,
		"schools": schools, "flotsam": sailing.flotsam.map(func(f): return f["x"]),
	}
