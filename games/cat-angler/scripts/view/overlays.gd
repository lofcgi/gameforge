class_name Overlays
extends Node2D
## 화면을 덮는 것들을 그린다: 타이틀 메뉴, 일시정지, 조작 안내, 알림, 어창, 도감(책), 디버그의 빠진 에셋 목록.
## 상태는 코어의 Menu 가 가진다.

const HELP_ROWS := [
	["← →  (A D)", "걷기 · 배 몰기 · 고르기 · 줄다리기 중 물고기 따라가기"],
	["↑ ↓  (W S)", "줄 올리기·내리기 · 고르기 · ↑ 문 들어가기"],
	["Space  (Z)", "줍기 · 들어가기 · 배 타기 · 닻 내리기 · 미끼 흔들기 · 감기"],
	["X  (Esc)", "닫기 · 나가기 · 닻 올리기 · 줄 끊기 · 메뉴"],
	["Q", "미끼 바꾸기"],
	["H", "어창 보기(놓아주기)"],
	["C  (Tab)", "도감"],
	["P  (Enter)", "잠깐 멈춤 · 저장"],
	["F3", "빠진 그림·소리 목록"],
]

var game: Game
var fx: Fx


func setup(g: Game, effects: Fx) -> void:
	game = g
	fx = effects


func advance() -> void:
	queue_redraw()


func _draw() -> void:
	var g := game
	match g.menu.kind:
		"title":
			_title(g)
		"pause":
			_dim()
			_list(g, Rect2(210, 84, 220, 176), "잠깐 멈춤")
		"help":
			_dim()
			_help()
		"notice":
			_dim()
			_notice(g)
		"hold":
			_dim()
			_hold(g)
		"codex":
			_codex(g)
	if g.debug:
		_debug()


func _dim() -> void:
	draw_rect(Rect2(Vector2.ZERO, Ui.SCREEN), Color(Pal.INK, 0.55))


func _open_scale(g: Game) -> float:
	return Ui.pop((g.tick - g.menu.opened) / 10.0)


func _row(g: Game, rect: Rect2, item: Dictionary, focused: bool) -> void:
	var nudge := 2.0 if focused and fx.on("deny") and g.tick % 4 < 2 else 0.0
	Ui.box(self, "button_focus" if focused else "button", Rect2(rect.position + Vector2(nudge, 0), rect.size), 8,
		Color.WHITE if item["ok"] else Color(1, 1, 1, 0.55))
	var color := Pal.BARK if item["ok"] else Pal.SAGE
	Ui.text(self, rect.position + Vector2(10 + nudge, (rect.size.y - Ui.fs()) * 0.5 - 1), item["text"], color)
	if item["right"] != "":
		Ui.text_right(self, rect.end.x - 10, rect.position.y + (rect.size.y - Ui.fs()) * 0.5 - 1, item["right"], Pal.WOOD if item["ok"] else Pal.SAGE)


func _title(g: Game) -> void:
	for i in g.menu.items.size():
		_row(g, Rect2(240, 222 + i * 28, 160, 22), g.menu.items[i], i == g.menu.cursor)


func _list(g: Game, rect: Rect2, title: String) -> void:
	var scale := _open_scale(g)
	draw_set_transform(rect.get_center(), 0.0, Vector2(1.0, scale))
	var local := Rect2(-rect.size * 0.5, rect.size)
	Ui.box(self, "panel", local)
	Ui.text_center(self, 0, local.position.y + 10, title, Pal.BARK)
	for i in g.menu.items.size():
		_row(g, Rect2(local.position.x + 16, local.position.y + 32 + i * 26, local.size.x - 32, 22), g.menu.items[i], i == g.menu.cursor)
	draw_set_transform(Vector2.ZERO)


func _help() -> void:
	var rect := Rect2(90, 50, 460, 250)
	Ui.box(self, "panel", rect)
	Ui.text_center(self, 320, rect.position.y + 10, "조작 (키보드 · 마우스 왼쪽 버튼은 Space 와 같다)", Pal.BARK)
	var y := rect.position.y + 36
	for row in HELP_ROWS:
		Ui.box(self, "button", Rect2(rect.position.x + 14, y - 2, 96, 20), 8)
		Ui.text(self, Vector2(rect.position.x + 22, y + 1), row[0], Pal.BARK)
		Ui.text(self, Vector2(rect.position.x + 120, y + 1), row[1], Pal.BARK)
		y += 23


func _notice(g: Game) -> void:
	var rect := Rect2(110, 120, 420, 100)
	draw_set_transform(rect.get_center(), 0.0, Vector2(1.0, _open_scale(g)))
	Ui.box(self, "panel", Rect2(-rect.size * 0.5, rect.size))
	Ui.paragraph(self, Rect2(-rect.size.x * 0.5 + 20, -rect.size.y * 0.5 + 22, rect.size.x - 40, 60), g.menu.text)
	draw_set_transform(Vector2.ZERO)


## 물고기 그림을 칸 안에 맞춰 놓는다(크면 정수로 나눠 줄인다).
func fish_icon(id: String, area: Rect2, tint := Color.WHITE) -> void:
	var texture := Assets.frame("fish/%s_swim" % id, 0)
	var size := texture.get_size()
	var shrink := maxf(1.0, ceilf(maxf(size.x / area.size.x, size.y / area.size.y)))
	var shown := size / shrink
	draw_texture_rect(texture, Rect2((area.get_center() - shown * 0.5).round(), shown), false, tint)


func _hold(g: Game) -> void:
	var rect := Rect2(100, 50, 440, 262)
	Ui.box(self, "panel", rect)
	Ui.text(self, rect.position + Vector2(16, 10), "어창  %d/%d칸" % [g.inv.hold_used(), g.inv.hold_cap()], Pal.BARK)
	if g.menu.say != "":
		Ui.paragraph(self, Rect2(rect.position.x + 16, rect.end.y - 40, rect.size.x - 32, 32), g.menu.say, Pal.TEAL_D)
	# 왼쪽: 칸. 물고기는 크기만큼 칸을 차지한다.
	var cols := 4
	var cell := 30.0
	var grid := rect.position + Vector2(18, 36)
	for i in g.inv.hold_cap():
		Ui.box(self, "slot", Rect2(grid + Vector2(i % cols, i / cols) * cell, Vector2(28, 28)), 6)
	var at := 0
	for index in g.inv.hold.size():
		var sp := Data.fish(g.inv.hold[index])
		for k in sp["slots"]:
			var cell_at: int = at + k
			var pos := grid + Vector2(cell_at % cols, cell_at / cols) * cell
			if index == g.menu.cursor:
				Ui.box(self, "slot_focus", Rect2(pos, Vector2(28, 28)), 6)
			fish_icon(sp["id"], Rect2(pos + Vector2(2, 2), Vector2(24, 24)), Color.WHITE if k == 0 else Color(1, 1, 1, 0.35))
		at += sp["slots"]
	# 오른쪽: 목록
	var first := clampi(g.menu.cursor - 4, 0, maxi(0, g.menu.items.size() - 8))
	for row in mini(8, g.menu.items.size()):
		var i := first + row
		_row(g, Rect2(rect.position.x + 150, rect.position.y + 34 + row * 24, 274, 22), g.menu.items[i], i == g.menu.cursor)


func _codex(g: Game) -> void:
	draw_texture(Assets.tex("ui/codex_book.png"), Vector2.ZERO)
	var left := Layout.area("ui/codex_book", "left")
	var right := Layout.area("ui/codex_book", "right")
	var caught: int = g.inv.caught.size()
	Ui.text(self, left.position + Vector2(68, 2), "물고기 도감", Pal.BARK, "bold")
	Ui.text_right(self, left.end.x - 4, left.position.y + 2, "%d / %d" % [caught, Data.FISH.size()], Pal.WOOD)
	var cols := Menu.CODEX_COLS
	var cell := Vector2(floorf(left.size.x / cols), 50.0)
	for i in Data.FISH.size():
		var sp: Dictionary = Data.FISH[i]
		var known: bool = g.inv.caught.has(sp["id"])
		var area := Rect2(left.position + Vector2(i % cols, i / cols) * cell + Vector2(2, 24), cell - Vector2(6, 6))
		Ui.box(self, "slot_focus" if i == g.menu.cursor else "slot", area, 6)
		fish_icon(sp["id"], area.grow(-5.0), Color.WHITE if known else Color(0.1, 0.09, 0.14, 0.85))
	var sp: Dictionary = Data.FISH[g.menu.cursor]
	var known: bool = g.inv.caught.has(sp["id"])
	var x := right.position.x + 8
	var y := right.position.y + 28
	var card := Assets.tex("fish/%s_card.png" % sp["id"])
	Ui.box(self, "slot", Rect2(x - 4, y - 2, 104, 72), 6)
	draw_texture(card, Vector2(x, y + 2), Color.WHITE if known else Color(0.1, 0.09, 0.14, 1.0))
	Ui.text(self, Vector2(x + 112, y + 4), sp["name"] if known else "???", Pal.BARK)
	Ui.text(self, Vector2(x + 112, y + 24), "낚은 수  %d" % g.inv.caught.get(sp["id"], 0) if known else "아직 못 낚았다", Pal.WOOD)
	if known:
		Ui.text(self, Vector2(x + 112, y + 44), "용궁에 바친다" if sp["id"] == "legend" else "%d닢 · %d칸" % [sp["price"], sp["slots"]], Pal.WOOD)
	y += 84
	var place: String = Data.zone(sp["zone"])["name"]
	if sp["place"] != "":
		place += " · " + Data.PLACES[sp["place"]]["name"]
	var baits := []
	for id in sp["baits"]:
		baits.append(Data.BAITS[id]["name"])
	for row in [["사는 곳", place], ["깊이", "%d ~ %dm" % [sp["dmin"], sp["dmax"]]], ["미끼", " · ".join(baits)]]:
		Ui.box(self, "button", Rect2(x - 4, y - 2, 56, 18), 8)
		Ui.text(self, Vector2(x + 2, y), row[0], Pal.BARK)
		Ui.text(self, Vector2(x + 62, y), row[1], Pal.BARK)
		y += 24
	y += 6
	Ui.paragraph(self, Rect2(x - 2, y, right.size.x - 16, 80),
		Data.FISH_NOTES[sp["id"]] if known else "실루엣만 알려져 있다. 위의 단서대로 찾아가 보자.", Pal.BARK if known else Pal.SLATE)


func _debug() -> void:
	var names := Assets.missing_list()
	var rows := 20
	var cols := 3
	draw_rect(Rect2(0, 28, 640, 16 + mini(rows, names.size()) * 12 + 14), Color(Pal.INK, 0.8))
	Ui.text(self, Vector2(6, 30), "아직 없는 에셋 %d개 (임시 그림·무음으로 대신한다)  F3: 닫기" % names.size(), Pal.CREAM)
	for i in mini(names.size(), rows * cols):
		Ui.text(self, Vector2(6 + (i / rows) * 212, 46 + (i % rows) * 12), names[i], Pal.WHITE, "small")
	if names.size() > rows * cols:
		Ui.text(self, Vector2(6, 46 + rows * 12), "… 그 밖에 %d개 (브리지 state.missing_assets 에 전부 있다)" % (names.size() - rows * cols), Pal.CREAM)
