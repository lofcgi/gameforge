class_name Fishing
extends RefCounted
## 닻을 내린 뒤의 일: 깊이 조준, 물고기의 접근과 입질, 줄다리기.

const LINE_SPEED := 220.0
const LINE_START := 56.0
const LINE_ACCEL := 480.0
const SENSE_X := 160.0
const SENSE_Y := 48.0
const LURK_SENSE := 1.8
const FOLLOW_SPEED := 44.0

var hook_y := 0.0
var hook_v := 0.0
var engaged = null          # 미끼에 반응 중이거나 걸린 물고기
var fighting := false
var jig_timer := 0
var jigs := 0
var nudges := 0
var limit_hits := 0

var tension := 0.0
var line := 0.0
var stamina := 1.0
var phase := ""             # tired, warn, pull, spent
var phase_t := 0
var off := 0.0              # 걸린 물고기의 좌우 벗어남(px)
var run_dir := 1.0
var slack_t := 0
var ratio := 1.0
var at_limit := false
var reeling := false

var catches := 0
var snaps := 0
var slips := 0


func hook_x(g: Game) -> float:
	# 낚싯대 끝의 자리는 배 그림 옆의 JSON(rod_tip)에서 온다.
	return g.sailing.x + Layout.boat_reach(g.inv.boat)


func max_depth(g: Game) -> float:
	return minf(g.inv.rod_data()["reach"] * Data.Y_PX, Sea.bed_y(hook_x(g)) - 6.0)


func drop_anchor(g: Game) -> void:
	g.mode = "fish"
	hook_y = 0.0
	hook_v = 0.0
	g.emit("anchor", {"down": true})


func reset() -> void:
	_let_go(60)
	fighting = false
	hook_y = 0.0
	hook_v = 0.0
	reeling = false


func step(g: Game) -> void:
	if fighting:
		_step_fight(g)
		return
	_step_line(g)
	jig_timer = maxi(0, jig_timer - 1)
	if g.pressed("action"):
		jig_timer = 45
		jigs += 1
		g.emit("jig", {})
	if g.pressed("bait"):
		g.swap_bait()
		_let_go(30)
	if g.pressed("left") or g.pressed("right"):
		nudges += 1
		g.emit("anchored", {})
	if g.pressed("cancel"):
		reset()
		g.mode = "sail"
		g.emit("anchor", {"down": false})
		return
	_step_interest(g)


func _step_line(g: Game) -> void:
	var dir := int(g.held("down")) - int(g.held("up"))
	var limit := max_depth(g)
	if dir == 0:
		hook_v = 0.0
	else:
		if signf(hook_v) != dir or absf(hook_v) < LINE_START:
			hook_v = dir * LINE_START
		hook_v = move_toward(hook_v, dir * LINE_SPEED, LINE_ACCEL / 60.0)
	hook_y += hook_v / 60.0
	if hook_y >= limit or hook_y <= 0.0:
		if hook_y > limit and g.pressed("down"):
			limit_hits += 1
			g.emit("limit", {"rod": limit < Sea.bed_y(hook_x(g)) - 8.0})
		elif hook_y <= 0.0 and g.pressed("up"):
			# 이미 다 올라와 있다: 고양이가 귀를 움찔한다.
			g.shrug()
		hook_y = clampf(hook_y, 0.0, limit)
		hook_v = 0.0


func _step_interest(g: Game) -> void:
	var baited: bool = hook_y > 16.0 and g.inv.baits[g.inv.bait] > 0
	if not baited:
		_let_go(60)
		return
	var hook := Vector2(hook_x(g), hook_y)
	if engaged == null:
		_find_candidate(g, hook)
		return
	var f: Dictionary = engaged
	var to := hook - Vector2(f["x"], f["y"])
	f["dir"] = 1.0 if to.x >= 0.0 else -1.0
	var near := 24.0 if f["state"] == "sniff" else 10.0
	if to.length() > near:
		var step := to.normalized() * maxf(f["sp"]["speed"] * 1.6, 60.0) / 60.0
		f["x"] += step.x
		f["y"] += step.y
		return
	f["timer"] -= 1
	if f["state"] == "sniff":
		if f["timer"] <= 0:
			_let_go(420)
		return
	if f["state"] == "approach":
		f["state"] = "nibble"
		f["timer"] = randi_range(35, 85)
	if f["timer"] % 20 == 0:
		g.emit("nibble", {})
	if f["timer"] <= 0:
		_bite(g, f)


func _find_candidate(g: Game, hook: Vector2) -> void:
	var boost := 1.6 if jig_timer > 0 else 1.0
	var best = null
	var best_d := INF
	for f in g.shoal.fish:
		if f["state"] != "swim" or f["cool"] > 0:
			continue
		var reach := SENSE_X * boost * (1.5 if g.sailing.school_near(hook.x, f["id"]) else 1.0)
		if f["sp"]["move"] == "lurk":
			# 숨어 사는 어종은 지나가 주지 않으므로 멀리서도 미끼 냄새를 맡는다.
			reach *= LURK_SENSE
		var dx := absf(f["x"] - hook.x)
		var dy := absf(f["y"] - hook.y)
		# 미끼가 맞는 물고기가 먼저 온다. 안 맞는 물고기가 기웃거리느라 맞는 물고기를 막지 않게 한다.
		var score := dx + dy + (0.0 if f["sp"]["baits"].has(g.inv.bait) else 1000.0)
		if dx < reach and dy < SENSE_Y * boost and score < best_d:
			best = f
			best_d = score
	if best == null:
		return
	engaged = best
	if best["sp"]["baits"].has(g.inv.bait):
		best["state"] = "approach"
	else:
		best["state"] = "sniff"
		best["timer"] = 50
		g.emit("sniff", {})


func _let_go(cooldown: int) -> void:
	if engaged != null:
		engaged["state"] = "swim"
		engaged["cool"] = cooldown
		engaged["home_y"] = clampf(engaged["y"], engaged["sp"]["dmin"] * Data.Y_PX, engaged["sp"]["dmax"] * Data.Y_PX)
		engaged["home_x"] = engaged["x"]
		engaged = null


func _bite(g: Game, f: Dictionary) -> void:
	g.inv.baits[g.inv.bait] -= 1
	f["state"] = "hooked"
	fighting = true
	ratio = f["sp"]["str"] / g.inv.rod_data()["str"]
	tension = 0.35
	line = hook_y
	stamina = 1.0
	off = 0.0
	slack_t = 0
	# 입질 직후 짧은 예고 뒤에 첫 버티기가 온다: 싸움은 늘 "기다렸다 감기"로 시작한다.
	_set_phase(g, "warn", 30)
	g.freeze = 6 if f["sp"]["slots"] >= 3 else 3
	g.emit("bite", {"big": f["sp"]["slots"] >= 3, "id": f["id"]})


func _set_phase(g: Game, name: String, ticks: int) -> void:
	phase = name
	phase_t = ticks
	g.emit(name, {})


func _next_phase(g: Game) -> void:
	var power: float = engaged["sp"]["str"]
	if stamina <= 0.0:
		_set_phase(g, "spent", 100000)
	elif phase == "tired":
		_set_phase(g, "warn", int(Data.TUG["warn"] * 60.0))
	elif phase == "warn":
		run_dir = 1.0 if randf() < 0.5 else -1.0
		if absf(off) > 120.0:
			run_dir = -signf(off)
		_set_phase(g, "pull", int((0.6 + 0.12 * power) * randf_range(0.75, 1.25) * (0.45 + 0.55 * stamina) * 60.0))
	else:
		_set_phase(g, "tired", int(maxf(0.7, 1.7 - 0.05 * power) * randf_range(0.8, 1.2) * (1.8 - 0.8 * stamina) * 60.0))


func _step_fight(g: Game) -> void:
	var f: Dictionary = engaged
	var sp: Dictionary = f["sp"]
	var tug: Dictionary = Data.TUG
	if g.pressed("cancel"):
		_lose(g, "cut", "줄을 끊었다. 미끼를 잃었다.")
		return
	phase_t -= 1
	if phase_t <= 0:
		_next_phase(g)
	if g.pressed("action"):
		g.emit("reel", {})
	reeling = g.held("action")
	var pulling := phase == "pull"
	var rc := minf(ratio, 1.4)
	var power: float = sp["str"]
	var spirit := 0.3 + 0.7 * stamina

	# 좌우: 버티는 큰 물고기는 옆으로 달아나며 배를 끈다. 같은 쪽으로 배를 몰면 따라붙는다.
	var steer := int(g.held("right")) - int(g.held("left"))
	if steer != 0:
		var moved := steer * FOLLOW_SPEED / 60.0
		g.sailing.x = clampf(g.sailing.x + moved, Sailing.left_limit(), Sailing.right_limit())
		off -= moved
	if pulling and sp["run"]:
		off += run_dir * (20.0 + 4.0 * power) * spirit / 60.0
		var drag: float = run_dir * (8.0 + 1.8 * power) * spirit / 60.0
		g.sailing.x = clampf(g.sailing.x + drag, Sailing.left_limit(), Sailing.right_limit())
		off -= drag
	elif not pulling:
		off -= off * 0.6 / 60.0
	off = clampf(off, -220.0, 220.0)

	# 줄 길이
	var limit := minf(g.inv.rod_data()["reach"] * Data.Y_PX, Sea.bed_y(hook_x(g) + off) - 6.0)
	at_limit = false
	if reeling and (not pulling or rc < 0.5):
		var ease_in := 0.5 if pulling else clampf(1.25 - 0.45 * rc, 0.5, 1.0)
		line -= g.inv.rod_data()["reel"] * ease_in / 60.0
	elif pulling and not reeling:
		line += (Data.TUG["run_speed"][0] + Data.TUG["run_speed"][1] * power) * spirit / 60.0
		if line >= limit:
			line = limit
			at_limit = true

	# 장력
	var target := 0.0
	if reeling:
		var pair: Array = tug["reel_pull"] if pulling else tug["reel_tired"]
		target = pair[0] + pair[1] * rc
	elif pulling:
		target = tug["slack_pull"][0] + tug["slack_pull"][1] * rc
	if pulling:
		target += tug["run_extra"] * clampf(absf(off) / 160.0, 0.0, 1.0)
		if at_limit:
			target += tug["limit_extra"]
		if steer != 0 and steer == signf(off) and absf(off) > 12.0:
			target -= tug["follow_relief"]
	target = minf(target, tug["cap"])
	var rate: float = tug["up"] if target > tension else tug["down"]
	tension = maxf(0.0, tension + (target - tension) * rate / 60.0)
	if tension > 0.35 and tension < 0.92:
		stamina = maxf(0.0, stamina - (1.0 if pulling or reeling else 0.3) / (2.0 + 1.2 * power) / 60.0)

	hook_y = line
	f["x"] = hook_x(g) + off
	f["y"] = line
	f["dir"] = run_dir if pulling else (1.0 if off < 0.0 else -1.0)

	if tension >= 1.0:
		_lose(g, "snap", "줄이 끊어졌다! 미끼를 잃었다.")
		return
	if tension < tug["slack_at"]:
		slack_t += 1
		var grace := lerpf(tug["slack_time"][1], tug["slack_time"][0], clampf(rc, 0.0, 1.0)) * 60.0
		if slack_t > grace:
			_lose(g, "slip", "줄이 느슨해 바늘이 빠졌다. 미끼를 잃었다.")
			return
	else:
		slack_t = maxi(0, slack_t - 2)
	if line <= 20.0:
		_catch(g, f)


func _lose(g: Game, how: String, text: String) -> void:
	if how == "snap":
		snaps += 1
	elif how == "slip":
		slips += 1
	engaged["home_y"] = engaged["y"]
	engaged["dir"] = run_dir
	var gone = engaged
	_end_fight(g)
	gone["state"] = "swim"
	gone["cool"] = 600
	gone["burst"] = 60
	g.emit(how, {"id": gone["id"]})
	g.toast(text)


func _end_fight(g: Game) -> void:
	engaged = null
	fighting = false
	reeling = false
	hook_y = 0.0
	hook_v = 0.0
	tension = 0.0
	phase = ""
	if g.inv.baits[g.inv.bait] <= 0:
		g.inv.cycle_bait()


func _catch(g: Game, f: Dictionary) -> void:
	var sp: Dictionary = f["sp"]
	var id: String = sp["id"]
	g.shoal.fish.erase(f)
	_end_fight(g)
	catches += 1
	var is_new := not g.inv.caught.has(id)
	g.inv.caught[id] = g.inv.caught.get(id, 0) + 1
	var big: bool = sp["slots"] >= 3
	g.freeze = 6 if big else 2
	g.emit("catch", {"id": id, "new": is_new, "big": big})
	if id == "legend":
		g.toast("항구로 돌아가 용궁에 바치자.")
	if g.inv.fits(id):
		g.inv.hold.append(id)
	else:
		g.menu.open(g, "hold", id)
