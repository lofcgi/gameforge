class_name Hud
extends Node2D
## 화면 위 정보: 상태 줄, 조작 안내, 깊이 눈금, 장력 게이지, 알림. 패널과 카드는 Panels 가 그린다.

const DARK := Color("#17121B")
const WHITE := Color("#E9F3E2")
const GOLD := Color("#E9D36B")
const RED := Color("#E0564A")
const GREEN := Color("#6CC08B")
const BLUE := Color("#468DB4")
const SIZE := 10

var game: Game
var world: WorldView

var _font: Font = ThemeDB.fallback_font


func advance() -> void:
	queue_redraw()


func text(pos: Vector2, value: String, color := WHITE, size := SIZE) -> void:
	draw_string(_font, pos + Vector2(1, 1), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(DARK, 0.7 * color.a))
	draw_string(_font, pos, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func width(value: String, size := SIZE) -> float:
	return _font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func text_center(center_x: float, y: float, value: String, color := WHITE, size := SIZE) -> void:
	text(Vector2(roundf(center_x - width(value, size) * 0.5), y), value, color, size)


func _draw() -> void:
	if game == null:
		return
	var g := game
	var fx := world.fx
	if not g.menu.cards.is_empty():
		Panels.cards(self, g)
		return
	_status(g, fx)
	if g.mode == "fish":
		_depth_gauge(g, fx)
		if g.fishing.fighting:
			_fight(g, fx)
	_hints(g, fx)
	_toasts(fx)
	if not fx.catch_card.is_empty():
		_catch_card(fx)
	if g.menu.panel != "":
		Panels.panel(self, g, fx)


func _status(g: Game, fx: Fx) -> void:
	draw_rect(Rect2(0, 0, 320, 25), Color(DARK, 0.35))
	var place: String = "작은 섬" if g.mode == "land" and g.land.area == "island" else Sea.zone_at(g.sailing.x if g.mode != "land" else g.land.x)["name"]
	if g.mode != "land":
		place += " %dm" % int(g.sailing.x / Data.X_PX)
	text(Vector2(4, 10), place, GOLD if fx.on("zone") else WHITE)
	var coins := "%d닢" % g.inv.coins
	text(Vector2(316 - width(coins), 10), coins, GOLD if fx.on("coins") else WHITE)
	# 내구도
	var dur: float = g.inv.durability / g.inv.boat_data()["dur"]
	var shake := Vector2(1 if fx.on("hit") and g.tick % 4 < 2 else 0, 0)
	text(Vector2(4, 21) + shake, "배")
	draw_rect(Rect2(Vector2(15, 14) + shake, Vector2(42, 6)), DARK)
	draw_rect(Rect2(Vector2(16, 15) + shake, Vector2(40.0 * dur, 4)), RED if dur < 0.35 or fx.on("hit") else GREEN)
	# 어창: 칸마다 사각형
	text(Vector2(64, 21), "어창")
	var slot := 0
	for id in g.inv.hold:
		var fish := Data.fish(id)
		for i in fish["slots"]:
			draw_rect(Rect2(86 + slot * 5, 15, 4, 5), GOLD if id == "legend" else fish["color"])
			slot += 1
	for i in range(slot, g.inv.hold_cap()):
		draw_rect(Rect2(86 + i * 5, 15, 4, 5), Color(DARK, 0.6))
	# 미끼
	var bait: Dictionary = Data.BAITS[g.inv.bait]
	var count: int = g.inv.baits[g.inv.bait]
	var label := "%s x%d" % [bait["name"], count]
	var bx := 316 - width(label)
	draw_rect(Rect2(bx - 8, 15, 5, 5), bait["color"])
	text(Vector2(bx, 21), label, GOLD if fx.on("bait") else (RED if count == 0 else WHITE))


func _hints(g: Game, fx: Fx) -> void:
	var line := ""
	var prompt := ""
	match g.mode:
		"land":
			line = "←→ 걷기   Space 줍기·열기   C 도감"
			if g.land.near != null:
				var kind: String = g.land.near["kind"]
				prompt = "Space: %s" % ("배 타기" if kind == "board" else g.land.near["name"] + (" 줍기" if kind == "gather" else ""))
		"sail":
			line = "←→ 배 몰기  Space 닻  Q 미끼  H 어창  C 도감"
			if g.sailing.at_pier():
				prompt = "Space: 부두에 대기"
			elif g.sailing.at_island():
				prompt = "Space: 섬에 내리기"
			elif g.inv.durability < g.inv.boat_data()["dur"] * 0.35:
				prompt = "배가 위험하다. 돌아갈까?"
			elif g.inv.hold_used() >= g.inv.hold_cap():
				prompt = "어창이 가득 찼다"
		"fish":
			if g.fishing.fighting:
				line = "Space 누르면 감기·떼면 풀기   ←→ 따라가기"
			else:
				line = "↑↓ 줄   Space 미끼 흔들기   Q 미끼   X 닻 올리기"
				if g.inv.baits[g.inv.bait] <= 0:
					prompt = "미끼가 없다"
				elif fx.on("limit"):
					prompt = "더는 내려가지 않는다"
				elif fx.on("anchored"):
					prompt = "닻을 내렸다. X 로 올리고 움직인다"
	draw_rect(Rect2(0, 168, 320, 12), Color(DARK, 0.45))
	text_center(160, 177, line, Color(WHITE, 0.9))
	if prompt != "":
		var w := width(prompt) + 10
		draw_rect(Rect2(160 - w * 0.5, 153, w, 13), Color(DARK, 0.7))
		text_center(160, 163, prompt, GOLD)


func _depth_gauge(g: Game, fx: Fx) -> void:
	var top := 34.0
	var height := 112.0
	var x := 309.0
	var bed: float = Sea.bed_y(g.fishing.hook_x(g)) / Data.Y_PX
	var reach: float = g.inv.rod_data()["reach"]
	var span := maxf(bed, 10.0)
	draw_rect(Rect2(x - 1, top - 1, 6, height + 2), Color(DARK, 0.6))
	draw_rect(Rect2(x, top, 4, height * minf(1.0, reach / span)), BLUE.lightened(0.3))
	if reach < span:
		draw_rect(Rect2(x, top + height * reach / span, 4, height * (1.0 - reach / span)), Color(RED, 0.5))
	var step := 10 if span <= 60.0 else (20 if span <= 100.0 else 50)
	var mark := 0
	while mark <= span:
		var my := top + height * mark / span
		draw_rect(Rect2(x - 3, my, 3, 1), WHITE)
		text(Vector2(x - 6 - width(str(mark), 8), my + 3), str(mark), Color(WHITE, 0.8), 8)
		mark += step
	var depth := g.fishing.hook_y / Data.Y_PX
	var hy := top + height * clampf(depth / span, 0.0, 1.0)
	var color := RED if fx.on("limit") else GOLD
	draw_colored_polygon(PackedVector2Array([Vector2(x - 6, hy - 3), Vector2(x, hy), Vector2(x - 6, hy + 3)]), color)
	draw_rect(Rect2(x, hy - 1, 5, 2), color)
	var label := "%dm" % int(depth)
	draw_rect(Rect2(x - 12 - width(label), hy - 6, width(label) + 4, 12), Color(DARK, 0.75))
	text(Vector2(x - 10 - width(label), hy + 4), label, color)


## 줄다리기: 왼쪽 가장자리의 세로 장력 게이지(위가 끊어짐, 아래가 느슨함)와 물고기 기력, 아래쪽의 지시 문구.
## 물고기가 화면 가운데에 보이도록 가운데는 비워 둔다.
func _fight(g: Game, fx: Fx) -> void:
	var fishing := g.fishing
	var t := clampf(fishing.tension, 0.0, 1.0)
	var jolt := Vector2(1 if t > 0.85 and g.tick % 4 < 2 else 0, 0)
	var bar := Rect2(Vector2(8, 40) + jolt, Vector2(10, 100))
	var slack_h: float = bar.size.y * Data.TUG["slack_at"]
	draw_rect(bar.grow(2), Color(DARK, 0.8))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x, bar.size.y * 0.15)), RED)
	draw_rect(Rect2(bar.position + Vector2(0, bar.size.y * 0.15), Vector2(bar.size.x, bar.size.y * 0.85 - slack_h)), Color(GREEN, 0.8))
	draw_rect(Rect2(bar.position + Vector2(0, bar.size.y - slack_h), Vector2(bar.size.x, slack_h)), BLUE)
	var my := bar.end.y - bar.size.y * t
	draw_rect(Rect2(bar.position.x - 3, my - 1, bar.size.x + 6, 3), WHITE)
	draw_colored_polygon(PackedVector2Array([Vector2(bar.end.x + 8, my - 4), Vector2(bar.end.x + 3, my), Vector2(bar.end.x + 8, my + 4)]), WHITE)
	text(Vector2(4, 35), "장력", RED if t > 0.85 else WHITE)
	# 기력
	var sp: Dictionary = fishing.engaged["sp"]
	draw_rect(Rect2(31, 40, 4, 100), Color(DARK, 0.8))
	draw_rect(Rect2(31, 140 - 100 * fishing.stamina, 4, 100 * fishing.stamina), GOLD)
	text(Vector2(4, 152), "%s 기력" % sp["name"], GOLD)
	var banner := ""
	var color := WHITE
	match fishing.phase:
		"warn":
			banner = "곧 버틴다…"
			color = GOLD
		"pull":
			var tug: Dictionary = Data.TUG
			if tug["reel_pull"][0] + tug["reel_pull"][1] * fishing.ratio < 0.9:
				# 낚싯대가 넉넉히 버티는 작은 물고기: 감아도 끊어지지 않는다.
				banner = "버티지만 약하다. 감아!"
				color = GREEN
			else:
				banner = "버틴다! 떼!" if fishing.reeling else "버틴다! 기다려"
				color = RED
		"tired":
			banner = "지쳤다! 감아!"
			color = GREEN
		"spent":
			banner = "기진맥진! 감아!"
			color = GREEN
	if fishing.slack_t > 20 and g.tick % 16 < 10:
		banner = "줄이 느슨하다! 감아!"
		color = BLUE.lightened(0.4)
	if absf(fishing.off) > 20.0 and fishing.phase == "pull":
		banner += "  →→" if fishing.off > 0.0 else "  ←←"
	var w := width(banner, 12) + 12
	draw_rect(Rect2(160 - w * 0.5, 151, w, 16), Color(DARK, 0.8))
	text_center(160, 163, banner, color, 12)
	if fishing.reeling:
		draw_rect(Rect2(160 + w * 0.5 + 3, 155, 7, 7), WHITE if g.tick % 8 < 4 else GOLD)


func _toasts(fx: Fx) -> void:
	var y := 38.0
	for toast in fx.toasts:
		var alpha := minf(1.0, toast["t"] / 20.0)
		var w := width(toast["text"]) + 10
		draw_rect(Rect2(160 - w * 0.5, y - 10, w, 13), Color(DARK, 0.7 * alpha))
		text_center(160, y, toast["text"], Color(WHITE, alpha))
		y += 15.0


func _catch_card(fx: Fx) -> void:
	var sp := Data.fish(fx.catch_card["id"])
	var pop := minf(1.0, (150 - fx.catch_card["t"]) / 8.0)
	var box := Rect2(160 - 50 * pop, 66, 100 * pop, 34)
	draw_rect(box, Color(DARK, 0.8))
	draw_rect(box.grow(-1), Color(WHITE, 0.12))
	if pop < 1.0:
		return
	Actors.fish_shape(self, Vector2.ZERO, Vector2(134, 83), sp, 1.0, 0.0)
	text(Vector2(156, 80), sp["name"], GOLD if fx.catch_card["new"] else WHITE)
	text(Vector2(156, 93), "새 어종!" if fx.catch_card["new"] else "%d닢 · %d칸" % [sp["price"], sp["slots"]], WHITE)
