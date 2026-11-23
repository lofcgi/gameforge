extends ShopScreen
## 미끼 공방: 작업대. 바구니의 재료가 작업대로 날아가 빚어지고, 완성된 미끼가 옆에 놓인다.

const MAT_ORDER := ["herb", "bug", "berry", "flower"]


func on_anim(anim: Dictionary) -> void:
	if anim["kind"] != "craft":
		return
	var bench := Layout.area("places/in_bait", "bench")
	if anim["t"] == 16:
		fx.burst(bench.get_center() - Vector2(0, 8), 10, Data.BAITS[anim["arg"]]["color"], 60.0, 50.0)
		fx.shake = 3.0
	if anim["t"] == 30:
		fx.play("sea/sparkle", bench.get_center() + Vector2(0, -6))


func stage() -> void:
	var g := game
	var shop := g.shop
	var inv := g.inv
	var bench := Layout.area("places/in_bait", "bench")
	var baskets := Layout.points("places/in_bait", "baskets")
	var out := point("out")
	var selected: String = shop.items[shop.cursor]["arg"]
	var cost: Dictionary = Data.BAITS[selected]["cost"]
	var crafting: bool = not shop.anim.is_empty() and shop.anim["kind"] == "craft"
	var t: int = shop.anim["t"] if crafting else 999

	# 바구니: 가진 재료
	for i in MAT_ORDER.size():
		var mat: String = MAT_ORDER[i]
		var at: Vector2 = baskets[i]
		var needed: bool = cost.has(mat)
		slot(Rect2(at - Vector2(16, 18), Vector2(32, 32)), needed, inv.mats[mat] > 0)
		Ui.icon(self, "items/%s.png" % mat, at - Vector2(8, 10), Color.WHITE if inv.mats[mat] > 0 else Color(1, 1, 1, 0.35))
		Ui.label_center(self, at.x, at.y + 16, "%s %d" % [Data.MATS[mat]["name"], inv.mats[mat]], Pal.WHITE if inv.mats[mat] > 0 else Pal.MINT_D)

	# 만들 미끼 고르기
	var n := shop.items.size()
	var first_x := bench.get_center().x - (n * 62.0) * 0.5
	for i in n:
		var bait: String = shop.items[i]["arg"]
		var rect := Rect2(first_x + i * 62.0, 40, 58, 44)
		slot(rect, i == shop.cursor, shop.items[i]["ok"])
		Ui.icon(self, "items/bait_%s.png" % bait, rect.position + Vector2(21, 5), Color.WHITE if shop.items[i]["ok"] else Color(1, 1, 1, 0.5))
		Ui.text_center(self, rect.get_center().x, rect.position.y + 25, "×%d" % inv.baits[bait], Pal.BARK)
		if i == shop.cursor:
			tag(rect.get_center().x, rect.end.y + 2, Data.BAITS[bait]["name"], true)

	# 작업대: 고른 미끼에 드는 재료가 놓일 자리
	var mats := cost.keys()
	var spacing := minf(40.0, bench.size.x / (mats.size() + 1))
	var start := bench.get_center().x - spacing * (mats.size() - 1) * 0.5
	for i in mats.size():
		var mat: String = mats[i]
		var rest := Vector2(start + i * spacing, bench.position.y - 2)
		var have: bool = inv.mats[mat] >= cost[mat] or crafting
		var pos := rest
		if crafting and t < 16:
			pos = baskets[MAT_ORDER.find(mat)].lerp(rest, Ui.ease_out(t / 16.0)) - Vector2(0, sin(t / 16.0 * PI) * 30.0)
		elif crafting and t < 30:
			pos = rest.lerp(Vector2(bench.get_center().x, rest.y), (t - 16) / 14.0) + Vector2(0, -absf(sin(t * 0.9)) * 4.0)
		if not crafting or t < 30:
			Ui.sprite(self, Assets.tex("items/%s.png" % mat), pos, Vector2(0.5, 1.0), false, Color.WHITE if have else Color(1, 1, 1, 0.3))
	# 완성된 미끼
	var bait_tex := Assets.tex("items/bait_%s.png" % (shop.anim["arg"] if crafting else selected))
	if crafting and t >= 30:
		var k := (t - 30) / 18.0
		var from := Vector2(bench.get_center().x, bench.position.y - 2)
		var pos := from.lerp(out, Ui.ease_out(k)) - Vector2(0, sin(k * PI) * 26.0)
		Ui.sprite(self, bait_tex, pos)
	elif inv.baits[selected] > 0:
		Ui.sprite(self, bait_tex, out)
	Ui.label_center(self, out.x, out.y + 4, "%s ×%d" % [Data.BAITS[selected]["name"], inv.baits[selected]], Pal.WHITE)
