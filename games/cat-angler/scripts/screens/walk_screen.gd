extends Screen
## 걸어 다니는 화면: 항구 마을, 채집지, 섬. 배경 그림 위에서 고양이가 걷고, 문·재료·배 앞에서 Space 를 누른다.

const EDGE_TEXT := {"town": ["← 채집지", ""], "forage": ["", "마을 →"], "island": ["", ""]}

var cam_x := 320.0

var _area := ""
var _width := 640.0


func setup(g: Game, effects: Fx) -> void:
	super.setup(g, effects)
	_area = g.scene
	_width = Layout.width("places/" + _area)
	cam_x = _target()


func _target() -> float:
	return clampf(game.walk.x + game.walk.facing * 40.0, 320.0, maxf(320.0, _width - 320.0))


func advance() -> void:
	cam_x += (_target() - cam_x) * 0.08
	queue_redraw()


func _origin() -> Vector2:
	return Vector2(-roundf(cam_x - 320.0), 0) + fx.offset


func focus() -> Vector2:
	return _origin() + Vector2(game.walk.x, game.walk.ground() - 30.0)


func _draw() -> void:
	var g := game
	var walk := g.walk
	var origin := _origin()
	var data := walk.layout()
	var ground := walk.ground()
	draw_texture(Assets.tex("places/%s.png" % _area), origin)
	# 내 배가 부두(섬에서는 선착장)에 매여 있다.
	if _area != "forage":
		var boat := Layout.boat(g.inv.boat)
		var water: float = data.get("water_y", ground + 24.0)
		var bx: float = data["pier"] + 34.0 + boat["size"].x * 0.5 if _area == "town" else data["dock"] - 30.0 - boat["size"].x * 0.5
		var bob := roundf(sin(g.tick * 0.05) * 2.0)
		draw_texture(Assets.tex("boats/boat%d.png" % (g.inv.boat + 1)), (origin + Vector2(bx, water + bob) - boat["pivot"]).round())
	# 자란 재료
	for spot in walk.spots():
		if spot["kind"] == "gather" and walk.stock[spot["mat"]][spot["index"]]:
			var sway := roundf(sin(g.tick * 0.05 + spot["x"]) * 1.0)
			Ui.sprite(self, Assets.tex("items/%s_plant.png" % spot["mat"]), origin + Vector2(spot["x"] + sway, spot["y"]))
			# 주울 수 있는 자리는 가끔 반짝인다.
			var beat: int = (g.tick + spot["index"] * 23 + int(spot["x"])) % 96
			if beat < 24:
				Ui.sprite(self, Assets.frame("sea/sparkle", beat, 0, true), origin + Vector2(spot["x"] + 6, spot["y"] - 18), Vector2(0.5, 0.5))
	# 고양이
	var action := "idle"
	if walk.pick_t > 0:
		action = "pick"
	elif fx.mood != "":
		action = fx.mood
	elif absf(walk.vx) > 20.0:
		action = "walk"
	var lift := sin(fx.hop / 16.0 * PI) * 12.0 if fx.hop > 0 else 0.0
	draw_cat(origin + Vector2(walk.x, ground - lift), action, walk.facing < 0.0, g.tick - (Walk.PICK_TICKS - walk.pick_t) if action == "pick" else 0,
		action == "pick")
	if _area == "town":
		draw_texture(Assets.tex("places/town_fg.png"), origin)
	draw_effects(origin)
	_prompt(origin)
	_pointer(origin)


## 닿는 거리 안의 것 위에 이름과 키를 띄운다.
func _prompt(origin: Vector2) -> void:
	var near = game.walk.near
	if near == null or game.menu.busy() or game.transitioning():
		return
	var text := ""
	var height := 60.0
	match near["kind"]:
		"door":
			text = Data.SHOPS[near["id"]]["title"]
			height = 100.0
		"gather":
			text = Data.MATS[near["mat"]]["name"]
			height = 86.0
		"board":
			text = "배 타기"
			height = 86.0
	var w := Ui.width(text) + Ui.width("Space") + 30.0
	var pos := origin + Vector2(near["x"] - w * 0.5, near["y"] - height + roundf(sin(game.tick * 0.1) * 1.5))
	Ui.box(self, "bubble", Rect2(pos, Vector2(w, 22)))
	var used := Ui.key(self, pos + Vector2(6, 2), "action", "", Pal.BARK)
	Ui.text(self, pos + Vector2(used - 6, 4), text, Pal.BARK)


func _pointer(origin: Vector2) -> void:
	var target := game.guide.target(game)
	if target.is_empty() or game.menu.busy():
		return
	var blink := game.tick % 40 < 28
	var dir: int = target.get("dir", 0)
	if dir == 0:
		var sx: float = origin.x + target["x"]
		if sx < 16.0:
			dir = -1
		elif sx > 624.0:
			dir = 1
		elif game.walk.near == null or absf(game.walk.near["x"] - target["x"]) > 4.0:
			draw_pointer(Vector2(sx, game.walk.ground() - 100.0))
			return
		else:
			return
	if not blink:
		return
	var words: Array = EDGE_TEXT[_area]
	var text: String = words[0 if dir < 0 else 1]
	if text == "":
		text = "←" if dir < 0 else "→"
	var push := roundf(absf(sin(game.tick * 0.1)) * 4.0)
	if dir < 0:
		Ui.label(self, Vector2(10 - push, 200), text, Pal.CREAM)
	else:
		Ui.label(self, Vector2(630 - Ui.width(text, "bold") + push, 200), text, Pal.CREAM)
