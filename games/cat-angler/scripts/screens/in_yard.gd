extends ShopScreen
## 조선소: 선거에 올린 내 배. 벽의 판에는 다음 배의 설계도가 걸리고, 옆의 표에서 지금 배와 견준다. 수리와 개조.

const BLUEPRINT := Color(0.75, 0.95, 1.0, 0.9)
const SHEET := Rect2(16, 34, 282, 150)


func on_anim(anim: Dictionary) -> void:
	var dock := point("dock")
	if anim["kind"] == "repair" and anim["t"] % 8 == 1 and anim["t"] < 34:
		fx.burst(dock + Vector2((anim["t"] * 37) % 90 - 45, -10), 4, Pal.CREAM, 50.0, 40.0)
		fx.shake = 2.0
	if anim["kind"] == "upgrade":
		if anim["t"] == 1:
			fx.flash["hit"] = 24
			fx.shake = 6.0
		if anim["t"] % 10 == 2 and anim["t"] < 40:
			fx.play("sea/sparkle", dock + Vector2((anim["t"] * 53) % 160 - 80, -20 - (anim["t"] * 17) % 40))


func stage() -> void:
	var g := game
	var shop := g.shop
	var inv := g.inv
	var dock := point("dock")
	var board := Layout.area("places/in_yard", "preview")
	var upgrading: bool = not shop.anim.is_empty() and shop.anim["kind"] == "upgrade"
	var repairing: bool = not shop.anim.is_empty() and shop.anim["kind"] == "repair"
	var t: int = shop.anim["t"] if not shop.anim.is_empty() else 999

	# 선거의 내 배
	var boat := Layout.boat(inv.boat)
	var scale := Ui.pop(t / 16.0) if upgrading else 1.0
	draw_set_transform(dock, sin(g.tick * 0.9) * 0.012 if repairing and t < 34 else 0.0, Vector2(scale, scale))
	draw_texture(Assets.tex("boats/boat%d.png" % (inv.boat + 1)), -boat["pivot"])
	draw_set_transform(Vector2.ZERO)

	# 벽의 판: 다음 배의 설계도
	var next := inv.boat + 1
	var has_next := next < Data.BOATS.size()
	if has_next:
		var texture := Assets.tex("boats/boat%d.png" % (next + 1))
		var size := texture.get_size()
		var shrink := maxf(1.0, ceilf(maxf(size.x / (board.size.x - 8), size.y / (board.size.y - 8))))
		draw_texture_rect(texture, Rect2((board.get_center() - size / shrink * 0.5).round(), size / shrink), false, BLUEPRINT)

	# 견적서: 내 배의 상태, 다음 배와의 비교, 맡길 일 둘
	Ui.box(self, "panel", SHEET)
	var x := SHEET.position.x + 14
	var y := SHEET.position.y + 10
	var cap: float = inv.boat_data()["dur"]
	var shown: float = inv.durability
	if repairing:
		shown = lerpf(shop.anim["from"], cap, Ui.ease_out(t / 34.0))
	Ui.text(self, Vector2(x, y), "내 배  %s" % inv.boat_data()["name"], Pal.BARK, "bold")
	Ui.gauge(self, Rect2(x + 128, y + 1, 84, 12), shown / cap, Hud.GOOD if shown / cap > 0.4 else Hud.WARN)
	Ui.text(self, Vector2(x + 218, y), "%d/%d" % [int(shown), int(cap)], Pal.BARK)
	y += 22
	if has_next:
		var data: Dictionary = Data.BOATS[next]
		var now: Dictionary = inv.boat_data()
		var sea: String = Data.ZONES.filter(func(z): return z["grade"] == data["grade"])[0]["name"]
		Ui.text(self, Vector2(x, y), "다음 배  %s" % data["name"], Pal.TEAL_D, "bold")
		Ui.text(self, Vector2(x, y + 18), "%s의 파도를 버틴다" % sea, Pal.BARK)
		Ui.text(self, Vector2(x, y + 34), "내구도 %d → %d    어창 %d → %d칸" % [now["dur"], data["dur"], now["hold"], data["hold"]], Pal.BARK)
		Ui.text(self, Vector2(x, y + 50), "빠르기 %d → %d" % [now["speed"], data["speed"]], Pal.BARK)
	else:
		Ui.text(self, Vector2(x, y + 18), "가장 좋은 배다. 더 고칠 설계도가 없다.", Pal.BARK)
	var cost := inv.repair_cost()
	var labels := ["수리  %d닢" % cost if cost > 0 else "수리  (멀쩡하다)",
		"개조  %d닢" % Data.BOATS[next]["price"] if has_next else "개조  (최고 단계)"]
	for i in 2:
		var rect := Rect2(SHEET.position.x + 12 + i * 132, SHEET.end.y - 32, 126, 22)
		var focused: bool = shop.cursor == i
		var nudge := 2.0 if focused and fx.on("deny") and g.tick % 4 < 2 else 0.0
		Ui.box(self, "button_focus" if focused else "button", Rect2(rect.position + Vector2(nudge, 0), rect.size), 8,
			Color.WHITE if shop.items[i]["ok"] or focused else Color(1, 1, 1, 0.6))
		Ui.text_center(self, rect.get_center().x + nudge, rect.position.y + 4, labels[i], Pal.BARK if shop.items[i]["ok"] else Pal.SAGE)
