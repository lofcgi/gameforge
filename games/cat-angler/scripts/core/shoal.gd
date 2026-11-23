class_name Shoal
extends RefCounted
## 배 주변의 물고기들: 생성과 헤엄. 미끼에 대한 반응과 줄다리기는 Fishing 이 맡는다.

const WINDOW := 500.0
const FAR := 660.0

var fish: Array = []


func step(g: Game) -> void:
	var boat_x := g.sailing.x
	if g.tick % 20 == 0:
		_populate(g, boat_x)
	for f in fish:
		if f["state"] == "swim":
			_swim(f)
	fish = fish.filter(func(f): return f["state"] != "swim" or absf(f["x"] - boat_x) < FAR)


func _populate(g: Game, boat_x: float) -> void:
	for sp in Data.FISH:
		var id: String = sp["id"]
		var wanted: int = sp["count"]
		# 전설의 심해어는 한 마리뿐이다: 낚아서 싣고 있거나 이미 바쳤으면 다시 나오지 않는다.
		if id == "legend" and (g.delivered or g.inv.hold.has("legend") or g.menu.pending == "legend"):
			continue
		if g.sailing.school_near(boat_x, id):
			wanted *= 2
		if fish.filter(func(f): return f["id"] == id).size() >= wanted:
			continue
		var px := boat_x + randf_range(-WINDOW, WINDOW)
		if sp["place"] != "":
			var place: Dictionary = Data.PLACES[sp["place"]]
			px = Sea.place_x(sp["place"]) + randf_range(-0.5, 0.5) * place["w"] * Data.X_PX
			if absf(px - boat_x) > WINDOW:
				continue
		elif g.mode == "fish" and absf(px - boat_x) < 350.0:
			# 낚시 중에는 화면 밖에서 헤엄쳐 들어오게 한다.
			px = boat_x + signf(px - boat_x + 0.01) * randf_range(350.0, WINDOW)
		if Sea.zone_at(px)["id"] != sp["zone"]:
			continue
		var bed := Sea.bed_y(px)
		if bed < sp["dmin"] * Data.Y_PX + 16.0:
			continue
		var py := minf(randf_range(sp["dmin"], sp["dmax"]) * Data.Y_PX, bed - 12.0)
		fish.append({
			"id": id, "sp": sp, "x": px, "y": py, "home_x": px, "home_y": py,
			"dir": 1.0 if randf() < 0.5 else -1.0, "phase": randf() * TAU, "state": "swim",
			"timer": 0, "cool": 0, "burst": 0, "squash": 0, "born": g.tick,
		})


func _swim(f: Dictionary) -> void:
	var sp: Dictionary = f["sp"]
	var speed: float = sp["speed"]
	var roam := 300.0
	match sp["move"]:
		"dart":
			f["burst"] -= 1
			if f["burst"] < -50:
				f["burst"] = 24
			speed *= 2.2 if f["burst"] > 0 else 0.5
		"lurk":
			roam = 52.0
		"patrol":
			roam = 420.0
	f["x"] += f["dir"] * speed / 60.0
	f["phase"] += 0.05
	f["y"] = minf(f["home_y"] + sin(f["phase"]) * 5.0, Sea.bed_y(f["x"]) - 8.0)
	var leaving: bool = absf(f["x"] - f["home_x"]) > roam and signf(f["x"] - f["home_x"]) == f["dir"]
	# 바닥이 제 깊이보다 얕아지는 곳(암초, 비탈) 앞에서는 돌아선다.
	if leaving or Sea.bed_y(f["x"] + f["dir"] * 24.0) < f["home_y"] + 12.0:
		f["dir"] = -f["dir"]
		f["home_x"] = f["x"] if not leaving else f["home_x"]
		f["squash"] = 8
	f["cool"] = maxi(0, f["cool"] - 1)
	f["squash"] = maxi(0, f["squash"] - 1)
