class_name Fx
extends RefCounted
## 연출 상태: 입자, 화면 흔들림, 떠오르는 글자, 알림, 깜박임, 날아가는 동전. 게임 규칙에는 영향을 주지 않는다.
## 물리 틱에서 진행하고, 코어의 난수 순서를 건드리지 않게 따로 난수기를 쓴다.

const FLY_TICKS := 30
const COIN_TICKS := 34

var particles: Array = []     # 세계 좌표의 작은 사각형 {pos, vel, life, color, size, grav}
var sprites: Array = []       # 세계 좌표의 한 번 재생되는 애니메이션 {base, pos, start}
var floaters: Array = []      # 세계 좌표에 떠오르는 글자 {pos, text, t, color}
var toasts: Array = []        # 화면 알림 {text, t}
var coins: Array = []         # 화면 좌표로 날아가는 동전 {from, t, delay}
var shake := 0.0
var offset := Vector2.ZERO
var twitch := 0               # 낚싯줄 떨림
var ears := 0                 # 고양이 귀 서기(입질)
var hop := 0
var flash := {}               # 이름 -> 남은 틱
var catch_card := {}          # {id, new, t}
var fly := {}                 # 낚인 물고기가 물 밖으로 튀어 배로 날아드는 연출 {id, from, t}
var facing := 1.0             # 배가 보는 쪽
var mood := ""                # 고양이의 기분 동작: cheer, sad
var mood_t := 0
var tick := 0

var _rng := RandomNumberGenerator.new()


func _init() -> void:
	_rng.seed = 7


func clear_world() -> void:
	particles.clear()
	sprites.clear()
	floaters.clear()
	fly = {}
	shake = 0.0


func burst(pos: Vector2, count: int, color: Color, speed := 80.0, up := 60.0) -> void:
	for i in count:
		var vel := Vector2(_rng.randf_range(-speed, speed), _rng.randf_range(-speed - up, speed * 0.3))
		particles.append({"pos": pos, "vel": vel, "life": _rng.randi_range(18, 40), "color": color,
			"size": _rng.randi_range(2, 3), "grav": 280.0})


func play(base: String, pos: Vector2) -> void:
	sprites.append({"base": base, "pos": pos, "start": tick})


func floater(pos: Vector2, text: String, color := Pal.WHITE) -> void:
	floaters.append({"pos": pos, "text": text, "t": 70, "color": color})


func coin_burst(from: Vector2, count: int) -> void:
	for i in mini(count, 12):
		coins.append({"from": from + Vector2(_rng.randf_range(-14, 14), _rng.randf_range(-10, 10)), "t": 0, "delay": i * 3})


func on(name: String) -> bool:
	return flash.get(name, 0) > 0


func set_mood(name: String, ticks: int) -> void:
	mood = name
	mood_t = ticks


func consume(g: Game) -> void:
	var boat := Vector2(g.sailing.x, g.sailing.y)
	var hook := Vector2(g.fishing.hook_x(g), g.fishing.hook_y)
	for e in g.events:
		match e["type"]:
			"toast":
				toasts.append({"text": e["text"], "t": 190})
				if toasts.size() > 2:
					toasts.pop_front()
			"enter":
				clear_world()
			"paddle":
				burst(boat + Vector2(-e["dir"] * 40.0, 2.0), 4, Pal.WHITE, 36.0, 28.0)
			"ride":
				play("sea/splash", boat + Vector2(facing * 40.0, 0))
			"hit":
				shake = 12.0
				flash["hit"] = 40
				play("sea/splash", boat + Vector2(30, 0))
				play("sea/splash", boat + Vector2(-30, 0))
				burst(boat, 18, Pal.WHITE, 120.0, 80.0)
				floater(boat + Vector2(-16, -70), "-%d" % e["damage"], Pal.ORANGE)
				set_mood("sad", 50)
			"pickup":
				burst(Vector2(e["x"], 0), 8, Pal.CREAM, 60.0, 60.0)
				play("sea/sparkle", Vector2(e["x"], -16))
				flash["coins"] = 30
			"anchor":
				play("sea/splash", boat + Vector2(-facing * 30.0, 0))
			"dock", "board":
				burst(boat + Vector2(0, 4), 8, Pal.WHITE, 48.0, 36.0)
			"jig":
				twitch = 12
				burst(hook, 3, Pal.WHITE, 24.0, 8.0)
			"bait":
				flash["bait"] = 24
			"sniff":
				twitch = 6
			"nibble":
				twitch = 9
				ears = 40
			"bite":
				shake = 10.0 if e["big"] else 5.0
				ears = 90
				burst(hook, 10, Pal.WHITE, 80.0, 20.0)
				floater(boat + Vector2(20, -84), "!", Pal.CREAM)
			"warn":
				flash["warn"] = 22
			"pull":
				shake = maxf(shake, 3.0)
				twitch = 16
			"reel":
				twitch = maxi(twitch, 4)
			"snap", "cut":
				shake = 10.0
				flash["hit"] = 20
				burst(boat + Vector2(60, -40), 12, Pal.WHITE, 100.0, 40.0)
				set_mood("sad", 80)
			"slip":
				burst(hook, 8, Pal.WHITE, 40.0, 0.0)
				set_mood("sad", 80)
			"catch":
				shake = 14.0 if e["big"] else 6.0
				play("sea/splash", Vector2(hook.x, 0))
				burst(Vector2(hook.x, 0), 26 if e["big"] else 12, Pal.WHITE, 120.0, 100.0)
				catch_card = {"id": e["id"], "new": e["new"], "t": 0}
				fly = {"id": e["id"], "from": Vector2(hook.x, 0.0), "t": 0}
				ears = 60
				set_mood("cheer", 90)
			"limit":
				flash["limit"] = 24
			"anchored":
				flash["anchored"] = 30
			"gather":
				burst(Vector2(e["x"], e["y"] - 12), 8, Data.MATS[e["id"]]["color"], 52.0, 60.0)
				floater(Vector2(e["x"] - 16, e["y"] - 50), "%s +%d" % [Data.MATS[e["id"]]["name"], e["amount"]], Pal.WHITE)
				flash["mats"] = 30
			"hop":
				hop = 16
			"sell":
				flash["coins"] = 50
			"buy", "craft", "repair":
				flash["coins"] = 20
				flash["buy"] = 30
			"deny":
				flash["deny"] = 14
			"shrug":
				ears = 14
				flash["shrug"] = 10
			"zone":
				flash["zone"] = 120
			"cursor", "open", "close", "page":
				flash["cursor"] = 6
			"wreck":
				shake = 18.0
			"saved":
				flash["saved"] = 60


func step(g: Game) -> void:
	tick += 1
	for p in particles:
		p["vel"].y += p["grav"] / 60.0
		p["pos"] += p["vel"] / 60.0
		p["life"] -= 1
	particles = particles.filter(func(p): return p["life"] > 0)
	sprites = sprites.filter(func(s): return (tick - s["start"]) * Assets.anim(s["base"])["fps"] / 60.0 < Assets.frame_count(s["base"]))
	for f in floaters:
		f["pos"].y -= 0.6
		f["t"] -= 1
	floaters = floaters.filter(func(f): return f["t"] > 0)
	for t in toasts:
		t["t"] -= 1
	toasts = toasts.filter(func(t): return t["t"] > 0)
	for coin in coins:
		if coin["delay"] > 0:
			coin["delay"] -= 1
		else:
			coin["t"] += 1
	coins = coins.filter(func(coin): return coin["t"] < COIN_TICKS)
	for name in flash:
		flash[name] = maxi(0, flash[name] - 1)
	twitch = maxi(0, twitch - 1)
	ears = maxi(0, ears - 1)
	hop = maxi(0, hop - 1)
	mood_t = maxi(0, mood_t - 1)
	if mood_t == 0:
		mood = ""
	if not catch_card.is_empty():
		catch_card["t"] += 1
		if catch_card["t"] > 170:
			catch_card = {}
	if not fly.is_empty():
		fly["t"] += 1
		if fly["t"] > FLY_TICKS:
			fly = {}
	shake = maxf(0.0, shake * 0.86 - 0.1)
	offset = Vector2(_rng.randf_range(-shake, shake), _rng.randf_range(-shake, shake)).round()
	if g.menu.busy() or g.freeze > 0 or g.scene != "sea":
		return
	var sail := g.sailing
	if g.mode == "sail":
		if absf(sail.vx) > 8.0:
			facing = signf(sail.vx)
		if absf(sail.vx) > 44.0 and g.tick % 5 == 0:
			burst(Vector2(sail.x - facing * 50.0, sail.y + 2.0), 1, Pal.WHITE, 16.0, 20.0)
	elif g.mode == "fish":
		facing = 1.0
		if g.fishing.fighting:
			if g.fishing.reeling and g.tick % 6 == 0:
				burst(Vector2(g.fishing.hook_x(g), 0.0), 1, Pal.WHITE, 16.0, 16.0)
			if g.fishing.phase == "pull" and g.tick % 8 == 0:
				play("sea/bubble", Vector2(g.fishing.engaged["x"], g.fishing.engaged["y"] - 8.0))
			if g.fishing.tension > 0.85:
				shake = maxf(shake, 2.0)
