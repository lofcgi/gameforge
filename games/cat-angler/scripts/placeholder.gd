class_name Placeholder
## 그림 파일이 아직 없을 때 쓰는 임시 그림. 규격(design/asset-spec.md)의 크기와 기준점대로 도형을 찍는다.
## 진짜 그림이 들어오면 Assets 가 이 파일을 거치지 않는다. 여기를 다듬는 데 공을 들이지 않는다.

const ZONE_SKY := {"shallow": [Pal.MINT, Pal.WHITE], "open": [Pal.MINT_D, Pal.MINT], "deep": [Pal.MIST, Pal.MINT_D]}
const ZONE_WATER := {"shallow": [Pal.CYAN, Pal.AQUA, Pal.AQUA_D], "open": [Pal.BLUE, Pal.BLUE_D, Pal.INDIGO],
	"deep": [Pal.INDIGO, Pal.NIGHT, Pal.INK]}
const ZONE_BED := {"shallow": [Pal.CREAM, Pal.SAND], "open": [Pal.SAGE, Pal.SLATE], "deep": [Pal.MINT_D, Pal.MIST]}
const KEEPER_COLORS := {"bait": [Pal.SLATE, Pal.INK], "market": [Pal.WOOD, Pal.CREAM], "yard": [Pal.BARK, Pal.SAND],
	"tackle": [Pal.MINT_D, Pal.ORANGE]}
const CAT_FRAMES := {"idle": [4, 6.0], "walk": [6, 10.0], "pick": [3, 8.0], "sit_fish": [4, 5.0], "reel": [4, 10.0],
	"strain": [4, 8.0], "cheer": [4, 8.0], "sad": [2, 3.0]}


static func image(rel: String) -> Image:
	var name := rel.get_basename()
	var dir := name.get_slice("/", 0)
	var leaf := name.get_slice("/", 1)
	match dir:
		"boats":
			return _boat(int(leaf.right(1)))
		"portraits":
			return _portrait(leaf)
		"fish":
			return _fish_card(leaf.trim_suffix("_card"))
		"sea":
			return _sea(leaf)
		"places":
			return _place(leaf)
		"items":
			return _item(leaf)
		"ui":
			return _ui(leaf)
	var unknown := Px.blank(16, 16)
	Px.box(unknown, 0, 0, 16, 16, Pal.SLATE, Pal.INK)
	return unknown


static func frames(base: String) -> Dictionary:
	var dir := base.get_slice("/", 0)
	var leaf := base.get_slice("/", 1)
	var list: Array = []
	var fps := 6.0
	if dir == "chars" and leaf.begins_with("cat_"):
		var action := leaf.trim_prefix("cat_")
		var spec: Array = CAT_FRAMES.get(action, [2, 4.0])
		fps = spec[1]
		for i in spec[0]:
			list.append(_cat(action, i))
	elif dir == "chars" and leaf.begins_with("keeper_"):
		var parts := leaf.trim_prefix("keeper_").split("_")
		var count := 2 if parts[1] == "talk" else 4
		fps = 6.0 if parts[1] == "talk" else 4.0
		for i in count:
			list.append(_keeper(parts[0], i, parts[1] == "talk"))
	elif dir == "fish":
		var shadow := leaf.ends_with("_shadow_swim")
		var id := leaf.trim_suffix("_shadow_swim").trim_suffix("_swim")
		for i in 4:
			list.append(_fish(Data.fish(id), i, shadow))
	else:
		match leaf:
			"school_small", "school_mid", "school_big":
				for i in 4:
					list.append(_school(leaf, i))
			"bird":
				for i in 4:
					list.append(_bird(i))
				fps = 8.0
			"splash":
				for i in 6:
					list.append(_splash(i))
				fps = 14.0
			"bubble":
				for i in 4:
					var bubble := Px.blank(8, 8)
					Px.oval(bubble, 4, 4, 1.5 + i * 0.5, 1.5 + i * 0.5, Color(0, 0, 0, 0), Pal.WHITE)
					list.append(bubble)
			"sparkle":
				for i in 4:
					var spark := Px.blank(16, 16)
					var arm: int = [2, 5, 7, 4][i]
					Px.rect(spark, 8 - arm, 7, arm * 2, 2, Pal.WHITE)
					Px.rect(spark, 7, 8 - arm, 2, arm * 2, Pal.WHITE)
					list.append(spark)
				fps = 10.0
			"vortex":
				for i in 4:
					var swirl := Px.blank(96, 24)
					for ring in 3:
						var rx := 44.0 - ring * 14.0
						Px.oval(swirl, 48 + [0, 2, 0, -2][(i + ring) % 4], 14, rx, 8.0 - ring * 2.0, Color(0, 0, 0, 0), Pal.WHITE)
					list.append(swirl)
			_:
				list.append(image(base + ".png"))
	return {"frames": list, "fps": fps}


# ---- 캐릭터 ----

static func _cat(action: String, i: int) -> Image:
	var im := Px.blank(48, 56)
	var bob: int = [0, 1, 0, -1][i % 4] if action in ["idle", "sit_fish", "reel"] else 0
	var sit := action in ["sit_fish", "reel", "strain"]
	var crouch := 6 if action == "pick" and i == 1 else (0 if not sit else 4)
	var lean := 0
	if action == "strain":
		lean = -3 - (i % 2)
	if action == "cheer":
		bob = [-2, -6, -3, 0][i]
	var by := 40 + crouch + bob
	var hy := 23 + crouch + bob + (2 if action == "sad" else 0)
	# 꼬리
	var tail: int = [0, 2, 3, 1][i % 4]
	Px.line(im, Vector2(13 + lean, by + 6), Vector2(6 + lean, by - 2 - tail), Pal.ORANGE, 3)
	# 다리
	if action == "walk":
		var stride: int = [4, 2, 0, -4, -2, 0][i % 6]
		Px.rect(im, 18 + stride, 48, 5, 7, Pal.ORANGE)
		Px.rect(im, 26 - stride, 48, 5, 7, Pal.ORANGE)
	elif not sit:
		Px.rect(im, 18, 49 + bob, 5, 6 - bob, Pal.ORANGE)
		Px.rect(im, 26, 49 + bob, 5, 6 - bob, Pal.ORANGE)
	else:
		Px.rect(im, 22, 51, 12, 4, Pal.ORANGE)
	# 몸과 조끼
	Px.oval(im, 23 + lean, by, 9, 10, Pal.ORANGE)
	Px.rect(im, 16 + lean, by - 5, 14, 11, Pal.INDIGO)
	Px.rect(im, 21 + lean, by - 5, 4, 11, Pal.CREAM)
	# 팔
	var arm_y := by - 3
	if action == "cheer":
		Px.line(im, Vector2(29, arm_y), Vector2(35, arm_y - 10), Pal.ORANGE, 3)
		Px.line(im, Vector2(17, arm_y), Vector2(11, arm_y - 10), Pal.ORANGE, 3)
	elif sit:
		var pull: int = [0, 1, 2, 1][i % 4] if action == "reel" else 0
		Px.line(im, Vector2(27 + lean, arm_y), Vector2(33 + lean - pull, arm_y - 2 - pull), Pal.ORANGE, 3)
	elif action == "pick":
		Px.line(im, Vector2(28, arm_y), Vector2(34, arm_y + 6 + i), Pal.ORANGE, 3)
	# 머리, 귀, 모자
	var hx := 26 + lean
	var ear := 0 if action == "sad" else 3
	Px.poly(im, [Vector2(hx - 11, hy - 6), Vector2(hx - 5, hy - 9), Vector2(hx - 9, hy - 14 - ear)], Pal.ORANGE)
	Px.poly(im, [Vector2(hx + 5, hy - 9), Vector2(hx + 11, hy - 6), Vector2(hx + 9, hy - 14 - ear)], Pal.ORANGE)
	Px.oval(im, hx, hy, 13, 11, Pal.ORANGE)
	Px.oval(im, hx + 2, hy + 4, 8, 6, Pal.CREAM)
	Px.oval(im, hx, hy - 9, 16, 3, Pal.SAND)
	Px.rect(im, hx - 8, hy - 15, 16, 6, Pal.SAND)
	Px.rect(im, hx - 8, hy - 11, 16, 2, Pal.TEAL_D)
	# 얼굴
	var blink := action == "idle" and i == 3
	Px.rect(im, hx - 3, hy, 2, 1 if blink else 3, Pal.INK)
	Px.rect(im, hx + 6, hy, 2, 1 if blink else 3, Pal.INK)
	if action in ["cheer", "strain"]:
		Px.rect(im, hx + 1, hy + 5, 4, 3, Pal.BARK)
	elif action == "sad":
		Px.rect(im, hx + 1, hy + 7, 4, 1, Pal.BARK)
	else:
		Px.rect(im, hx + 2, hy + 5, 2, 1, Pal.BARK)
	Px.outline(im, Pal.INK)
	return im


static func _keeper(id: String, i: int, talk: bool) -> Image:
	var im := Px.blank(48, 56)
	var colors: Array = KEEPER_COLORS.get(id, [Pal.SLATE, Pal.CREAM])
	var bob: int = [0, 1, 0, -1][i % 4] if not talk else 0
	Px.oval(im, 24, 42 + bob, 11, 12, colors[0])
	Px.rect(im, 15, 38 + bob, 18, 12, Pal.CREAM)
	if id == "tackle":
		Px.rect(im, 21, 14 + bob, 6, 20, colors[0])
		Px.oval(im, 24, 12 + bob, 8, 7, colors[0])
		Px.poly(im, [Vector2(16, 10 + bob), Vector2(16, 15 + bob), Vector2(2, 14 + bob)], colors[1])
	else:
		Px.oval(im, 24, 20 + bob, 13, 11, colors[0])
		Px.oval(im, 14, 10 + bob, 4, 4, colors[0])
		Px.oval(im, 34, 10 + bob, 4, 4, colors[0])
		Px.oval(im, 22, 24 + bob, 8, 5, colors[1] if id != "bait" else Pal.CREAM)
		if id == "bait":
			Px.rect(im, 13, 17 + bob, 22, 5, colors[1])
		if id == "yard":
			Px.rect(im, 19, 27 + bob, 5, 4, Pal.WHITE)
	Px.rect(im, 17, 19 + bob, 2, 2, Pal.WHITE if id == "bait" else Pal.INK)
	Px.rect(im, 26, 19 + bob, 2, 2, Pal.WHITE if id == "bait" else Pal.INK)
	if talk and i == 1:
		Px.rect(im, 19, 26, 5, 3, Pal.BARK)
	Px.outline(im, Pal.INK)
	return im


static func _portrait(id: String) -> Image:
	var im := Px.blank(96, 96)
	Px.box(im, 0, 0, 96, 96, Pal.MINT, Pal.WOOD)
	var small: Image = _cat("idle", 0) if id == "cat" else _keeper(id.trim_prefix("keeper_"), 0, false)
	if id in ["turtle", "king"]:
		small = Px.blank(48, 56)
		Px.oval(small, 24, 30, 18, 16, Pal.TEAL if id == "turtle" else Pal.AQUA_D, Pal.INK)
		Px.rect(small, 16, 26, 3, 3, Pal.INK)
		Px.rect(small, 28, 26, 3, 3, Pal.INK)
	# 머리 쪽을 두 배로 키워 얹는다.
	var head := small.get_region(Rect2i(4, 0, 40, 40))
	head.resize(80, 80, Image.INTERPOLATE_NEAREST)
	im.blend_rect(head, Rect2i(0, 0, 80, 80), Vector2i(8, 14))
	return im


# ---- 배 ----

static func _boat(tier: int) -> Image:
	var data: Dictionary = Layout.DEFAULTS["boats/boat%d" % tier]
	var w: int = data["size"][0]
	var h: int = data["size"][1]
	var wl: int = data["waterline"]
	var im := Px.blank(w, h)
	var top := wl - 14 - tier * 2
	if tier >= 2:
		var mast := int(w * 0.36)
		Px.rect(im, mast, 2, 3, top - 2, Pal.BARK)
		Px.poly(im, [Vector2(mast - 2, 4), Vector2(mast - 2, top - 8), Vector2(mast - 46 - tier * 6, top - 8)], Pal.CREAM)
	if tier >= 3:
		Px.box(im, 20, top - 26, 56, 26, Pal.WOOD_L, Pal.BARK)
		Px.rect(im, 30, top - 18, 12, 10, Pal.MIST)
		Px.rect(im, 52, top - 18, 12, 10, Pal.MIST)
	Px.poly(im, [Vector2(1, top), Vector2(w - 1, top - 2), Vector2(w - 14 - tier * 3, h - 1), Vector2(14, h - 1)], Pal.WOOD)
	Px.rect(im, 2, top, w - 4, 3, Pal.WOOD_L)
	Px.rect(im, 10, top + 7, w - 26, 1, Pal.BARK)
	if tier >= 3:
		Px.rect(im, 12, wl - 4, w - 30, 2, Pal.TEAL_D)
	Px.outline(im, Pal.INK)
	return im


# ---- 물고기 ----

static func fish_size(sp: Dictionary) -> Vector2i:
	var size := Vector2i(24, 16)
	if sp["id"] == "legend":
		return Vector2i(160, 80)
	if sp["slots"] == 2:
		size = Vector2i(40, 24)
	elif sp["slots"] >= 3:
		size = Vector2i(72, 40)
	if sp["shape"] == "long":
		size = Vector2i(int(size.x * 1.4), maxi(10, int(size.y * 0.5)))
	elif sp["shape"] == "flat":
		size = Vector2i(size.x, maxi(10, int(size.y * 0.6)))
	return size


static func _fish(sp: Dictionary, i: int, shadow := false) -> Image:
	var size := fish_size(sp)
	var im := Px.blank(size.x, size.y)
	var body: Color = Pal.NIGHT if shadow else sp["color"]
	var cy := size.y * 0.5
	var tail := size.x * 0.22
	var wag: float = [-1.0, 0.0, 1.0, 0.0][i] * maxf(1.0, size.y * 0.1)
	Px.poly(im, [Vector2(tail + 2, cy), Vector2(1, cy - size.y * 0.4 + wag), Vector2(1, cy + size.y * 0.4 + wag)], body)
	Px.oval(im, tail + (size.x - tail) * 0.5, cy, (size.x - tail) * 0.5 - 1, size.y * 0.5 - 2, body)
	Px.poly(im, [Vector2(size.x * 0.45, 3), Vector2(size.x * 0.7, 3), Vector2(size.x * 0.55, 0)], body)
	if not shadow:
		Px.oval(im, tail + (size.x - tail) * 0.5, cy + size.y * 0.18, (size.x - tail) * 0.36, size.y * 0.16, body.lightened(0.3))
		var eye := maxi(2, size.y / 8)
		Px.rect(im, size.x - 3 - eye * 2, int(cy) - eye, eye + 1, eye + 1, Pal.WHITE)
		Px.rect(im, size.x - 2 - eye * 2, int(cy) - eye + 1, eye, eye, Pal.INK)
		if sp["zone"] == "deep":
			Px.rect(im, size.x - 6, 1, 2, 2, Pal.CYAN)
		Px.outline(im, Pal.INK)
	return im


static func _fish_card(id: String) -> Image:
	var im := Px.blank(96, 64)
	Px.box(im, 0, 0, 96, 64, Pal.MINT, Pal.WOOD)
	var fish := _fish(Data.fish(id), 1)
	var scale := 1
	while fish.get_width() * (scale + 1) <= 84 and fish.get_height() * (scale + 1) <= 54:
		scale += 1
	if fish.get_width() > 84:
		fish.resize(84, int(84.0 * fish.get_height() / fish.get_width()), Image.INTERPOLATE_NEAREST)
	else:
		fish.resize(fish.get_width() * scale, fish.get_height() * scale, Image.INTERPOLATE_NEAREST)
	im.blend_rect(fish, Rect2i(Vector2i.ZERO, fish.get_size()), Vector2i((96 - fish.get_width()) / 2, (64 - fish.get_height()) / 2))
	return im


# ---- 바다 ----

static func _sea(leaf: String) -> Image:
	var zone := leaf.get_slice("_", leaf.get_slice_count("_") - 1)
	if leaf.begins_with("sky_"):
		var sky := Px.blank(640, 200, ZONE_SKY[zone][0])
		Px.rect(sky, 0, 150, 640, 50, ZONE_SKY[zone][1])
		Px.dither(sky, 0, 142, 640, 8, ZONE_SKY[zone][1])
		for c in [[90, 50, 46], [300, 84, 60], [520, 40, 38]]:
			Px.oval(sky, c[0], c[1], c[2], 9, Pal.WHITE)
			Px.oval(sky, c[0] + 20, c[1] - 8, c[2] * 0.5, 8, Pal.WHITE)
		return sky
	if leaf.begins_with("far_"):
		var far := Px.blank(640, 96)
		var tone: Color = {"shallow": Pal.MINT_D, "open": Pal.MIST, "deep": Pal.SAGE}[zone]
		for m in [[0, 150, 60], [190, 120, 40], [330, 200, 76], [540, 160, 50]]:
			Px.poly(far, [Vector2(m[0], 96), Vector2(m[0] + m[1] * 0.5, 96 - m[2]), Vector2(m[0] + m[1], 96)], tone)
		return far
	if leaf.begins_with("mid_"):
		var mid := Px.blank(640, 64)
		var tone: Color = {"shallow": Pal.MOSS, "open": Pal.SAGE, "deep": Pal.SLATE}[zone]
		for m in [[110, 70, 22], [420, 110, 30]]:
			Px.oval(mid, m[0], 64, m[1], m[2], tone)
			Px.oval(mid, m[0] - 10, 64 - m[2] + 2, 10, 8, Pal.TEAL_D)
		return mid
	if leaf.begins_with("under_"):
		var colors: Array = ZONE_WATER[zone]
		var under := Px.blank(640, 360, colors[0])
		Px.rect(under, 0, 120, 640, 120, colors[1])
		Px.rect(under, 0, 240, 640, 120, colors[2])
		Px.dither(under, 0, 108, 640, 12, colors[1])
		Px.dither(under, 0, 228, 640, 12, colors[2])
		for sx in [80, 260, 470]:
			for row in 110:
				if row % 2 == 0:
					Px.dither(under, sx - row / 2, row, 26, 1, colors[0].lightened(0.25))
		return under
	if leaf.begins_with("bed_"):
		var bed := Px.blank(64, 64)
		for x in 64:
			var top: int = 4 + [0, 1, 2, 3, 3, 2, 1, 0][(x / 4) % 8]
			Px.rect(bed, x, top, 1, 64 - top, ZONE_BED[zone][0])
			Px.rect(bed, x, top, 1, 2, Pal.WHITE if zone != "open" else Pal.MINT_D)
		Px.rect(bed, 0, 26, 64, 38, ZONE_BED[zone][1])
		Px.dither(bed, 0, 20, 64, 6, ZONE_BED[zone][1])
		for p in [[10, 14], [34, 18], [52, 12]]:
			Px.rect(bed, p[0], p[1], 4, 2, ZONE_BED[zone][1])
		return bed
	match leaf:
		"surface_pattern":
			var pattern := Px.blank(64, 32)
			for c in [[16, 22], [48, 22], [0, 32], [32, 32], [64, 32]]:
				var rings := [[17, Pal.CREAM], [15, Pal.TEAL_D], [11, Pal.CREAM], [9, Pal.AQUA_D], [5, Pal.CREAM], [3, Pal.TEAL]]
				for ring in rings:
					Px.oval(pattern, c[0], c[1], ring[0], ring[0], ring[1])
			return pattern
		"wave_crest":
			var crest := Px.blank(64, 24)
			Px.oval(crest, 32, 24, 30, 16, Pal.WHITE)
			Px.oval(crest, 30, 26, 24, 12, Pal.AQUA_D)
			Px.oval(crest, 50, 8, 7, 6, Pal.WHITE)
			return crest
		"reef":
			var reef := Px.blank(240, 96)
			for r in [[40, 60, 44], [110, 80, 70], [190, 56, 50]]:
				Px.oval(reef, r[0], 96, r[1] * 0.6, r[2], Pal.SLATE)
				Px.oval(reef, r[0] - 6, 96 - r[2] + 8, 10, 6, Pal.SAGE)
			Px.rect(reef, 70, 66, 4, 30, Pal.ORANGE)
			Px.rect(reef, 150, 54, 4, 42, Pal.AQUA_D)
			Px.outline(reef, Pal.INK)
			return reef
		"wreck":
			var wreck := Px.blank(256, 128)
			Px.poly(wreck, [Vector2(10, 70), Vector2(240, 96), Vector2(210, 126), Vector2(40, 126)], Pal.BARK)
			Px.rect(wreck, 96, 10, 6, 76, Pal.BARK)
			Px.rect(wreck, 70, 30, 60, 4, Pal.BARK)
			for hole in [70, 130, 180]:
				Px.rect(wreck, hole, 100, 16, 12, Pal.INK)
			Px.outline(wreck, Pal.INK)
			return wreck
		"island_far":
			var isle := Px.blank(320, 160)
			Px.oval(isle, 170, 148, 150, 70, Pal.SAND)
			Px.oval(isle, 190, 110, 90, 44, Pal.MOSS)
			Px.rect(isle, 0, 144, 320, 16, Pal.SAND)
			Px.rect(isle, 196, 30, 6, 60, Pal.BARK)
			Px.oval(isle, 198, 30, 30, 12, Pal.TEAL_D)
			Px.rect(isle, 6, 126, 5, 22, Pal.BARK)
			Px.rect(isle, 0, 138, 44, 4, Pal.WOOD)
			Px.outline(isle, Pal.INK)
			return isle
		"ruin_1", "ruin_2", "ruin_3":
			var ruin := Px.blank(64, 96)
			var n := int(leaf.right(1))
			Px.rect(ruin, 10, 96 - 40 - n * 14, 14, 40 + n * 14, Pal.MIST)
			Px.rect(ruin, 40, 96 - 30 - n * 8, 14, 30 + n * 8, Pal.MIST)
			if n >= 2:
				Px.rect(ruin, 6, 96 - 46 - n * 14, 52, 8, Pal.MIST)
			Px.outline(ruin, Pal.BLUE_D)
			return ruin
		"pavilion":
			var pav := Px.blank(192, 160)
			Px.poly(pav, [Vector2(4, 62), Vector2(96, 14), Vector2(188, 62)], Pal.TEAL)
			Px.rect(pav, 10, 58, 172, 8, Pal.AQUA_D)
			for col in [34, 78, 114, 158]:
				Px.rect(pav, col - 5, 66, 10, 86, Pal.TEAL_D)
			Px.rect(pav, 18, 150, 156, 10, Pal.MINT_D)
			Px.outline(pav, Pal.INK)
			return pav
		"pier":
			var pier := Px.blank(320, 120)
			Px.rect(pier, 0, 76, 300, 10, Pal.WOOD_L)
			Px.rect(pier, 0, 86, 300, 3, Pal.BARK)
			for post in [20, 90, 160, 230, 290]:
				Px.rect(pier, post, 70, 8, 50, Pal.WOOD)
			Px.rect(pier, 0, 40, 60, 36, Pal.SAND)
			Px.poly(pier, [Vector2(-6, 42), Vector2(30, 18), Vector2(66, 42)], Pal.TEAL)
			Px.outline(pier, Pal.INK)
			return pier
		"crate":
			var crate := Px.blank(24, 24)
			Px.box(crate, 2, 4, 20, 18, Pal.WOOD_L, Pal.INK)
			Px.rect(crate, 3, 12, 18, 2, Pal.WOOD)
			Px.rect(crate, 11, 5, 2, 16, Pal.WOOD)
			return crate
		"bottle":
			var bottle := Px.blank(16, 24)
			Px.box(bottle, 4, 8, 9, 15, Pal.TEAL, Pal.INK)
			Px.box(bottle, 6, 2, 5, 7, Pal.TEAL, Pal.INK)
			Px.rect(bottle, 6, 12, 5, 6, Pal.CREAM)
			return bottle
		"hook":
			var hook := Px.blank(8, 12)
			Px.rect(hook, 4, 0, 1, 9, Pal.INK)
			Px.rect(hook, 1, 9, 4, 1, Pal.INK)
			Px.rect(hook, 1, 6, 1, 3, Pal.INK)
			return hook
	if leaf.begins_with("bait_"):
		var bait := Px.blank(8, 8)
		Px.oval(bait, 4, 4, 3.5, 3.5, Data.BAITS[leaf.trim_prefix("bait_")]["color"], Pal.INK)
		return bait
	return Px.blank(16, 16, Pal.SLATE)


static func _school(leaf: String, i: int) -> Image:
	var im := Px.blank(96, 32)
	var n: int = {"school_small": 7, "school_mid": 4, "school_big": 2}[leaf]
	for k in n:
		var x: int = 8 + k * (80 / n) + [0, 2, 4, 2][(i + k) % 4]
		var y := 12 + (k % 3) * 5
		var w := 96 / (n + 3)
		Px.rect(im, x, y, w, 2, Pal.WHITE)
		Px.rect(im, x + 2, y + 4, w - 3, 1, Pal.AQUA_D)
	if leaf == "school_big":
		Px.oval(im, 48, 24, 34, 6, Pal.BLUE_D)
	return im


static func _bird(i: int) -> Image:
	var im := Px.blank(24, 16)
	var flap: int = [-4, -1, 3, -1][i]
	Px.line(im, Vector2(2, 8 + flap), Vector2(12, 8), Pal.WHITE, 2)
	Px.line(im, Vector2(12, 8), Vector2(21, 8 + flap), Pal.WHITE, 2)
	Px.rect(im, 11, 7, 3, 3, Pal.CREAM)
	Px.outline(im, Pal.INK)
	return im


static func _splash(i: int) -> Image:
	var im := Px.blank(48, 32)
	var h: int = [8, 18, 26, 22, 14, 6][i]
	var spread := 6 + i * 3
	for side in [-1, 1]:
		Px.line(im, Vector2(24 + side * 3, 31), Vector2(24 + side * spread, 31 - h), Pal.WHITE, 2)
		Px.rect(im, 24 + side * (spread + 2), 28 - h, 2, 2, Pal.WHITE)
	Px.rect(im, 23, 31 - h * 2 / 3, 2, h * 2 / 3, Pal.WHITE)
	return im


# ---- 장소 ----

static func _place(leaf: String) -> Image:
	match leaf:
		"town":
			return _town()
		"town_fg":
			var fg := Px.blank(1600, 360)
			for x in [180, 480, 790, 1090, 1370]:
				Px.box(fg, x, 296, 18, 22, Pal.WOOD, Pal.INK)
				Px.rect(fg, x + 1, 302, 16, 2, Pal.BARK)
			for x in [60, 760, 1420]:
				Px.rect(fg, x, 262, 3, 56, Pal.BARK)
				Px.box(fg, x - 5, 252, 13, 14, Pal.SAND, Pal.INK)
			return fg
		"forage":
			var im := Px.blank(960, 360, Pal.MINT)
			Px.rect(im, 0, 200, 960, 160, Pal.WHITE)
			for i in 12:
				Px.oval(im, 40 + i * 84, 200 - (i % 3) * 14, 60, 66, Pal.TEAL_D if i % 2 == 0 else Pal.TEAL)
				Px.rect(im, 34 + i * 84, 240, 12, 64, Pal.BARK)
			Px.rect(im, 0, 300, 960, 60, Pal.MOSS)
			Px.rect(im, 0, 300, 960, 3, Pal.TEAL)
			Px.dither(im, 0, 330, 960, 30, Pal.SAGE)
			Px.rect(im, 900, 250, 6, 50, Pal.BARK)
			Px.box(im, 880, 236, 60, 18, Pal.SAND, Pal.BARK)
			return im
		"island":
			var im := Px.blank(640, 360, Pal.MINT_D)
			Px.rect(im, 0, 150, 640, 60, Pal.MINT)
			Px.rect(im, 0, 210, 640, 150, Pal.BLUE)
			Px.oval(im, 340, 330, 330, 110, Pal.SAND)
			Px.rect(im, 60, 270, 560, 90, Pal.SAND)
			Px.oval(im, 480, 250, 110, 44, Pal.MOSS)
			Px.rect(im, 520, 120, 10, 130, Pal.BARK)
			Px.oval(im, 524, 118, 60, 22, Pal.TEAL_D)
			Px.rect(im, 20, 262, 110, 8, Pal.WOOD_L)
			for post in [28, 70, 112]:
				Px.rect(im, post, 262, 6, 60, Pal.WOOD)
			return im
		"title":
			var im := Px.blank(640, 360, Pal.MINT)
			Px.rect(im, 0, 150, 640, 60, Pal.WHITE)
			Px.rect(im, 0, 226, 640, 134, Pal.AQUA)
			Px.rect(im, 0, 280, 640, 80, Pal.BLUE)
			Px.dither(im, 0, 272, 640, 8, Pal.BLUE)
			return im
	return _interior(leaf)


static func _town() -> Image:
	var layout: Dictionary = Layout.DEFAULTS["places/town"]
	var ground: int = layout["ground_y"]
	var im := Px.blank(1600, 360, Pal.MINT)
	Px.rect(im, 0, 190, 1600, 120, Pal.WHITE)
	for i in 8:
		Px.poly(im, [Vector2(i * 220 - 40, 250), Vector2(i * 220 + 90, 150 + (i % 3) * 20), Vector2(i * 220 + 240, 250)], Pal.MINT_D)
	Px.rect(im, 0, 240, 1440, 70, Pal.MOSS)
	var roofs := {"bait": Pal.TEAL, "market": Pal.BLUE, "yard": Pal.WOOD, "tackle": Pal.TEAL_D}
	for id in layout["doors"]:
		var x: int = layout["doors"][id]
		Px.box(im, x - 100, ground - 120, 200, 120, Pal.CREAM, Pal.INK)
		Px.poly(im, [Vector2(x - 116, ground - 118), Vector2(x, ground - 176), Vector2(x + 116, ground - 118)], roofs[id])
		Px.rect(im, x - 116, ground - 122, 232, 6, Pal.BARK)
		Px.box(im, x - 16, ground - 52, 32, 52, Pal.BARK, Pal.INK)
		Px.rect(im, x + 8, ground - 28, 3, 3, Pal.SAND)
		Px.box(im, x - 80, ground - 84, 36, 30, Pal.MIST, Pal.BARK)
		Px.box(im, x + 44, ground - 84, 36, 30, Pal.MIST, Pal.BARK)
		Px.box(im, x - 34, ground - 82, 68, 20, roofs[id], Pal.INK)
	# 바다와 부두
	Px.rect(im, 1440, 250, 160, 110, Pal.AQUA)
	Px.rect(im, 1440, 250, 160, 3, Pal.WHITE)
	Px.rect(im, 0, ground, 1440, 60, Pal.SAND)
	Px.rect(im, 0, ground, 1440, 3, Pal.WOOD_L)
	Px.dither(im, 0, ground + 30, 1440, 30, Pal.WOOD_L)
	Px.rect(im, 1400, ground, 200, 8, Pal.WOOD_L)
	Px.rect(im, 1400, ground + 8, 200, 3, Pal.BARK)
	for post in [1450, 1510, 1570]:
		Px.rect(im, post, ground + 8, 8, 52, Pal.WOOD)
	Px.rect(im, 1560, ground - 30, 6, 30, Pal.BARK)
	return im


static func _interior(leaf: String) -> Image:
	var im := Px.blank(640, 360, Pal.CREAM)
	var name := "places/" + leaf
	var tone: Color = {"in_bait": Pal.MOSS, "in_market": Pal.MIST, "in_yard": Pal.SAND, "in_tackle": Pal.MINT_D}.get(leaf, Pal.MINT)
	Px.rect(im, 0, 0, 640, 258, tone)
	for x in range(0, 640, 80):
		Px.rect(im, x, 0, 2, 258, tone.darkened(0.12))
	Px.rect(im, 0, 258, 640, 102, Pal.WOOD_L)
	Px.rect(im, 0, 258, 640, 4, Pal.BARK)
	Px.dither(im, 0, 300, 640, 60, Pal.WOOD)
	if not Layout.DEFAULTS.has(name):
		return im
	var data: Dictionary = Layout.DEFAULTS[name]
	var keeper: Array = data["keeper"]
	Px.box(im, keeper[0] - 70, keeper[1] - 26, 150, 40, Pal.WOOD, Pal.INK)
	Px.rect(im, keeper[0] - 70, keeper[1] - 26, 150, 5, Pal.WOOD_L)
	match leaf:
		"in_bait":
			var b: Array = data["bench"]
			Px.box(im, b[0] - 8, b[1], b[2] + 16, 10, Pal.WOOD_L, Pal.INK)
			Px.rect(im, b[0], b[1] + 10, 8, 62, Pal.WOOD)
			Px.rect(im, b[0] + b[2] - 8, b[1] + 10, 8, 62, Pal.WOOD)
			Px.rect(im, 40, 138, 210, 6, Pal.BARK)
			for p in data["baskets"]:
				Px.box(im, p[0] - 18, p[1] - 14, 36, 22, Pal.SAND, Pal.BARK)
			Px.box(im, data["out"][0] - 22, data["out"][1] - 4, 44, 12, Pal.SAND, Pal.BARK)
		"in_market":
			var t: Array = data["table"]
			Px.box(im, t[0] - 8, t[1] - 6, t[2] + 16, t[3] + 12, Pal.MIST, Pal.INK)
			Px.rect(im, t[0], t[1] + t[3] + 6, 10, 258 - t[1] - t[3] - 6, Pal.WOOD)
			Px.rect(im, t[0] + t[2] - 10, t[1] + t[3] + 6, 10, 258 - t[1] - t[3] - 6, Pal.WOOD)
			Px.box(im, data["scale"][0] - 20, data["scale"][1] + 10, 40, 8, Pal.SLATE, Pal.INK)
			Px.rect(im, data["scale"][0] - 2, data["scale"][1] + 18, 4, 40, Pal.SLATE)
		"in_yard":
			var d: Array = data["dock"]
			Px.rect(im, 0, d[1] + 10, 440, 248 - d[1], Pal.MIST)
			Px.rect(im, d[0] - 150, d[1] + 12, 300, 6, Pal.BARK)
			for post in [-130, -40, 50, 130]:
				Px.rect(im, d[0] + post, d[1] + 18, 8, 240 - d[1], Pal.WOOD)
			var pv: Array = data["preview"]
			Px.box(im, pv[0], pv[1], pv[2], pv[3], Pal.BLUE_D, Pal.INK)
		"in_tackle":
			Px.rect(im, 180, 54, 290, 6, Pal.BARK)
			for p in data["rods"]:
				Px.box(im, p[0] - 30, p[1] - 70, 60, 140, Pal.WHITE, Pal.BARK)
	return im


# ---- 물건과 UI ----

static func _item(leaf: String) -> Image:
	if leaf.ends_with("_wall"):
		var wall := Px.blank(24, 128)
		var tier := int(leaf.substr(3, 1))
		Px.rect(wall, 11, 2, 2 + tier / 2, 124, [Pal.SAND, Pal.BARK, Pal.TEAL_D][tier - 1])
		Px.rect(wall, 9, 96, 6 + tier / 2, 20, Pal.WOOD)
		Px.oval(wall, 16, 88, 4, 4, Pal.SLATE)
		Px.outline(wall, Pal.INK)
		return wall
	if leaf.begins_with("rod"):
		var rod := Px.blank(32, 32)
		var tier := int(leaf.right(1))
		Px.line(rod, Vector2(4, 28), Vector2(27, 3), [Pal.SAND, Pal.BARK, Pal.TEAL_D][tier - 1], 2)
		Px.line(rod, Vector2(4, 28), Vector2(9, 22), Pal.WOOD, 3)
		Px.outline(rod, Pal.INK)
		return rod
	if leaf.ends_with("_plant"):
		var id := leaf.trim_suffix("_plant")
		var plant := Px.blank(24, 24)
		Px.rect(plant, 11, 10, 2, 14, Pal.TEAL_D)
		Px.oval(plant, 7, 14, 5, 3, Pal.TEAL)
		Px.oval(plant, 17, 12, 5, 3, Pal.TEAL)
		Px.oval(plant, 12, 7, 5, 5, Data.MATS[id]["color"])
		Px.outline(plant, Pal.INK)
		return plant
	var icon := Px.blank(16, 16)
	if leaf == "coin":
		Px.oval(icon, 8, 8, 6, 6, Pal.SAND, Pal.BARK)
		Px.rect(icon, 7, 5, 2, 6, Pal.WOOD_L)
	elif leaf.begins_with("bait_"):
		Px.oval(icon, 8, 9, 6, 5, Data.BAITS[leaf.trim_prefix("bait_")]["color"], Pal.INK)
		Px.rect(icon, 6, 6, 3, 2, Pal.WHITE)
	elif Data.MATS.has(leaf):
		Px.oval(icon, 8, 8, 5, 6, Data.MATS[leaf]["color"], Pal.INK)
		Px.rect(icon, 8, 1, 1, 4, Pal.TEAL_D)
	else:
		Px.box(icon, 2, 2, 12, 12, Pal.SLATE, Pal.INK)
	return icon


static func _frame(w: int, h: int, fill: Color, edge: Color, shade: Color) -> Image:
	var im := Px.blank(w, h)
	Px.rect(im, 2, 0, w - 4, h, edge)
	Px.rect(im, 0, 2, w, h - 4, edge)
	Px.rect(im, 1, 1, w - 2, h - 2, edge)
	Px.rect(im, 2, 1, w - 4, h - 2, fill)
	Px.rect(im, 1, 2, w - 2, h - 4, fill)
	Px.rect(im, 2, h - 3, w - 4, 2, shade)
	return im


static func _ui(leaf: String) -> Image:
	match leaf:
		"panel":
			var panel := _frame(48, 48, Pal.CREAM, Pal.WOOD, Pal.SAND)
			Px.oval(panel, 6, 6, 3, 3, Color(0, 0, 0, 0), Pal.AQUA_D)
			return panel
		"bubble":
			return _frame(48, 48, Pal.WHITE, Pal.WOOD, Pal.CREAM)
		"button":
			return _frame(32, 24, Pal.SAND, Pal.WOOD, Pal.WOOD_L)
		"button_focus":
			return _frame(32, 24, Pal.WHITE, Pal.TEAL_D, Pal.MINT)
		"slot":
			return _frame(28, 28, Pal.MINT_D, Pal.WOOD, Pal.SAGE)
		"slot_focus":
			return _frame(28, 28, Pal.WHITE, Pal.TEAL_D, Pal.MINT)
		"gauge_frame":
			return _frame(64, 12, Pal.NIGHT, Pal.INK, Pal.NIGHT)
		"tension_frame":
			return _frame(24, 168, Pal.NIGHT, Pal.INK, Pal.NIGHT)
		"gauge_fill", "tension_fill":
			return Px.blank(4, 4, Pal.WHITE)
		"depth_ruler":
			var ruler := Px.blank(24, 32, Pal.CREAM)
			Px.rect(ruler, 0, 0, 1, 32, Pal.WOOD)
			Px.rect(ruler, 23, 0, 1, 32, Pal.WOOD)
			Px.rect(ruler, 14, 0, 9, 1, Pal.BARK)
			Px.rect(ruler, 18, 16, 5, 1, Pal.WOOD_L)
			return ruler
		"codex_book":
			var book := Px.blank(640, 360, Pal.NIGHT)
			Px.box(book, 20, 18, 600, 324, Pal.BARK, Pal.INK)
			Px.box(book, 32, 28, 284, 304, Pal.CREAM, Pal.WOOD)
			Px.box(book, 324, 28, 284, 304, Pal.CREAM, Pal.WOOD)
			Px.rect(book, 316, 28, 8, 304, Pal.WOOD)
			return book
		"logo":
			var logo := _frame(320, 96, Pal.CREAM, Pal.WOOD, Pal.SAND)
			Px.rect(logo, 12, 80, 296, 3, Pal.AQUA_D)
			return logo
		"arrow":
			var arrow := Px.blank(16, 16)
			Px.rect(arrow, 6, 1, 4, 7, Pal.CREAM)
			Px.poly(arrow, [Vector2(1, 8), Vector2(15, 8), Vector2(8, 15)], Pal.CREAM)
			Px.outline(arrow, Pal.BARK)
			return arrow
	var icon := Px.blank(16, 16)
	match leaf:
		"icon_coin":
			return _item("coin")
		"icon_durability":
			Px.poly(icon, [Vector2(1, 6), Vector2(15, 6), Vector2(12, 13), Vector2(4, 13)], Pal.WOOD)
			Px.rect(icon, 7, 1, 2, 5, Pal.BARK)
		"icon_hold":
			Px.box(icon, 2, 4, 12, 10, Pal.WOOD_L, Pal.INK)
			Px.rect(icon, 3, 8, 10, 1, Pal.BARK)
		"icon_anchor":
			Px.rect(icon, 7, 2, 2, 11, Pal.SLATE)
			Px.rect(icon, 4, 5, 8, 2, Pal.SLATE)
			Px.rect(icon, 3, 11, 10, 2, Pal.SLATE)
		"icon_bait":
			Px.oval(icon, 8, 9, 5, 5, Pal.MOSS)
		_:
			Px.box(icon, 2, 2, 12, 12, Pal.SLATE, Pal.INK)
	Px.outline(icon, Pal.INK)
	return icon
