class_name WorldView
extends Node2D
## 세계를 도형으로 그린다. 코어(Game)의 상태를 읽기만 하고, 카메라와 연출(Fx)만 스스로 가진다.
## 카메라와 연출도 물리 틱에서만 진행해 기록 재생의 화면이 원본과 같게 한다.

const SCREEN := Vector2(320, 180)
const SURFACE_LINE := 99.0      # 운항 중 수면선의 화면 y (위에서 55%)
const DARK := Color("#17121B")
const WHITE := Color("#E9F3E2")

var game: Game
var fx := Fx.new()
var cam := Vector2(160, 90 - SURFACE_LINE)

var _font: Font = ThemeDB.fallback_font
var _origin := Vector2.ZERO
var _snapped := false


var _layers := {}


func _ready() -> void:
	for kind in ["clouds", "mountains", "islets"]:
		_layers[kind] = StaticLayer.make(func(c: CanvasItem): Scenery.backdrop(c, kind))
	_layers["port"] = StaticLayer.make(func(c: CanvasItem): Scenery.port(c, game, _font))
	_layers["island"] = StaticLayer.make(func(c: CanvasItem): Scenery.island(c, game, _font))
	for name in _layers:
		add_child(_layers[name])


func advance() -> void:
	fx.consume(game)
	fx.step(game)
	_move_camera()
	_origin = (SCREEN * 0.5 - cam + fx.offset).round()
	_place_layers()
	queue_redraw()


## 한 번 그려 둔 겹들의 위치와 색만 옮긴다.
func _place_layers() -> void:
	var g := game
	var sky := Sea.blend_color(cam.x, "sky")
	RenderingServer.set_default_clear_color(sky)
	var horizon := _origin.y
	var tints := {"clouds": sky.lightened(0.35), "mountains": sky.lerp(Color("#426A96"), 0.25), "islets": sky.lerp(Color("#28706F"), 0.45)}
	var speeds := {"clouds": 0.08, "mountains": 0.18, "islets": 0.45}
	for kind in tints:
		var layer: StaticLayer = _layers[kind]
		var drift := g.tick * 0.01 if kind == "clouds" else 0.0
		layer.visible = horizon > -10.0
		layer.position = Vector2(-fposmod(cam.x * speeds[kind] - drift, Scenery.PERIOD[kind]), horizon).round()
		layer.modulate = tints[kind]
		layer.refresh(0)
	var near_id: String = g.land.near["id"] if g.mode == "land" and g.land.near != null else ""
	_layers["port"].visible = cam.x < 800.0
	_layers["port"].position = _origin
	_layers["port"].refresh([g.land.stock.duplicate(), near_id])
	_layers["island"].visible = absf(cam.x - Sea.place_x("island")) < 260.0
	_layers["island"].position = _origin
	_layers["island"].refresh(g.land.stock["flower"])


func _move_camera() -> void:
	var g := game
	var target := Vector2(g.sailing.x + g.sailing.vx * 0.3, 90.0 - SURFACE_LINE)
	if g.mode == "land":
		target.x = g.land.x
		if g.land.area == "port":
			target.x = clampf(target.x, 100.0, 560.0)
	elif g.mode == "fish":
		var fishing := g.fishing
		target.x = fishing.hook_x(g) + (fishing.off * 0.5 if fishing.fighting else 0.0)
		var deepest := maxf(target.y, Sea.bed_y(target.x) + 42.0 - SCREEN.y * 0.5)
		target.y = clampf(fishing.hook_y - 8.0, target.y, deepest)
	if not _snapped:
		cam = target
		_snapped = true
	cam.x += (target.x - cam.x) * 0.1
	cam.y += (target.y - cam.y) * 0.12


func _draw() -> void:
	if game == null:
		return
	var g := game
	var tick := g.tick
	var left := cam.x - 170.0
	var right := cam.x + 170.0
	var top := cam.y - 92.0
	var bottom := cam.y + 92.0
	if not g.menu.cards.is_empty():
		return
	if _origin.y > -10.0:
		draw_circle(Vector2(250, _origin.y - 62), 9.0, Sea.blend_color(cam.x, "sky").lightened(0.5))
	draw_set_transform(_origin)
	var water := Sea.blend_color(cam.x, "water")
	# 가까운 파도 한 겹: 배 뒤에서 다른 속도로 흐른다.
	_wave_band(left, right, tick, -3.0, 0.8, water.lightened(0.28), 30.0)
	if g.mode == "land":
		var ground := Scenery.ground_y(g.land.area, g.land.x)
		var lift := sin(fx.hop / 14.0 * PI) * 5.0
		draw_set_transform(_origin + Vector2(g.land.x, ground - lift).round(), 0.0, Vector2(g.land.facing, 1))
		Actors.cat(self, Vector2.ZERO, tick + int(absf(g.land.vx) * tick * 0.05), fx.ears > 0)
		draw_set_transform(_origin)
	Scenery.surface_marks(self, _origin, g, left, right)
	Actors.boat(self, _origin, g, fx)
	_water_body(left, right, top, bottom, tick, water)
	Scenery.vortex_mark(self, _origin, g, left, right)
	_seabed(left, right, bottom, tick)
	for f in g.shoal.fish:
		if f["x"] > left - 40.0 and f["x"] < right + 40.0 and f["y"] < bottom + 20.0:
			Actors.fish(self, _origin, f, g, _font)
	for s in g.sailing.schools:
		if s["x"] > left - 30.0 and s["x"] < right + 30.0:
			Actors.school(self, s, g.sailing.surface_y(s["x"], tick), tick)
	for item in g.sailing.flotsam:
		if item["x"] > left and item["x"] < right:
			Actors.flotsam(self, _origin, item, g.sailing.surface_y(item["x"], tick), tick)
	for crest in g.sailing.crests:
		var cy := g.sailing.surface_y(crest["x"], tick)
		var h := g.sailing.crest_height(crest)
		if h > 2.0:
			draw_rect(Rect2(crest["x"] - 4, cy - 1, 8, 2), WHITE)
			draw_rect(Rect2(crest["x"] - 9, cy + 1, 4, 1), WHITE)
			draw_rect(Rect2(crest["x"] + 6, cy + 2, 3, 1), WHITE)
	if g.mode == "fish":
		_line(g)
	if not fx.fly.is_empty():
		var t: float = fx.fly["t"] / float(Fx.FLY_TICKS)
		var from: Vector2 = fx.fly["from"]
		var to := Vector2(g.sailing.x, g.sailing.y - 8.0)
		var at := from.lerp(to, t) - Vector2(0, sin(t * PI) * 26.0)
		Actors.fish_shape(self, _origin, at, Data.fish(fx.fly["id"]), 1.0, sin(g.tick * 0.9) * 2.0, 1.0, Color.TRANSPARENT, -1.2 + t * 2.4)
	for p in fx.particles:
		draw_rect(Rect2(p["pos"].round(), Vector2(p["size"], p["size"])), p["color"])
	for f in fx.floaters:
		draw_string(_font, f["pos"].round(), f["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(f["color"], minf(1.0, f["t"] / 20.0)))
	draw_set_transform(Vector2.ZERO)


## 높이를 4px 마다 재서 그 아래를 다각형 하나로 채우고 윗선을 긋는다.
## 띠마다 사각형을 그리는 것보다 그리기 명령이 훨씬 적다(수백 개 → 두 개).
func _fill_below(left: float, right: float, heights: Callable, floor_y: float, color: Color, edge := Color.TRANSPARENT) -> void:
	var line := PackedVector2Array()
	var px := floorf(left / 4.0) * 4.0
	while px <= right + 4.0:
		line.append(Vector2(px, roundf(heights.call(px))))
		px += 4.0
	var body := line.duplicate()
	body.append(Vector2(px - 4.0, floor_y))
	body.append(Vector2(line[0].x, floor_y))
	draw_colored_polygon(body, color)
	if edge.a > 0.0:
		draw_polyline(line, edge, 1.0)


func _wave_band(left: float, right: float, tick: int, lift: float, parallax: float, color: Color, shift: float) -> void:
	var back := func(px: float) -> float:
		return Sea.ripple_y((px - cam.x) / parallax + cam.x * parallax + shift, tick + 90) * 1.2 + lift
	_fill_below(left, right, back, 16.0, color)


func _water_color(base: Color, depth: float) -> Color:
	var t := clampf(depth / (150.0 * Data.Y_PX), 0.0, 1.0)
	return base.lerp(Data.DEEP_WATER, pow(t, 0.55) * 0.9)


func _water_body(left: float, right: float, top: float, bottom: float, tick: int, water: Color) -> void:
	if top < 20.0:
		var front := func(px: float) -> float: return game.sailing.surface_y(px, tick)
		# 수면 문양: 수면선을 따라 밝은 선과 천천히 흐르는 짧은 무늬.
		_fill_below(left, right, front, 16.0, Color(_water_color(water, 0.0), 0.86), water.lightened(0.55))
		var mark := floorf(left / 22.0) * 22.0
		while mark < right:
			var mx := mark + fposmod(tick * 0.12, 22.0)
			draw_rect(Rect2(mx, game.sailing.surface_y(mx, tick) + 4.0, 7, 1), Color(water.lightened(0.5), 0.6))
			mark += 22.0
	var row := maxf(16.0, floorf(top / 8.0) * 8.0)
	while row < bottom:
		draw_rect(Rect2(left, row, right - left, 8.0), _water_color(water, row))
		row += 8.0
	if top < 110.0:
		for i in 3:
			var rx := floorf(cam.x / 130.0) * 130.0 + (i - 1) * 130.0 + 40.0 + sin(tick * 0.01 + i) * 10.0
			draw_colored_polygon(PackedVector2Array([Vector2(rx, 16), Vector2(rx + 12, 16), Vector2(rx - 18, 110), Vector2(rx - 36, 110)]),
				Color(WHITE, 0.06))
	# 떠다니는 알갱이: 카메라가 움직일 때 깊이와 속도를 느끼게 한다.
	var cell := 40.0
	var gx := floorf(left / cell) * cell
	while gx < right:
		var gy := maxf(cell, floorf(top / cell) * cell)
		while gy < bottom:
			var seed_value := int(gx * 0.37 + gy * 1.31)
			var px := gx + posmod(seed_value * 17, 40) + sin(tick * 0.02 + seed_value) * 3.0
			var py := gy + posmod(seed_value * 29, 40) - fposmod(tick * 0.05, cell)
			if py > 18.0 and py < Sea.bed_y(px):
				draw_rect(Rect2(px, py, 1, 1), Color(WHITE, 0.28))
			gy += cell
		gx += cell


func _seabed(left: float, right: float, bottom: float, tick: int) -> void:
	if Sea.bed_y(left) > bottom and Sea.bed_y(right) > bottom and Sea.bed_y(cam.x) > bottom:
		return
	var color := Sea.blend_color(cam.x, "bed_color")
	if Sea.near_place(cam.x, "reef", 30.0):
		color = color.lerp(Scenery.ROCK, 0.6)
	color = color.lerp(_water_color(Sea.blend_color(cam.x, "water"), Sea.bed_y(cam.x)), 0.45)
	# 화면 아래로 벗어난 바닥은 화면 밖의 평평한 선으로 눌러 다각형이 뒤집히지 않게 한다.
	var floor_y := maxf(bottom, 80.0) + 40.0
	var bed := func(px: float) -> float: return clampf(Sea.bed_y(px), 2.0, floor_y - 4.0)
	_fill_below(left, right, bed, floor_y, color, color.lightened(0.25))
	Scenery.bed_decor(self, left, right, tick)


func _line(g: Game) -> void:
	var fishing := g.fishing
	var tip := Actors.rod_tip(g, fx)
	var hook := Vector2(fishing.hook_x(g) + (fishing.off if fishing.fighting else 0.0), maxf(fishing.hook_y, tip.y + 6.0))
	var color := Color("#E5DDC8")
	var sag := sin(g.tick * 0.05) * 2.0
	if fishing.fighting:
		var t := fishing.tension
		color = color.lerp(Color.WHITE, clampf(t * 1.4, 0.0, 1.0))
		if t > 0.85:
			color = Color("#FF5A4A") if g.tick % 6 < 3 else Color.WHITE
		sag = (1.0 - t) * 14.0 * (1.0 if fishing.off >= 0.0 else -1.0)
	var jitter := sin(g.tick * 2.1) * fx.twitch * 0.25
	var mid := (tip + hook) * 0.5 + Vector2(sag + jitter, 0.0)
	var points := PackedVector2Array()
	for i in 11:
		var t := i / 10.0
		points.append(tip.lerp(mid, t).lerp(mid.lerp(hook, t), t))
	draw_polyline(points, color, 1.0)
	if fishing.fighting:
		return
	hook.y += jitter
	draw_rect(Rect2(hook.x, hook.y, 1, 3), DARK)
	draw_rect(Rect2(hook.x - 2, hook.y + 2, 2, 1), DARK)
	if g.inv.baits[g.inv.bait] > 0:
		var bait: Color = Data.BAITS[g.inv.bait]["color"]
		draw_rect(Rect2(hook.x - 2, hook.y + 3, 3, 3), bait)
		draw_rect(Rect2(hook.x - 3, hook.y + 2, 5, 5), Color(bait, 0.35 if fx.twitch > 0 else 0.0))
