extends ShopScreen
## 낚시 가게: 벽에 걸린 낚싯대 세 자루. 좌우로 견주어 보면 닿는 깊이·힘·감는 속도가 지금 것과 나란히 보인다.

const STATS := [["닿는 깊이", "reach", 150.0, "m"], ["버티는 힘", "str", 12.0, ""], ["감는 속도", "reel", 132.0, ""]]


func on_anim(anim: Dictionary) -> void:
	if anim["kind"] != "buy_rod":
		return
	var at: Vector2 = Layout.points("places/in_tackle", "rods")[anim["arg"]]
	if anim["t"] == 1:
		fx.shake = 4.0
	if anim["t"] % 9 == 1 and anim["t"] < 40:
		fx.play("sea/sparkle", at + Vector2((anim["t"] * 31) % 40 - 20, (anim["t"] * 23) % 100 - 50))


func stage() -> void:
	var g := game
	var shop := g.shop
	var inv := g.inv
	var rods := Layout.points("places/in_tackle", "rods")
	for tier in Data.RODS.size():
		var at: Vector2 = rods[tier]
		var focused: bool = shop.cursor == tier
		var texture := Assets.tex("items/rod%d_wall.png" % (tier + 1))
		var bought: bool = not shop.anim.is_empty() and shop.anim["kind"] == "buy_rod" and shop.anim["arg"] == tier
		var lift := roundf(sin(g.tick * 0.12) * 2.0) if focused else 0.0
		if bought:
			lift = -sin(minf(1.0, shop.anim["t"] / 20.0) * PI) * 14.0
		slot(Rect2(at - Vector2(28, texture.get_height() * 0.5 + 6), Vector2(56, texture.get_height() + 12)), focused, tier <= inv.rod + 1)
		Ui.sprite(self, texture, at + Vector2(0, lift), Vector2(0.5, 0.5), false, Color.WHITE if tier <= inv.rod + 1 or focused else Color(1, 1, 1, 0.6))
		var state := "%d닢" % Data.RODS[tier]["price"]
		if tier == inv.rod:
			state = "쓰는 중"
		elif tier < inv.rod:
			state = "가진 것"
		tag(at.x, at.y + texture.get_height() * 0.5 + 10, state, focused, Pal.BARK if tier <= inv.rod or shop.items[tier]["ok"] else Pal.SAGE)
	# 견주기 판: 고른 낚싯대(막대)와 지금 쓰는 것(세로 금)
	var chosen: Dictionary = Data.RODS[shop.cursor]
	var mine: Dictionary = inv.rod_data()
	var panel := Rect2(24.0 if rods[1].x > 320.0 else 436.0, 34, 180, 104)
	Ui.box(self, "panel", panel)
	Ui.text(self, panel.position + Vector2(12, 8), chosen["name"], Pal.BARK)
	for i in STATS.size():
		var stat: Array = STATS[i]
		var y := panel.position.y + 30 + i * 23
		Ui.text(self, Vector2(panel.position.x + 12, y), stat[0], Pal.WOOD)
		var bar := Rect2(panel.position.x + 76, y + 1, 64, 12)
		var better: bool = chosen[stat[1]] > mine[stat[1]]
		Ui.gauge(self, bar, chosen[stat[1]] / stat[2], Hud.GOOD if better else Pal.MIST)
		var mark := bar.position.x + 2 + roundf((bar.size.x - 4) * mine[stat[1]] / stat[2])
		draw_rect(Rect2(mark - 1, bar.position.y - 2, 2, bar.size.y + 4), Pal.BARK)
		Ui.text(self, Vector2(bar.end.x + 4, y), "%d%s" % [int(chosen[stat[1]]), stat[3]], Pal.TEAL_D if better else Pal.BARK)
