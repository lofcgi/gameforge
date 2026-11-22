class_name Actors
## 움직이는 것들의 도형 그리기: 배와 고양이, 물고기, 어군 표시, 떠다니는 물건. 그림이 생기면 여기를 바꾼다.

const WOOD := Color("#8C533C")
const WOOD_LIGHT := Color("#B4774F")
const CAT := Color("#D79966")
const CREAM := Color("#E5DDC8")
const DARK := Color("#17121B")
const WHITE := Color("#E9F3E2")
const DECK := [-3.0, -4.0, -6.0]


static func rod_tip(g: Game, fx: Fx) -> Vector2:
	var deck: float = DECK[g.inv.boat]
	var bend := g.fishing.tension * 5.0 if g.fishing.fighting else 0.0
	var local := Vector2(16.0 * fx.facing, deck - 13.0 + bend)
	return Vector2(g.sailing.x, g.sailing.y).round() + local.rotated(g.sailing.tilt)


static func boat(c: CanvasItem, origin: Vector2, g: Game, fx: Fx) -> void:
	var tier := g.inv.boat
	var deck: float = DECK[tier]
	c.draw_set_transform(origin + Vector2(g.sailing.x, g.sailing.y).round(), g.sailing.tilt, Vector2(fx.facing, 1))
	match tier:
		0:
			c.draw_colored_polygon(PackedVector2Array([Vector2(-13, -3), Vector2(14, -3), Vector2(10, 3), Vector2(-10, 3)]), WOOD)
			c.draw_rect(Rect2(-13, -4, 27, 1), WOOD_LIGHT)
		1:
			c.draw_rect(Rect2(-6, -26, 1, 22), WOOD)
			c.draw_colored_polygon(PackedVector2Array([Vector2(-7, -25), Vector2(-7, -9), Vector2(-17, -9)]), CREAM)
			c.draw_colored_polygon(PackedVector2Array([Vector2(-17, -4), Vector2(20, -4), Vector2(14, 4), Vector2(-14, 4)]), WOOD)
			c.draw_rect(Rect2(-17, -5, 37, 1), WOOD_LIGHT)
		2:
			c.draw_rect(Rect2(-3, -34, 1, 28), WOOD)
			c.draw_colored_polygon(PackedVector2Array([Vector2(-4, -33), Vector2(-4, -15), Vector2(-16, -15)]), CREAM)
			c.draw_rect(Rect2(-20, -14, 13, 8), WOOD_LIGHT)
			c.draw_rect(Rect2(-17, -12, 3, 3), Color("#7BAEB9"))
			c.draw_colored_polygon(PackedVector2Array([Vector2(-23, -6), Vector2(27, -6), Vector2(20, 5), Vector2(-19, 5)]), WOOD)
			c.draw_rect(Rect2(-23, -7, 50, 1), WOOD_LIGHT)
			c.draw_rect(Rect2(-20, -2, 42, 1), Color("#28706F"))
	if g.mode != "land":
		var bend := g.fishing.tension * 5.0 if g.fishing.fighting else 0.0
		cat(c, Vector2(2, deck), g.tick, fx.ears > 0)
		c.draw_line(Vector2(6, deck - 5), Vector2(16, deck - 13 + bend), WOOD_LIGHT, 1.0)
	if g.mode == "fish":
		c.draw_line(Vector2(-10, 2), Vector2(-10, 9), Color("#546166"), 1.0)
	c.draw_set_transform(origin)


## 발밑 가운데가 pos 인 고양이.
static func cat(c: CanvasItem, pos: Vector2, tick: int, alert: bool) -> void:
	var sway := sin(tick * 0.08) * 1.5
	c.draw_polyline(PackedVector2Array([pos + Vector2(-3, -2), pos + Vector2(-6, -4 + sway * 0.5), pos + Vector2(-7, -7 + sway)]), CAT, 1.0)
	c.draw_rect(Rect2(pos.x - 3, pos.y - 6, 6, 6), CAT)
	c.draw_rect(Rect2(pos.x - 1, pos.y - 4, 3, 4), CREAM)
	c.draw_rect(Rect2(pos.x - 1, pos.y - 11, 6, 5), CAT)
	var ear := 4.0 if alert or tick % 240 < 8 else 2.0
	c.draw_colored_polygon(PackedVector2Array([pos + Vector2(-1, -11), pos + Vector2(1, -11), pos + Vector2(0, -11 - ear)]), CAT)
	c.draw_colored_polygon(PackedVector2Array([pos + Vector2(3, -11), pos + Vector2(5, -11), pos + Vector2(4, -11 - ear)]), CAT)
	c.draw_rect(Rect2(pos.x + 3, pos.y - 9, 1, 1), DARK)


static func fish_size(sp: Dictionary) -> Vector2:
	var length: float = 7.0 + sp["slots"] * 4.5
	match sp["shape"]:
		"flat":
			return Vector2(length, length * 0.24)
		"long":
			return Vector2(length * 1.5, maxf(2.0, length * 0.16))
	return Vector2(length, length * 0.44)


## 오른쪽을 보는 물고기를 pos 에 그린다. flip 이 -1 이면 왼쪽을 본다.
static func fish_shape(c: CanvasItem, origin: Vector2, pos: Vector2, sp: Dictionary, flip: float, wag: float,
		squash := 1.0, body := Color.TRANSPARENT, turn := 0.0, zoom := 1.0) -> void:
	var size := fish_size(sp)
	var color: Color = sp["color"] if body == Color.TRANSPARENT else body
	var half := size * 0.5
	c.draw_set_transform(origin + pos.round(), turn, Vector2(flip * squash, 1) * zoom)
	# 덩어리 몸통: 긴 띠 + 굵은 가운데, 꼬리 두 조각, 등지느러미. 사각형만 써서 한 번에 묶여 그려진다.
	c.draw_rect(Rect2(-half.x, -half.y * 0.55, size.x, half.y * 1.1), color)
	c.draw_rect(Rect2(-half.x * 0.7, -half.y, size.x * 0.68, size.y), color)
	var tail := maxf(2.0, half.x * 0.5)
	c.draw_rect(Rect2(-half.x - tail, -half.y * 0.9 + wag, tail * 0.6, half.y * 1.8), color)
	c.draw_rect(Rect2(-half.x - tail * 0.5, -half.y * 0.45 + wag * 0.5, tail * 0.6, half.y * 0.9), color)
	c.draw_rect(Rect2(-half.x * 0.3, -half.y - 1.5, half.x * 0.5, 2), color)
	if body == Color.TRANSPARENT:
		c.draw_rect(Rect2(-half.x * 0.6, half.y * 0.2, size.x * 0.6, maxf(1.0, half.y * 0.5)), color.lightened(0.3))
		c.draw_rect(Rect2(half.x * 0.55, -half.y * 0.35, 1, 1), DARK)
	c.draw_set_transform(origin)


static func fish(c: CanvasItem, origin: Vector2, f: Dictionary, g: Game, font: Font) -> void:
	var sp: Dictionary = f["sp"]
	var pos := Vector2(f["x"], f["y"])
	var hooked: bool = f["state"] == "hooked"
	var pulling := hooked and g.fishing.phase == "pull"
	var wag := sin(g.tick * (0.6 if pulling else 0.25) + f["phase"]) * (2.0 if pulling else 1.0)
	var squash := 0.6 if f["squash"] > 0 else 1.0
	var body := Color.TRANSPARENT
	if sp["id"] == "legend" and not hooked:
		body = Actors.DARK
	var turn := sin(g.tick * 0.7) * 0.25 if pulling else 0.0
	fish_shape(c, origin, pos, sp, f["dir"], wag, squash, body, turn)
	if sp["zone"] == "deep" and body == Color.TRANSPARENT:
		c.draw_rect(Rect2(pos.x + f["dir"] * fish_size(sp).x * 0.5 - 1, pos.y - fish_size(sp).y * 0.5 - 3, 2, 2), Color("#76D7D9"))
	var mark := ""
	match f["state"]:
		"sniff":
			mark = "?"
		"nibble":
			mark = "…"
		"hooked":
			mark = "!" if pulling else ""
	if mark != "":
		c.draw_string(font, pos + Vector2(-3, -fish_size(sp).y * 0.5 - 4), mark, HORIZONTAL_ALIGNMENT_LEFT, -1, 10,
			Color("#E9D36B"))


## 어군 표시: 작은 어종은 잔물결 여럿과 새 셋, 중간은 물거품과 새 둘, 큰 어종은 큰 그림자와 새 하나.
static func school(c: CanvasItem, s: Dictionary, surface: float, tick: int) -> void:
	var sp := Data.fish(s["sp"])
	var alpha := clampf(minf(s["age"] / 60.0, s["life"] / 180.0), 0.0, 1.0)
	var center := Vector2(s["x"], surface)
	var tint := Color(sp["color"], alpha)
	var foam := Color(WHITE, alpha)
	var slots: int = sp["slots"]
	if slots >= 3:
		c.draw_rect(Rect2(center.x - 20, center.y + 6, 40, 7), Color(DARK, 0.3 * alpha))
		c.draw_rect(Rect2(center.x - 14, center.y + 4, 28, 11), Color(DARK, 0.3 * alpha))
		var ring := 10.0 + (tick % 90) / 90.0 * 16.0
		c.draw_arc(center + Vector2(0, 1), ring, PI * 1.1, PI * 1.9, 8, Color(WHITE, alpha * (1.0 - (tick % 90) / 90.0)), 1.0)
	for i in (6 if slots == 1 else 3):
		var drift := sin(tick * 0.05 + i * 1.7) * 3.0
		var px := center.x - 18.0 + i * (36.0 / (5 if slots == 1 else 2)) + drift
		if slots == 1:
			c.draw_rect(Rect2(px, center.y + 1 + (i % 2) * 3, 4, 1), foam)
			c.draw_rect(Rect2(px + 1, center.y + 4 + (i % 3) * 2, 2, 1), tint)
		else:
			c.draw_rect(Rect2(px - 2, center.y, 6, 2), foam)
			c.draw_rect(Rect2(px, center.y + 5, 3, 2), tint)
	var birds := 3 if slots == 1 else (2 if slots == 2 else 1)
	for i in birds:
		var a := tick * 0.03 + i * TAU / birds
		var at := center + Vector2(cos(a) * (12.0 + slots * 2.0), -18.0 - slots * 2.0 + sin(a) * 5.0)
		var wing := 2.0 + slots + sin(tick * 0.3 + i) * 1.0
		c.draw_polyline(PackedVector2Array([at + Vector2(-wing, -1), at, at + Vector2(wing, -1)]), Color(DARK, alpha), 1.0)


static func flotsam(c: CanvasItem, origin: Vector2, item: Dictionary, surface: float, tick: int) -> void:
	var rock := sin(tick * 0.05 + item["x"]) * 0.2
	c.draw_set_transform(origin + Vector2(item["x"], surface).round(), rock)
	if item["kind"] == "crate":
		c.draw_rect(Rect2(-4, -5, 8, 7), WOOD_LIGHT)
		c.draw_rect(Rect2(-4, -2, 8, 1), WOOD)
		c.draw_rect(Rect2(-1, -5, 1, 7), WOOD)
	else:
		c.draw_rect(Rect2(-1, -6, 3, 7), Color("#439083"))
		c.draw_rect(Rect2(0, -8, 1, 2), CREAM)
		c.draw_rect(Rect2(0, -4, 1, 3), CREAM)
	c.draw_set_transform(origin)
