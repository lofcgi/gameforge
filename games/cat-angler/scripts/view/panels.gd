class_name Panels
## 패널(가게·작업대·어창·도감)과 이야기 카드 그리기.

const DARK := Color("#17121B")
const WHITE := Color("#E9F3E2")
const GOLD := Color("#E9D36B")
const BOX := Rect2(30, 22, 260, 136)
const ROWS := 6


static func cards(hud: Hud, g: Game) -> void:
	hud.draw_rect(Rect2(0, 0, 320, 180), Color("#1B2139"))
	for i in 9:
		var px := fposmod(i * 41.0 + g.tick * 0.15, 340.0) - 10.0
		var py := 150.0 + sin(g.tick * 0.03 + i) * 4.0 - (i % 3) * 6.0
		hud.draw_rect(Rect2(px, py, 14, 2), Color("#2E3068"))
	var lines: PackedStringArray = g.menu.cards[g.menu.card].split("\n")
	var y := 78.0 - lines.size() * 8.0
	for line in lines:
		hud.text_center(160, y, line, WHITE, 12)
		y += 17.0
	hud.text(Vector2(8, 172), "%d/%d" % [g.menu.card + 1, g.menu.cards.size()], Color(WHITE, 0.6))
	hud.text(Vector2(312 - hud.width("Space 다음   X 건너뛰기"), 172), "Space 다음   X 건너뛰기", Color(WHITE, 0.7))


static func panel(hud: Hud, g: Game, fx: Fx) -> void:
	var menu := g.menu
	var nudge := Vector2(2 if fx.on("deny") and g.tick % 4 < 2 else 0, 0)
	var box := Rect2(BOX.position + nudge, BOX.size)
	hud.draw_rect(Rect2(0, 0, 320, 180), Color(DARK, 0.45))
	hud.draw_rect(box, Color("#1B2139"))
	hud.draw_rect(Rect2(box.position, Vector2(box.size.x, 15)), Color("#2E3068"))
	var title: String = Menu.TITLES[menu.panel]
	if menu.panel == "codex":
		title += " %d/%d" % [g.inv.caught.size(), Data.FISH.size()]
	elif menu.panel == "hold":
		title += " %d/%d칸" % [g.inv.hold_used(), g.inv.hold_cap()]
	hud.text(box.position + Vector2(6, 11), title, GOLD)
	var coins := "%d닢" % g.inv.coins
	hud.text(box.position + Vector2(box.size.x - 6 - hud.width(coins), 11), coins, GOLD if fx.on("coins") else WHITE)
	var list_w := 96.0 if menu.panel == "codex" else box.size.x
	var first := clampi(menu.cursor - ROWS / 2, 0, maxi(0, menu.items.size() - ROWS))
	for row in mini(ROWS, menu.items.size()):
		var index := first + row
		var item: Dictionary = menu.items[index]
		var y := box.position.y + 30 + row * 14
		var color := WHITE if item["ok"] or menu.panel == "codex" else Color(WHITE, 0.4)
		if index == menu.cursor:
			hud.draw_rect(Rect2(box.position.x + 3, y - 10, list_w - 6, 13), Color(WHITE, 0.16))
			hud.text(Vector2(box.position.x + 6 + (1 if fx.on("cursor") else 0), y), ">", GOLD)
		hud.text(Vector2(box.position.x + 16, y), item["text"], color)
		if item["right"] != "":
			hud.text(Vector2(box.position.x + box.size.x - 8 - hud.width(item["right"]), y), item["right"], color)
	if menu.items.size() > ROWS:
		hud.text(Vector2(box.position.x + list_w - 14, box.position.y + 30 + ROWS * 14 - 4), "↑↓", Color(WHITE, 0.6))
	if menu.panel == "codex":
		_codex_entry(hud, g, Data.fish(menu.items[menu.cursor]["arg"]), box)
	var foot := "Space 선택   X 닫기"
	if menu.panel == "codex":
		foot = "↑↓ 넘기기   X 닫기"
	elif menu.panel == "bench":
		hud.text(Vector2(box.position.x + 8, box.end.y - 30), "재료  " + _mats(g), Color(WHITE, 0.8))
	if menu.say != "":
		hud.text(Vector2(box.position.x + 8, box.end.y - 17), menu.say, Color("#BAEADC"))
	hud.text(Vector2(box.end.x - 6 - hud.width(foot), box.end.y - 4), foot, Color(WHITE, 0.6))


static func _mats(g: Game) -> String:
	var parts := []
	for id in Data.MATS:
		parts.append("%s %d" % [Data.MATS[id]["name"], g.inv.mats[id]])
	return "  ".join(parts)


## 도감 한 장: 낚은 어종은 색과 값, 못 낚은 어종은 실루엣과 구간·깊이·미끼 힌트.
static func _codex_entry(hud: Hud, g: Game, sp: Dictionary, box: Rect2) -> void:
	var known: bool = g.inv.caught.has(sp["id"])
	var x := box.position.x + 104
	var y := box.position.y + 20
	hud.draw_rect(Rect2(x, y, 148, 40), Color("#28706F", 0.5))
	Actors.fish_shape(hud, Vector2.ZERO, Vector2(x + 78, y + 20), sp, 1.0, sin(g.tick * 0.2) * 0.5, 1.0,
		Color.TRANSPARENT if known else DARK, 0.0, 2.0)
	var where: String = Data.zone(sp["zone"])["name"]
	if sp["place"] != "":
		where += " · " + Data.PLACES[sp["place"]]["name"]
	var baits := []
	for id in sp["baits"]:
		baits.append(Data.BAITS[id]["name"])
	var lines := [
		sp["name"] if known else "???  (아직 못 낚았다)",
		"사는 곳  " + where,
		"깊이  %d~%dm" % [sp["dmin"], sp["dmax"]],
		"미끼  " + ", ".join(baits),
	]
	if known:
		lines.append("%d마리 · %d칸 · %s" % [g.inv.caught[sp["id"]], sp["slots"],
			"용궁에 바친다" if sp["id"] == "legend" else "%d닢" % sp["price"]])
	for i in lines.size():
		hud.text(Vector2(x, y + 52 + i * 12), lines[i], GOLD if i == 0 else WHITE)
