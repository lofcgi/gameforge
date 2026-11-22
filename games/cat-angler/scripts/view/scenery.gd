class_name Scenery
## 움직이지 않는 것들의 도형 그리기: 먼 배경, 항구, 섬, 암초, 난파선, 소용돌이, 바닥 장식.

const GRASS := Color("#96B89D")
const SAND := Color("#E5DDC8")
const SOIL := Color("#DFB68B")
const WOOD := Color("#8C533C")
const ROCK := Color("#546166")
const DARK := Color("#17121B")
const WHITE := Color("#E9F3E2")
const KEEPERS := {"bench": Color("#799088"), "market": Color("#B4774F"), "shipyard": Color("#8C533C"), "tackle": Color("#B8D0BF")}


static func ground_y(area: String, x: float) -> float:
	if area != "island":
		return -6.0
	var local := (x - Sea.place_x("island") - 4.0) / 58.0
	return -3.0 - 22.0 * maxf(0.0, 1.0 - local * local)


## 먼 배경 한 겹을 흰색으로 그린다(색은 노드의 modulate 로 입힌다). 무늬는 PERIOD 마다 되풀이되고,
## 노드가 한 번만 그린 뒤 위치만 옮기므로 매 프레임 다시 그리지 않는다. y=0 이 수면선이다.
const PERIOD := {"clouds": 485.0, "mountains": 750.0, "islets": 780.0}


static func backdrop(c: CanvasItem, kind: String) -> void:
	for lap in 2:
		var base: float = lap * PERIOD[kind]
		match kind:
			"clouds":
				for i in 5:
					var px := base + i * 97.0
					var py := -70.0 + (i % 3) * 13.0
					c.draw_rect(Rect2(px, py, 34, 5), Color.WHITE)
					c.draw_rect(Rect2(px + 8, py - 4, 18, 4), Color.WHITE)
			"mountains":
				for i in 5:
					var px := base + i * 150.0
					var h := 22.0 + (i * 37 % 20)
					c.draw_colored_polygon(PackedVector2Array([Vector2(px, 0), Vector2(px + 50, -h), Vector2(px + 78, -h * 0.6),
						Vector2(px + 120, 0)]), Color.WHITE)
			"islets":
				for i in 3:
					var px := base + i * 260.0
					c.draw_colored_polygon(PackedVector2Array([Vector2(px, 0), Vector2(px + 14, -9), Vector2(px + 34, -12),
						Vector2(px + 52, 0)]), Color.WHITE)
					c.draw_rect(Rect2(px + 24, -19, 1, 8), Color.WHITE)
					c.draw_rect(Rect2(px + 21, -21, 7, 3), Color.WHITE)


static func port(c: CanvasItem, g: Game, font: Font) -> void:
	var land := PackedVector2Array([Vector2(-400, -6), Vector2(560, -6), Vector2(612, 30), Vector2(640, 70), Vector2(-400, 70)])
	c.draw_colored_polygon(land, SOIL)
	c.draw_rect(Rect2(-400, -6, 590, 3), GRASS)
	c.draw_rect(Rect2(190, -6, 370, 2), SAND)
	for i in 7:
		var px := -150.0 + i * 26.0
		c.draw_rect(Rect2(px + 4, -16, 3, 10), WOOD)
		c.draw_colored_polygon(PackedVector2Array([Vector2(px - 6, -14), Vector2(px + 5, -44 - (i % 3) * 6), Vector2(px + 17, -14)]), Color("#28706F"))
	c.draw_rect(Rect2(552, -7, 64, 2), WOOD)
	for px in [560, 584, 608]:
		c.draw_rect(Rect2(px, -5, 2, 26), WOOD)
	for station in Data.STATIONS:
		var x: float = station["x"]
		var near: bool = g.mode == "land" and g.land.near == station
		match station["id"]:
			"herb", "bug", "berry":
				var full: bool = g.land.stock[station["id"]] > 0
				var color: Color = Data.MATS[station["id"]]["color"]
				if station["id"] == "berry":
					c.draw_rect(Rect2(x - 1, -24, 3, 18), WOOD)
					c.draw_circle(Vector2(x, -27), 9.0, Color("#439083"))
				else:
					c.draw_colored_polygon(PackedVector2Array([Vector2(x - 10, -6), Vector2(x - 4, -14), Vector2(x + 5, -15), Vector2(x + 10, -6)]),
						Color("#439083"))
				if full:
					for i in 5:
						var dy := -26.0 if station["id"] == "berry" else -10.0
						c.draw_rect(Rect2(x - 7 + i * 3, dy - (i % 2) * 4, 2, 2), color)
			"bench":
				c.draw_rect(Rect2(x - 12, -15, 24, 2), WOOD)
				c.draw_rect(Rect2(x - 10, -13, 2, 7), WOOD)
				c.draw_rect(Rect2(x + 8, -13, 2, 7), WOOD)
			"market":
				c.draw_rect(Rect2(x - 16, -18, 32, 12), Color("#B4774F"))
				c.draw_colored_polygon(PackedVector2Array([Vector2(x - 20, -18), Vector2(x - 14, -27), Vector2(x + 14, -27), Vector2(x + 20, -18)]),
					Color("#D46A7E"))
			"shipyard":
				c.draw_rect(Rect2(x - 20, -30, 40, 24), Color("#799088"))
				c.draw_colored_polygon(PackedVector2Array([Vector2(x - 24, -30), Vector2(x, -42), Vector2(x + 24, -30)]), ROCK)
				c.draw_colored_polygon(PackedVector2Array([Vector2(x - 12, -14), Vector2(x + 12, -14), Vector2(x + 8, -8), Vector2(x - 8, -8)]), WOOD)
			"tackle":
				c.draw_rect(Rect2(x - 14, -24, 28, 18), Color("#7BAEB9"))
				c.draw_colored_polygon(PackedVector2Array([Vector2(x - 18, -24), Vector2(x, -34), Vector2(x + 18, -24)]), Color("#426A96"))
				c.draw_line(Vector2(x + 16, -8), Vector2(x + 24, -34), WOOD, 1.0)
			"pier":
				c.draw_rect(Rect2(x - 1, -20, 2, 14), WOOD)
				c.draw_rect(Rect2(x, -20, 9, 5), Color("#D46A7E"))
		if KEEPERS.has(station["id"]):
			var keeper: Color = KEEPERS[station["id"]]
			var bob := 0.0
			c.draw_rect(Rect2(x + 14, -13 + bob, 6, 7), keeper)
			c.draw_rect(Rect2(x + 14, -18 + bob, 6, 5), keeper.lightened(0.2))
			c.draw_rect(Rect2(x + 14, -20 + bob, 2, 2), keeper.lightened(0.2))
			c.draw_rect(Rect2(x + 18, -20 + bob, 2, 2), keeper.lightened(0.2))
		var width := font.get_string_size(station["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
		c.draw_string(font, Vector2(x - width * 0.5, -48), station["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 10,
			DARK if near else Color(DARK, 0.45))


static func island(c: CanvasItem, g: Game, font: Font) -> void:
	var cx := Sea.place_x("island")
	var hill := PackedVector2Array()
	for i in 15:
		var px := cx - 58.0 + i * 8.5
		hill.append(Vector2(px, ground_y("island", px)))
	hill.append(Vector2(cx + 70, 30))
	hill.append(Vector2(cx - 66, 30))
	c.draw_colored_polygon(hill, SAND)
	c.draw_rect(Rect2(cx - 22, -26, 46, 3), GRASS)
	c.draw_rect(Rect2(cx - 4, -50, 3, 26), WOOD)
	c.draw_colored_polygon(PackedVector2Array([Vector2(cx - 18, -46), Vector2(cx - 2, -56), Vector2(cx + 14, -46), Vector2(cx - 2, -49)]),
		Color("#439083"))
	c.draw_rect(Rect2(cx - 62, -5, 22, 2), WOOD)
	c.draw_rect(Rect2(cx - 60, -3, 2, 12), WOOD)
	var fx := cx + 34.0
	var fy := ground_y("island", fx)
	c.draw_rect(Rect2(fx, fy - 6, 1, 6), Color("#439083"))
	if g.land.stock["flower"] > 0:
		c.draw_rect(Rect2(fx - 2, fy - 9, 5, 3), Data.MATS["flower"]["color"])
		c.draw_rect(Rect2(fx - 1, fy - 10, 3, 5), Data.MATS["flower"]["color"])
		c.draw_rect(Rect2(fx + 4, fy - 13, 1, 1), WHITE)
	var width := font.get_string_size("작은 섬", HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	c.draw_string(font, Vector2(cx - width * 0.5, -62), "작은 섬", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(DARK, 0.5))


## 수면 위로 보이는 장소 표시: 암초의 바위, 난파선의 부표, 소용돌이.
static func surface_marks(c: CanvasItem, origin: Vector2, g: Game, from: float, to: float) -> void:
	var tick := g.tick
	var reef := Sea.place_x("reef")
	for i in (5 if reef > from - 100.0 and reef < to + 100.0 else 0):
		var px := reef - 70.0 + i * 34.0
		var top := -3.0 - (i * 7 % 9)
		var sy := g.sailing.surface_y(px, tick)
		c.draw_colored_polygon(PackedVector2Array([Vector2(px - 9, 8), Vector2(px - 3, top), Vector2(px + 4, top + 2), Vector2(px + 10, 8)]), ROCK)
		c.draw_rect(Rect2(px - 11, sy + 1, 22, 1), WHITE)
	var wreck := Sea.place_x("wreck")
	if wreck > from - 20.0 and wreck < to + 20.0:
		var wy := g.sailing.surface_y(wreck, tick)
		c.draw_line(Vector2(wreck, wy + 4), Vector2(wreck + 5, wy - 16), WOOD, 2.0)
		c.draw_rect(Rect2(wreck + 5, wy - 16, 8, 5), Color("#D46A7E"))
		c.draw_rect(Rect2(wreck - 4, wy - 2, 8, 4), Color("#B4774F"))


## 소용돌이는 물 위에 겹쳐 보여야 하므로 수면을 그린 뒤에 그린다.
static func vortex_mark(c: CanvasItem, origin: Vector2, g: Game, from: float, to: float) -> void:
	var tick := g.tick
	var vortex := Sea.place_x("vortex")
	var vy := g.sailing.surface_y(vortex, tick)
	for i in (4 if vortex > from - 50.0 and vortex < to + 50.0 else 0):
		var radius := 8.0 + i * 9.0
		var spin := tick * 0.05 + i * 1.3
		c.draw_set_transform(origin + Vector2(vortex, vy + 3.0), 0.0, Vector2(1.0, 0.22))
		c.draw_arc(Vector2.ZERO, radius, spin, spin + 2.4, 10, Color(WHITE, 0.8 - i * 0.15), 1.0)
		c.draw_arc(Vector2.ZERO, radius, spin + PI, spin + PI + 1.4, 8, Color(WHITE, 0.5 - i * 0.1), 1.0)
	c.draw_set_transform(origin)


## 바닥 위의 장식: 해초(얕은 바다), 유적 기둥(먼바다), 난파선, 자개빛 누각(심해 입구).
static func bed_decor(c: CanvasItem, from: float, to: float, tick: int) -> void:
	var start := floorf(from / 46.0) * 46.0
	var px := start
	while px < to:
		var by := Sea.bed_y(px)
		var zone: String = Sea.zone_at(px)["id"]
		var pick := int(absf(px) / 46.0)
		if by > 20.0:
			if zone == "shallow":
				var sway := sin(tick * 0.04 + px) * 2.0
				c.draw_polyline(PackedVector2Array([Vector2(px, by), Vector2(px + sway * 0.5, by - 6), Vector2(px + sway, by - 11 - pick % 5)]),
					Color("#439083"), 1.0)
			elif zone == "open" and not Sea.near_place(px, "reef", 20.0) and pick % 2 == 0:
				var h := 10.0 + (pick * 13 % 18)
				c.draw_rect(Rect2(px - 3, by - h, 6, h + 2), Color("#96B89D", 0.55))
				c.draw_rect(Rect2(px - 5, by - h - 2, 10, 3), Color("#96B89D", 0.55))
			elif zone == "deep":
				c.draw_rect(Rect2(px, by - 4 - pick % 3, 2, 2), Color("#76D7D9", 0.5 + 0.4 * sin(tick * 0.05 + px)))
		px += 46.0
	var wreck := Sea.place_x("wreck")
	if wreck > from - 80.0 and wreck < to + 80.0:
		var by := Sea.bed_y(wreck)
		c.draw_colored_polygon(PackedVector2Array([Vector2(wreck - 42, by - 6), Vector2(wreck + 34, by - 22), Vector2(wreck + 46, by - 12),
			Vector2(wreck + 30, by + 2), Vector2(wreck - 34, by + 2)]), Color("#5E342B"))
		c.draw_line(Vector2(wreck - 6, by - 12), Vector2(wreck + 6, by - 46), Color("#5E342B"), 2.0)
		c.draw_rect(Rect2(wreck - 14, by - 10, 6, 5), DARK)
		c.draw_rect(Rect2(wreck + 8, by - 13, 6, 5), DARK)
	var vortex := Sea.place_x("vortex")
	if vortex > from - 120.0 and vortex < to + 120.0:
		var by := Sea.bed_y(vortex)
		var jade := Color("#439083")
		var px2 := vortex + 60.0
		for i in 3:
			c.draw_rect(Rect2(px2 - 20 + i * 18, by - 26, 4, 26), jade)
		c.draw_colored_polygon(PackedVector2Array([Vector2(px2 - 34, by - 26), Vector2(px2 - 22, by - 40), Vector2(px2 + 22, by - 40),
			Vector2(px2 + 34, by - 26)]), Color("#28706F"))
		c.draw_rect(Rect2(px2 - 30, by - 28, 60, 2), Color("#54A9A7"))
