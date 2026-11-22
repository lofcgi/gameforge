class_name Fx
extends RefCounted
## 연출 상태: 작은 사각형 입자, 화면 흔들림, 떠오르는 글자, 알림, 깜박임. 게임 규칙에는 영향을 주지 않는다.
## 코어의 난수 순서를 건드리지 않게 따로 난수기를 쓴다.

const WHITE := Color("#E9F3E2")
const FLY_TICKS := 26

var particles: Array = []
var floaters: Array = []      # 세계 좌표에 떠오르는 글자
var toasts: Array = []
var shake := 0.0
var offset := Vector2.ZERO
var twitch := 0               # 낚싯줄 떨림
var ears := 0                 # 고양이 귀 서기
var hop := 0
var flash := {}               # 이름 -> 남은 틱 (hit, limit, anchored, coins, deny, bait, warn)
var catch_card := {}          # {id, new, t}
var fly := {}                 # 낚인 물고기가 물 밖으로 튀어 배로 날아드는 짧은 연출 {id, from, t}
var facing := 1.0

var _rng := RandomNumberGenerator.new()


func _init() -> void:
	_rng.seed = 7


func burst(pos: Vector2, count: int, color: Color, speed := 40.0, up := 30.0) -> void:
	for i in count:
		var vel := Vector2(_rng.randf_range(-speed, speed), _rng.randf_range(-speed - up, speed * 0.3))
		particles.append({"pos": pos, "vel": vel, "life": _rng.randi_range(18, 40), "color": color,
			"size": _rng.randi_range(1, 2), "grav": 140.0})


func bubble(pos: Vector2) -> void:
	particles.append({"pos": pos, "vel": Vector2(_rng.randf_range(-4, 4), -18.0), "life": 50,
		"color": Color(WHITE, 0.6), "size": 1, "grav": 0.0})


func floater(pos: Vector2, text: String, color := WHITE) -> void:
	floaters.append({"pos": pos, "text": text, "t": 60, "color": color})


func on(name: String) -> bool:
	return flash.get(name, 0) > 0


func consume(g: Game) -> void:
	var boat := Vector2(g.sailing.x, g.sailing.y)
	var hook := Vector2(g.fishing.hook_x(g), g.fishing.hook_y)
	var walker := Vector2(g.land.x, -8.0)
	for e in g.events:
		match e["type"]:
			"toast":
				toasts.append({"text": e["text"], "t": 170})
				if toasts.size() > 2:
					toasts.pop_front()
			"paddle":
				burst(boat + Vector2(-e["dir"] * 12.0, 1.0), 4, WHITE, 18.0, 14.0)
			"ride":
				burst(boat + Vector2(10, 0), 6, WHITE, 26.0, 20.0)
			"hit":
				shake = 6.0
				flash["hit"] = 40
				burst(boat, 18, WHITE, 60.0, 40.0)
				floater(boat + Vector2(-8, -22), "-%d" % e["damage"], Color("#D46A7E"))
			"pickup":
				burst(Vector2(e["x"], 0), 8, Color("#E9D36B"), 30.0, 30.0)
				flash["coins"] = 30
			"anchor", "dock", "board":
				burst(boat + Vector2(0, 2), 8, WHITE, 24.0, 18.0)
			"jig":
				twitch = 12
				burst(hook, 3, WHITE, 12.0, 4.0)
			"bait":
				flash["bait"] = 20
			"sniff":
				twitch = 6
			"nibble":
				twitch = 9
				ears = 40
			"bite":
				shake = 5.0 if e["big"] else 2.5
				ears = 90
				burst(hook, 10, WHITE, 40.0, 10.0)
				floater(boat + Vector2(4, -30), "!", Color("#E9D36B"))
			"warn":
				flash["warn"] = 22
			"pull":
				shake = maxf(shake, 1.6)
				twitch = 16
			"reel":
				twitch = maxi(twitch, 4)
				burst(Vector2(hook.x, 0), 2, WHITE, 10.0, 8.0)
			"snap", "cut":
				shake = 5.0
				flash["hit"] = 20
				burst(boat + Vector2(16, -14), 12, WHITE, 50.0, 20.0)
			"slip":
				burst(hook, 8, WHITE, 20.0, 0.0)
			"catch":
				shake = 7.0 if e["big"] else 3.0
				burst(Vector2(hook.x, 0), 26 if e["big"] else 12, WHITE, 60.0, 50.0)
				catch_card = {"id": e["id"], "new": e["new"], "t": 150}
				fly = {"id": e["id"], "from": Vector2(hook.x, 0.0), "t": 0}
				ears = 60
			"limit":
				flash["limit"] = 24
			"anchored":
				flash["anchored"] = 30
			"gather":
				burst(walker, 8, Data.MATS[e["id"]]["color"], 26.0, 30.0)
				hop = 14
			"hop", "empty":
				hop = 14
			"sell":
				flash["coins"] = 40
			"buy", "craft":
				flash["coins"] = 20
				flash["buy"] = 20
			"deny":
				flash["deny"] = 12
			"shrug":
				ears = 14
			"zone":
				flash["zone"] = 90
			"cursor", "card", "open", "close":
				flash["cursor"] = 6
			"wreck":
				shake = 9.0


func step(g: Game) -> void:
	for p in particles:
		p["vel"].y += p["grav"] / 60.0
		p["pos"] += p["vel"] / 60.0
		p["life"] -= 1
	particles = particles.filter(func(p): return p["life"] > 0)
	for f in floaters:
		f["pos"].y -= 0.35
		f["t"] -= 1
	floaters = floaters.filter(func(f): return f["t"] > 0)
	for t in toasts:
		t["t"] -= 1
	toasts = toasts.filter(func(t): return t["t"] > 0)
	for name in flash:
		flash[name] = maxi(0, flash[name] - 1)
	twitch = maxi(0, twitch - 1)
	ears = maxi(0, ears - 1)
	hop = maxi(0, hop - 1)
	if not catch_card.is_empty():
		catch_card["t"] -= 1
		if catch_card["t"] <= 0:
			catch_card = {}
	if not fly.is_empty():
		fly["t"] += 1
		if fly["t"] > FLY_TICKS:
			fly = {}
	shake = maxf(0.0, shake * 0.86 - 0.05)
	offset = Vector2(_rng.randf_range(-shake, shake), _rng.randf_range(-shake, shake)).round()
	if g.menu.busy() or g.freeze > 0:
		return
	var sail := g.sailing
	if g.mode == "sail":
		if absf(sail.vx) > 4.0:
			facing = signf(sail.vx)
		if absf(sail.vx) > 22.0 and g.tick % 5 == 0:
			burst(Vector2(sail.x - facing * 12.0, sail.y + 1.0), 1, WHITE, 8.0, 10.0)
	elif g.mode == "fish":
		facing = 1.0
		if g.fishing.fighting:
			if g.fishing.reeling and g.tick % 6 == 0:
				burst(Vector2(g.fishing.hook_x(g), 0.0), 1, WHITE, 8.0, 8.0)
			if g.fishing.phase == "pull" and g.tick % 4 == 0:
				bubble(Vector2(g.fishing.engaged["x"], g.fishing.engaged["y"]))
			if g.fishing.tension > 0.85:
				shake = maxf(shake, 1.0)
