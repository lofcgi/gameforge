class_name Hud
extends Node2D
## 화면 위 정보: 상태 줄(위), 할 일 띠, 조작 안내(아래), 깊이 눈금과 장력 게이지(양옆), 알림, 낚은 물고기 카드, 날아가는 동전.
## 놀이 영역을 가리지 않게 가장자리에만 둔다. 조작 안내에는 지금 실제로 하는 일이 있는 키만 나온다.

const PLACE_NAMES := {"town": "항구 마을", "forage": "채집지", "island": "작은 섬"}
const COIN_AT := Vector2(548, 7)
const GOOD := Color("#96B89D")
const WARN := Color("#D79966")
const COLD := Color("#468DB4")

var game: Game
var fx: Fx


func setup(g: Game, effects: Fx) -> void:
	game = g
	fx = effects


func _ready() -> void:
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED


func advance() -> void:
	queue_redraw()


func _draw() -> void:
	var g := game
	if g.scene == "title":
		_hints(g)
		return
	if g.mode == "cut":
		_hints(g)
		return
	_status(g)
	if g.scene == "sea" and g.mode == "fish" and not g.menu.busy():
		_depth_ruler(g)
		if g.fishing.fighting:
			_fight(g)
	_guide(g)
	_toasts()
	if not fx.catch_card.is_empty():
		_catch_card()
	_coins()
	_hints(g)
	if fx.on("hit"):
		draw_rect(Rect2(Vector2.ZERO, Ui.SCREEN), Color(Pal.WHITE, 0.35 * fx.flash["hit"] / 40.0))


# ---- 상태 줄 ----

func _status(g: Game) -> void:
	var place: String = PLACE_NAMES.get(g.scene, "")
	if g.scene == "sea":
		place = "%s  %dm" % [Sea.zone_at(g.sailing.x)["name"], int(g.sailing.x / Data.X_PX)]
	elif g.mode == "shop":
		place = g.shop.data()["title"]
	var w := Ui.width(place) + 32.0
	Ui.box(self, "panel", Rect2(4, 3, w, 24))
	Ui.text(self, Vector2(20, 8), place, Pal.TEAL_D if fx.on("zone") and g.tick % 16 < 8 else Pal.BARK)

	# 오른쪽: 돈과 고른 미끼
	var coins := "%d닢" % g.inv.coins
	var bait: Dictionary = Data.BAITS[g.inv.bait]
	var bait_text := "%s ×%d" % [bait["name"], g.inv.baits[g.inv.bait]]
	var right_w := 16.0 + Ui.width(coins) + 20.0 + 16.0 + Ui.width(bait_text) + 44.0
	var rx := 636.0 - right_w
	Ui.box(self, "panel", Rect2(rx, 3, right_w, 24))
	var bx := rx + 16.0
	Ui.icon(self, "items/bait_%s.png" % g.inv.bait, Vector2(bx, 7 - (2 if fx.on("bait") else 0)))
	bx += 18.0
	Ui.text(self, Vector2(bx, 8), bait_text, Pal.TEAL_D if fx.on("bait") else (Pal.BARK if g.inv.baits[g.inv.bait] > 0 else WARN))
	bx += Ui.width(bait_text) + 12.0
	Ui.icon(self, "ui/icon_coin.png", Vector2(bx, 7 - (2 if fx.on("coins") and g.tick % 8 < 4 else 0)))
	Ui.text(self, Vector2(bx + 18.0, 8), coins, Pal.TEAL_D if fx.on("coins") else Pal.BARK)

	if g.scene != "sea" and g.scene != "in_yard" and g.scene != "in_market":
		return
	# 가운데: 배의 내구도와 어창
	var cap: float = g.inv.boat_data()["dur"]
	var frac: float = g.inv.durability / cap
	var hold := "%d/%d" % [g.inv.hold_used(), g.inv.hold_cap()]
	var mid_w := 16.0 + 70.0 + 30.0 + 16.0 + Ui.width(hold) + 44.0
	var mx := roundf(320.0 - mid_w * 0.5)
	Ui.box(self, "panel", Rect2(mx, 3, mid_w, 24))
	mx += 8.0
	var shake := Vector2(0, -1) if fx.on("hit") and g.tick % 4 < 2 else Vector2.ZERO
	Ui.icon(self, "ui/icon_durability.png", Vector2(mx + 8, 7) + shake)
	Ui.gauge(self, Rect2(mx + 28, 9, 64, 12), frac, GOOD if frac > 0.4 else WARN)
	Ui.text(self, Vector2(mx + 96, 8), "%d" % int(g.inv.durability), Pal.BARK if frac > 0.4 else WARN)
	Ui.icon(self, "ui/icon_hold.png", Vector2(mx + 122, 7))
	Ui.text(self, Vector2(mx + 142, 8), hold, WARN if g.inv.hold_used() >= g.inv.hold_cap() else Pal.BARK)


# ---- 할 일 띠 ----

func _guide(g: Game) -> void:
	var text := g.guide.text()
	if text == "" or g.menu.busy() or g.transitioning() or (g.mode == "shop" and g.shop.talking()):
		return
	var w := Ui.width(text) + 76.0
	var x := roundf(320.0 - w * 0.5)
	var fresh := g.tick - g.guide.changed < 90 and g.tick % 20 < 10
	Ui.box(self, "bubble", Rect2(x, 30, w, 24))
	Ui.box(self, "button_focus" if fresh else "button", Rect2(x + 12, 33, 40, 18), 8)
	Ui.text(self, Vector2(x + 20, 36), "할 일", Pal.TEAL_D if fresh else Pal.BARK)
	Ui.text(self, Vector2(x + 58, 36), text, Pal.BARK)


# ---- 알림 ----

func _toasts() -> void:
	var y := 58.0 if game.guide.text() != "" else 32.0
	for toast in fx.toasts:
		var w := Ui.width(toast["text"]) + 36.0
		var slide := Ui.ease_out(minf(1.0, (190 - toast["t"]) / 10.0))
		var x := roundf(320.0 - w * 0.5)
		if toast["t"] > 12:
			Ui.box(self, "panel", Rect2(x, y - (1.0 - slide) * 8.0, w, 24))
			Ui.text(self, Vector2(x + 18, y + 5 - (1.0 - slide) * 8.0), toast["text"], Pal.BARK)
		y += 26.0


func _catch_card() -> void:
	var card := fx.catch_card
	var sp := Data.fish(card["id"])
	var t: int = card["t"]
	var scale := Ui.pop(t / 14.0) if t < 150 else maxf(0.0, 1.0 - (t - 150) / 12.0)
	if scale <= 0.02:
		return
	var size := Vector2(236, 80)
	var center := Vector2(320, 124)
	draw_set_transform(center, 0.0, Vector2(scale, scale))
	Ui.box(self, "panel", Rect2(-size * 0.5, size))
	draw_texture(Assets.tex("fish/%s_card.png" % card["id"]), Vector2(-110, -32))
	var tx := -6.0
	if card["new"]:
		Ui.box(self, "button_focus", Rect2(tx, -30, Ui.width("새 어종!") + 12, 18), 8)
		Ui.text(self, Vector2(tx + 6, -28), "새 어종!", Pal.TEAL_D)
	Ui.text(self, Vector2(tx, -8), sp["name"], Pal.BARK)
	Ui.text(self, Vector2(tx, 10), "용궁에 바친다" if sp["id"] == "legend" else "%d닢 · %d칸" % [sp["price"], sp["slots"]], Pal.WOOD)
	draw_set_transform(Vector2.ZERO)


func _coins() -> void:
	var coin := Assets.tex("items/coin.png")
	for c in fx.coins:
		if c["delay"] > 0:
			continue
		var t := Ui.ease_out(c["t"] / float(Fx.COIN_TICKS))
		var from: Vector2 = c["from"]
		var at := from.lerp(COIN_AT, t * t) - Vector2(0, sin(t * PI) * 40.0)
		draw_texture(coin, at.round())


# ---- 낚시 ----

func _depth_ruler(g: Game) -> void:
	var fishing := g.fishing
	var top := 60.0
	var height := 260.0
	var bed_m: float = maxf(10.0, Sea.bed_y(fishing.hook_x(g)) / Data.Y_PX)
	var reach: float = g.inv.rod_data()["reach"]
	var span := maxf(bed_m, 12.0)
	var ruler := Assets.tex("ui/depth_ruler.png")
	draw_texture_rect(ruler, Rect2(6, top, 24, height), true)
	draw_rect(Rect2(6, top - 2, 24, 2), Pal.BARK)
	draw_rect(Rect2(6, top + height, 24, 3), Pal.BARK)
	var step := 5.0 if span <= 40.0 else (10.0 if span <= 90.0 else 25.0)
	var m := 0.0
	while m <= span:
		var y := roundf(top + height * m / span)
		Ui.text(self, Vector2(8, y - 5 if m > 0.0 else y + 1), "%d" % int(m), Pal.WOOD, "small")
		m += step
	# 낚싯대가 닿는 한계
	if reach < span:
		var ry := roundf(top + height * reach / span)
		draw_rect(Rect2(4, ry, 28, 2), WARN if not fx.on("limit") or g.tick % 6 < 3 else Pal.WHITE)
		draw_rect(Rect2(6, ry + 2, 24, top + height - ry - 2), Color(Pal.INK, 0.45))
	# 미끼의 깊이
	var depth: float = fishing.hook_y / Data.Y_PX
	var hy := roundf(top + height * clampf(depth / span, 0.0, 1.0))
	draw_colored_polygon(PackedVector2Array([Vector2(40, hy - 5), Vector2(32, hy), Vector2(40, hy + 5)]), Pal.CREAM)
	draw_polyline(PackedVector2Array([Vector2(40, hy - 5), Vector2(32, hy), Vector2(40, hy + 5), Vector2(40, hy - 5)]), Pal.BARK, 1.0)
	Ui.label(self, Vector2(44, hy - 7), "%dm" % int(depth), Pal.WHITE if not fx.on("limit") else WARN)
	if fx.on("limit"):
		Ui.label(self, Vector2(44, hy + 8), "낚싯대가 여기까지" if reach < bed_m - 1.0 else "바닥이다", WARN)


func _fight(g: Game) -> void:
	var fishing := g.fishing
	var t := fishing.tension
	var frame := Rect2(606, 78, 24, 168)
	Ui.box(self, "tension_frame", frame, 6)
	var inner := frame.grow(-3.0)
	var slack_h: float = inner.size.y * Data.TUG["slack_at"]
	var danger_h := inner.size.y * 0.12
	draw_rect(Rect2(inner.position.x, inner.end.y - slack_h, inner.size.x, slack_h), Color(COLD, 0.55))
	draw_rect(Rect2(inner.position, Vector2(inner.size.x, danger_h)), Color(WARN, 0.55))
	var color := GOOD
	if t < Data.TUG["slack_at"]:
		color = COLD
	elif t > 0.85:
		color = Pal.WHITE if g.tick % 6 < 3 else WARN
	var fill_h := roundf(inner.size.y * clampf(t, 0.0, 1.0))
	draw_texture_rect(Assets.tex("ui/tension_fill.png"), Rect2(inner.position.x + 3, inner.end.y - fill_h, inner.size.x - 6, fill_h), false, color)
	draw_rect(Rect2(inner.position.x, inner.end.y - fill_h - 1, inner.size.x, 2), Pal.WHITE)
	Ui.label_center(self, 618, 250, "장력", Pal.WHITE)
	# 지금 할 일
	var say := ""
	var say_color := Pal.WHITE
	match fishing.phase:
		"pull":
			say = "버틴다! 풀어라"
			say_color = WARN
		"warn":
			say = "곧 버틴다…"
			say_color = Pal.CREAM
		"tired":
			say = "지쳤다! 감아라"
			say_color = Pal.MINT
		"spent":
			say = "힘이 빠졌다! 끝까지 감아라"
			say_color = Pal.MINT
	var jolt := Vector2(0, -2) if fx.on("warn") and g.tick % 4 < 2 else Vector2.ZERO
	Ui.label(self, Vector2(598 - Ui.width(say, "bold"), 82) + jolt, say, say_color)
	if t < Data.TUG["slack_at"]:
		Ui.label(self, Vector2(598 - Ui.width("줄이 느슨하다!", "bold"), 98), "줄이 느슨하다!", COLD.lightened(0.4))
	# 물고기의 남은 힘
	var sp: Dictionary = fishing.engaged["sp"]
	var name: String = sp["name"]
	var sy := 58.0 if g.guide.text() != "" else 34.0
	Ui.label(self, Vector2(520 - Ui.width(name, "bold"), sy), name, Pal.WHITE)
	Ui.gauge(self, Rect2(526, sy + 1, 106, 12), fishing.stamina, WARN)


# ---- 조작 안내 ----

## 지금 하는 일이 있는 키만 [키, 설명] 으로 돌려준다.
func hints(g: Game) -> Array:
	if g.transitioning():
		return []
	var list: Array = []
	var other_bait := false
	for id in g.inv.baits:
		other_bait = other_bait or (id != g.inv.bait and g.inv.baits[id] > 0)
	match g.menu.kind:
		"title":
			return [["ud", "고르기"], ["action", "선택"]]
		"pause":
			return [["ud", "고르기"], ["action", "선택"], ["cancel", "닫기"]]
		"hold":
			list = [["cancel", "닫기"]]
			if not g.inv.hold.is_empty():
				list = [["ud", "고르기"], ["action", "놓아주기"], ["cancel", "닫기"]]
			return list
		"codex":
			return [["arrows", "넘기기"], ["cancel", "닫기"]]
		"help", "notice":
			return [["action", "닫기"]]
	if g.mode == "cut":
		return [["cancel", "건너뛰기"]]
	if g.mode == "shop":
		if g.shop.talking():
			return [["action", "다음"], ["cancel", "건너뛰기"]]
		var verb: String = {"bait": "만들기", "market": "팔기", "yard": "맡기기", "tackle": "사기"}[g.shop.id]
		return [["lr", "고르기"], ["action", verb], ["cancel", "나가기"]]
	if g.mode == "land":
		list = [["lr", "걷기"]]
		if g.walk.near != null:
			var kind: String = g.walk.near["kind"]
			if kind == "door":
				list.append(["action", "%s 들어가기" % Data.SHOPS[g.walk.near["id"]]["title"]])
			elif kind == "gather":
				list.append(["action", "줍기"])
			else:
				list.append(["action", "배 타기"])
		if other_bait:
			list.append(["bait", "미끼 바꾸기"])
		list.append(["codex", "도감"])
		list.append(["pause", "메뉴"])
		return list
	if g.mode == "sail":
		var act := "닻 내리기"
		if g.sailing.at_pier():
			act = "항구에 대기"
		elif g.sailing.at_island():
			act = "섬에 대기"
		list = [["lr", "배 몰기"], ["action", act]]
		if other_bait:
			list.append(["bait", "미끼"])
		list.append_array([["hold", "어창"], ["codex", "도감"], ["pause", "메뉴"]])
		return list
	if g.fishing.fighting:
		list = [["action", "누르는 동안 감기"]]
		if g.fishing.engaged["sp"]["run"]:
			list.append(["lr", "따라가기"])
		list.append(["cancel", "줄 끊기"])
		return list
	list = [["ud", "줄 내리기·올리기"], ["action", "미끼 흔들기"]]
	if other_bait:
		list.append(["bait", "미끼"])
	list.append_array([["cancel", "닻 올리기"], ["hold", "어창"], ["codex", "도감"]])
	return list


func _hints(g: Game) -> void:
	var list := hints(g)
	if list.is_empty():
		return
	var total := 0.0
	for pair in list:
		total += Ui.key_width(pair[0], pair[1])
	draw_rect(Rect2(0, 339, 640, 21), Color(Pal.INK, 0.55))
	var x := roundf(maxf(6.0, 320.0 - total * 0.5))
	for pair in list:
		var lit: bool = fx.on("anchored") and pair[0] == "cancel" and g.tick % 8 < 4
		x += Ui.key(self, Vector2(x, 341), pair[0], pair[1], Pal.CREAM if lit else Pal.WHITE)
