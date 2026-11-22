class_name Land
extends RefCounted
## 걸어 다니는 곳: 항구와 작은 섬. 채집, 가게 열기, 배 타기.

const WALK_SPEED := 78.0
const REACH := 15.0

var area := "port"
var x: float = Data.PORT_SPAWN
var vx := 0.0
var facing := 1.0
var stock := {}
var near = null
var hops := 0


func _init() -> void:
	regrow()


func regrow() -> void:
	stock = {"herb": Data.GATHER_YIELD, "bug": Data.GATHER_YIELD, "berry": Data.GATHER_YIELD, "flower": 1}


func origin() -> float:
	return Sea.place_x("island") if area == "island" else 0.0


func stations() -> Array:
	return Data.ISLAND_STATIONS if area == "island" else Data.STATIONS


func bounds() -> Vector2:
	if area == "island":
		return Vector2(origin() - 44.0, origin() + 52.0)
	return Vector2(Data.PORT_LEFT, Data.PORT_RIGHT)


func enter(where: String) -> void:
	area = where
	vx = 0.0
	x = origin() - 40.0 if where == "island" else 588.0
	facing = 1.0 if where == "island" else -1.0


func step(g: Game) -> void:
	var dir := int(g.held("right")) - int(g.held("left"))
	if dir != 0:
		facing = dir
	vx += (dir * WALK_SPEED - vx) * 0.4
	if absf(vx) < 0.5:
		vx = 0.0
	x = clampf(x + vx / 60.0, bounds().x, bounds().y)
	near = null
	for station in stations():
		if absf(origin() + station["x"] - x) < REACH:
			near = station
	if not g.pressed("action"):
		return
	if near == null:
		hops += 1
		g.emit("hop", {})
		return
	match near["kind"]:
		"gather":
			_gather(g, near["id"])
		"panel":
			g.menu.open(g, near["id"])
		"board":
			g.sailing.x = Sailing.island_dock() if area == "island" else Sailing.left_limit()
			g.sailing.vx = 0.0
			g.mode = "sail"
			g.emit("board", {})


func _gather(g: Game, id: String) -> void:
	var amount: int = stock[id]
	if amount <= 0:
		hops += 1
		g.emit("empty", {})
		g.toast("다 땄다. 출항하고 돌아오면 다시 자란다.")
		return
	stock[id] = 0
	g.inv.mats[id] += amount
	g.emit("gather", {"id": id, "amount": amount})
	g.toast("%s +%d" % [Data.MATS[id]["name"], amount])
