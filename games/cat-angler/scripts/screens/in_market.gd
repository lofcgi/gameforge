extends ShopScreen
## 어시장: 어창의 물고기가 진열대에 놓인다. 하나씩 저울에 올려 팔거나 종을 쳐서 한꺼번에 판다. 판 값만큼 동전이 날아간다.

var _cells := {}              # 어종 -> 진열대 위의 자리(지난 프레임). 팔린 물고기가 어디서 출발하는지 알려고 둔다
var _flying: Array = []       # 저울로 가는 물고기 {id, from, t, delay}


func on_anim(anim: Dictionary) -> void:
	if anim["t"] != 1:
		return
	var scale := point("scale")
	if anim["kind"] == "sell":
		_flying.append({"id": anim["arg"], "from": _cells.get(anim["arg"], scale), "t": 0, "delay": 0})
		fx.coin_burst(scale - Vector2(0, 10), 1 + Data.fish(anim["arg"])["price"] / 12)
	elif anim["kind"] == "sell_all":
		var order := 0
		for id in anim["fish"]:
			_flying.append({"id": id, "from": _cells.get(id, scale), "t": 0, "delay": mini(order, 10) * 3})
			order += 1
		fx.coin_burst(scale - Vector2(0, 10), 12)


func advance() -> void:
	for f in _flying:
		if f["delay"] > 0:
			f["delay"] -= 1
		else:
			f["t"] += 1
	_flying = _flying.filter(func(f): return f["t"] < 20)
	super.advance()


func stage() -> void:
	var g := game
	var shop := g.shop
	var inv := g.inv
	var table := Layout.area("places/in_market", "table")
	var scale := point("scale")
	var stacks: Array = Shop.stacks(inv)
	var rows := 2 if table.size.y >= 80.0 else 1
	var cols := maxi(4, ceili(stacks.size() / float(rows)))
	var cell := Vector2(floorf(table.size.x / cols), floorf(table.size.y / rows))
	_cells = {}
	for i in stacks.size():
		var id: String = stacks[i]
		var sp := Data.fish(id)
		var rect := Rect2(table.position + Vector2(i % cols, i / cols) * cell + Vector2(2, 2), cell - Vector2(4, 4))
		var focused: bool = shop.cursor == i + 1
		slot(rect, focused, id != "legend")
		var texture := Assets.frame("fish/%s_swim" % id, g.tick if focused else 0)
		var size := texture.get_size()
		var shrink := maxf(1.0, ceilf(maxf(size.x / (rect.size.x - 6), size.y / (rect.size.y - 8))))
		draw_texture_rect(texture, Rect2((rect.get_center() - Vector2(0, 2) - size / shrink * 0.5).round(), size / shrink), false)
		Ui.label(self, Vector2(rect.end.x - 18, rect.end.y - 13), "×%d" % inv.hold.count(id), Pal.WHITE, Pal.INK, "small")
		if focused:
			tag(rect.get_center().x, rect.position.y - 16, "용궁에 바친다" if id == "legend" else "%s %d닢" % [sp["name"], sp["price"]], true)
		_cells[id] = rect.get_center()
	if stacks.is_empty():
		Ui.label_center(self, table.get_center().x, table.get_center().y - 8, "진열대가 비었다", Pal.WHITE)
	# 종: 모두 팔기
	var all_focus: bool = shop.cursor == 0
	var total := inv.hold_value()
	tag(scale.x, scale.y + 34, "모두 팔기  +%d닢" % total, all_focus, Pal.BARK if total > 0 else Pal.SAGE)
	if all_focus:
		draw_pointer(Vector2(scale.x, scale.y + 30))
	# 저울로 날아가는 물고기
	for f in _flying:
		if f["delay"] > 0:
			continue
		var k: float = f["t"] / 20.0
		var from: Vector2 = f["from"]
		var pos := from.lerp(scale, Ui.ease_out(k)) - Vector2(0, sin(k * PI) * 36.0)
		Ui.sprite(self, Assets.frame("fish/%s_swim" % f["id"], 0), pos, Vector2(0.5, 0.5))
