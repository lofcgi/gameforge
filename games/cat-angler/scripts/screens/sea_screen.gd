extends Screen
## 바다 화면: 항해와 낚시. 구간마다의 겹(하늘·먼 배경·중간 배경·물속·바닥)을 카메라 위치에 따라 서서히 바꿔 그리고,
## 실제 파도 위에 배와 고양이를 놓는다. 닻을 내리면 카메라가 미끼를 따라 내려간다.
## 그리기 명령을 아끼려고 수면 높이는 틱마다 한 번만 재서(_surf) 수면선, 물기둥, 문양, 배가 함께 쓴다.

const SURFACE_LINE := 198.0     # 항해 중 수면선의 화면 y (위에서 55%)
const COL := 8.0                # 물기둥 하나의 너비
const BED_COL := 16.0
const ROD_COLORS := [Pal.SAND, Pal.WOOD, Pal.TEAL_D]
const RUIN_SPOTS_M := [965.0, 1045.0, 1090.0, 1340.0, 1385.0, 1500.0, 1545.0, 1720.0, 1765.0]
const PAVILION_SPOTS_M := [1960.0, 2310.0]

var cam := Vector2.ZERO

var _origin := Vector2.ZERO
var _snapped := false
var _surf := PackedFloat32Array()
var _surf_from := 0.0
var _bottoms := {}            # 텍스처 경로 -> 맨 아랫줄의 색


func _ready() -> void:
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED


func setup(g: Game, effects: Fx) -> void:
	super.setup(g, effects)
	# 처음 나타나는 순간에 읽느라 멈칫하지 않게 바다의 그림을 미리 읽어 둔다.
	for sp in Data.FISH:
		Assets.anim("fish/%s_swim" % sp["id"])
	for base in ["fish/legend_shadow_swim", "sea/splash", "sea/bubble", "sea/sparkle", "sea/bird", "sea/vortex",
			"sea/school_small", "sea/school_mid", "sea/school_big", "chars/cat_sit_fish", "chars/cat_reel", "chars/cat_strain",
			"chars/cat_cheer", "chars/cat_sad"]:
		Assets.anim(base)
	for zone in ["shallow", "open", "deep"]:
		for layer in ["sky", "far", "mid", "under", "bed"]:
			Assets.tex("sea/%s_%s.png" % [layer, zone])
	_move_camera()
	_sample_surface()


func advance() -> void:
	_move_camera()
	_origin = (Ui.SCREEN * 0.5 - cam + fx.offset).round()
	_sample_surface()
	queue_redraw()


func focus() -> Vector2:
	return _origin + Vector2(game.sailing.x, game.sailing.y - 24.0)


# ---- 카메라와 수면 ----

func _move_camera() -> void:
	var g := game
	var s := g.sailing
	# 가는 쪽을 조금 앞서 보여 준다.
	var target := Vector2(s.x + clampf(s.vx * 0.45, -110.0, 110.0), 180.0 - SURFACE_LINE)
	if g.mode == "fish":
		var f := g.fishing
		target.x = f.hook_x(g) - 30.0 + (f.off * 0.5 if f.fighting else 0.0)
		# 닻을 내리면 바로 조금 잠기고, 그 뒤로는 미끼를 따라 내려간다.
		var deepest := maxf(target.y, Sea.bed_y(f.hook_x(g)) - 120.0)
		target.y = clampf(maxf(f.hook_y - 40.0, 46.0), target.y, deepest)
	target.x = clampf(target.x, Sailing.left_limit() + 120.0, Data.SEA_END_M * Data.X_PX - 320.0)
	if not _snapped:
		cam = target
		_snapped = true
		_origin = (Ui.SCREEN * 0.5 - cam).round()
	cam.x += (target.x - cam.x) * 0.08
	cam.y += (target.y - cam.y) * 0.07


func _sample_surface() -> void:
	_surf_from = floorf((cam.x - 336.0) / COL) * COL
	var count := int(672.0 / COL) + 3
	_surf.resize(count)
	var sailing := game.sailing
	var tick := game.tick
	for i in count:
		_surf[i] = sailing.surface_y(_surf_from + i * COL, tick)


## 세계 x 의 수면 높이(이번 틱의 표본에서 읽는다).
func surf(x: float) -> float:
	var at := clampf((x - _surf_from) / COL, 0.0, _surf.size() - 1.001)
	var index := int(at)
	return lerpf(_surf[index], _surf[index + 1], at - index)


## 카메라 자리의 구간 섞임: [앞 구간, 뒤 구간, 뒤 구간의 비율].
func _zone_mix() -> Array:
	var m := cam.x / Data.X_PX
	if m < 1350.0:
		return ["shallow", "open", smoothstep(850.0, 950.0, m)]
	return ["open", "deep", smoothstep(1750.0, 1850.0, m)]


func _bottom_color(rel: String) -> Color:
	if not _bottoms.has(rel):
		var image := Assets.tex(rel).get_image()
		_bottoms[rel] = image.get_pixel(0, image.get_height() - 1)
	return _bottoms[rel]


# ---- 그리기 ----

func _draw() -> void:
	var g := game
	var tick := g.tick
	var mix := _zone_mix()
	var left := cam.x - 328.0
	var right := cam.x + 328.0
	var horizon := _origin.y
	var deep_tone: Color = _bottom_color("sea/under_%s.png" % mix[0]).lerp(_bottom_color("sea/under_%s.png" % mix[1]), mix[2])
	draw_rect(Rect2(Vector2.ZERO, Ui.SCREEN), deep_tone)
	if horizon > -8.0:
		_backdrop("sky", mix, 0.03, horizon)
		_backdrop("far", mix, 0.12, horizon)
		_backdrop("mid", mix, 0.3, horizon)
		_above_water(left, right, tick)
	_boat(g)
	_surface_things(g, left, right, tick)
	_water(mix, left, right, deep_tone, tick)
	if horizon > -40.0:
		_submerged_hull(g)
	_bed(left, right)
	_fish(g, left, right, tick)
	if g.mode == "fish":
		_line(g)
	_fly(g)
	draw_effects(_origin)
	_pointer(g)


## 구간 겹 하나를 가로로 이어 깔고, 구간 경계에서는 다음 구간의 것을 겹쳐 서서히 바꾼다. 아래 가장자리가 수평선이다.
func _backdrop(layer: String, mix: Array, parallax: float, horizon: float) -> void:
	for i in 2:
		var alpha: float = 1.0 if i == 0 else mix[2]
		if alpha <= 0.0 or (i == 0 and mix[2] >= 1.0):
			continue
		var texture := Assets.tex("sea/%s_%s.png" % [layer, mix[i]])
		var size := texture.get_size()
		draw_texture_rect_region(texture, Rect2(0, horizon - size.y, 640, size.y),
			Rect2(roundf(cam.x * parallax), 0, 640, size.y), Color(1, 1, 1, alpha))


## 수면 위의 붙박이: 부두, 섬, 배 뒤의 물결 문양.
func _above_water(left: float, right: float, tick: int) -> void:
	var pier := Assets.tex("sea/pier.png")
	var pier_right := Sailing.left_limit() - 56.0
	if pier_right > left:
		draw_texture(pier, _origin + Vector2(pier_right - pier.get_width(), 24.0 - pier.get_height()))
	var isle := Assets.tex("sea/island_far.png")
	var isle_x := Sea.place_x("island")
	if absf(isle_x - cam.x) < 320.0 + isle.get_width():
		draw_texture(isle, _origin + Vector2(roundf(isle_x - isle.get_width() * 0.5), 16.0 - isle.get_height()))
	# 전통 물결 문양: 수면선에 걸쳐 천천히 흐른다.
	var pattern := Assets.tex("sea/surface_pattern.png")
	var pw := pattern.get_width()
	var px := floorf((left - tick * 0.12) / pw) * pw + fposmod(tick * 0.12, pw) - pw
	while px < right:
		var lift := roundf(surf(px + pw * 0.5) * 0.6) + 6.0
		draw_texture(pattern, _origin + Vector2(roundf(px), lift - pattern.get_height()))
		px += pw


func _cat_action(g: Game) -> String:
	if fx.mood != "":
		return fx.mood
	if g.mode != "fish":
		return "idle"
	if g.fishing.fighting:
		if g.fishing.phase == "pull" or g.fishing.tension > 0.8:
			return "strain"
		return "reel" if g.fishing.reeling else "sit_fish"
	return "sit_fish"


func _boat_transform(g: Game) -> void:
	draw_set_transform(_origin + Vector2(g.sailing.x, g.sailing.y).round(), g.sailing.tilt, Vector2(fx.facing, 1))


## 배의 그림 좌표(기준점에서 본 자리)를 세계 좌표로 옮긴다.
func _boat_point(g: Game, local: Vector2) -> Vector2:
	return Vector2(g.sailing.x, g.sailing.y).round() + Vector2(local.x * fx.facing, local.y).rotated(g.sailing.tilt)


func _rod_tip_local(g: Game) -> Vector2:
	var boat := Layout.boat(g.inv.boat)
	var action := _cat_action(g)
	var drawn = Layout.cat_rod_tip(action, Assets.frame_index("chars/cat_" + action, g.tick))
	if drawn != null:
		return boat["seat"] + drawn
	var tip: Vector2 = boat["rod_tip"]
	if g.fishing.fighting:
		tip += Vector2(3.0, 12.0) * g.fishing.tension
	return tip


func _boat(g: Game) -> void:
	var boat := Layout.boat(g.inv.boat)
	_boat_transform(g)
	draw_texture(Assets.tex("boats/boat%d.png" % (g.inv.boat + 1)), -boat["pivot"])
	var seat: Vector2 = boat["seat"]
	var action := _cat_action(g)
	var perk := Vector2(0, -2) if fx.ears > 0 and fx.ears % 8 < 4 else Vector2.ZERO
	draw_cat(seat + perk, action)
	_boat_front(boat, g.inv.boat)
	if g.mode == "fish" and Layout.cat_rod_tip("sit_fish", 0) == null:
		# 고양이 그림에 낚싯대가 없을 때(임시 그림): 손에서 끝까지 그린다. 장력이 오르면 끝이 숙는다.
		var hand: Vector2 = seat + Layout.point("chars/cat", "hand") - Layout.cat_foot()
		var tip := _rod_tip_local(g)
		var straight: Vector2 = Layout.boat(g.inv.boat)["rod_tip"]
		var mid := hand.lerp(straight, 0.6) + (tip - straight) * 0.25
		var points := PackedVector2Array()
		for i in 9:
			var t := i / 8.0
			points.append(hand.lerp(mid, t).lerp(mid.lerp(tip, t), t))
		draw_polyline(points, Pal.INK, 4.0)
		draw_polyline(points, ROD_COLORS[g.inv.rod], 2.0)
	if g.mode == "fish":
		var stern := Vector2(-boat["size"].x * 0.36, 2.0)
		draw_line(stern, stern + Vector2(-4, 30), Pal.SLATE, 2.0)
	draw_set_transform(Vector2.ZERO)


## 뱃전 아래쪽을 고양이 위에 다시 그려 발이 배 안에 들어가 보이게 한다.
func _boat_front(boat: Dictionary, tier: int) -> void:
	var texture := Assets.tex("boats/boat%d.png" % (tier + 1))
	var rim: float = boat["rim"]
	var size := texture.get_size()
	draw_texture_rect_region(texture, Rect2(-boat["pivot"].x, rim - boat["pivot"].y, size.x, size.y - rim), Rect2(0, rim, size.x, size.y - rim))


## 물속에 잠긴 선체를 물색 위에 옅게 다시 그려 수면 아래로 비쳐 보이게 한다.
func _submerged_hull(g: Game) -> void:
	var boat := Layout.boat(g.inv.boat)
	var texture := Assets.tex("boats/boat%d.png" % (g.inv.boat + 1))
	var size := texture.get_size()
	var below: float = size.y - boat["pivot"].y
	if below <= 0.0:
		return
	_boat_transform(g)
	draw_texture_rect_region(texture, Rect2(-boat["pivot"].x, 0, size.x, below), Rect2(0, boat["pivot"].y, size.x, below), Color(0.6, 0.9, 0.9, 0.4))
	draw_set_transform(Vector2.ZERO)


## 수면에 떠 있는 것: 어군 표시와 새, 떠다니는 물건, 큰 파도의 물마루, 소용돌이 자리.
func _surface_things(g: Game, left: float, right: float, tick: int) -> void:
	for s in g.sailing.schools:
		if s["x"] < left - 60.0 or s["x"] > right + 60.0:
			continue
		var sp := Data.fish(s["sp"])
		var slots: int = sp["slots"]
		var alpha := clampf(minf(s["age"] / 60.0, s["life"] / 180.0), 0.0, 1.0)
		var tint := Color(1, 1, 1, alpha)
		var base := "sea/school_small" if slots == 1 else ("sea/school_mid" if slots == 2 else "sea/school_big")
		var center := _origin + Vector2(s["x"], surf(s["x"]))
		Ui.sprite(self, Assets.frame(base, tick), center + Vector2(0, 4), Vector2(0.5, 0.5), false, tint)
		var birds := 4 - mini(slots, 3)
		for i in birds:
			var a: float = tick * 0.03 + i * TAU / birds + s["x"]
			var at := center + Vector2(cos(a) * (30.0 + slots * 6.0), -64.0 - slots * 6.0 + sin(a * 1.3) * 12.0)
			Ui.sprite(self, Assets.frame("sea/bird", tick + i * 7), at, Vector2(0.5, 0.5), sin(a) > 0.0, tint)
	for item in g.sailing.flotsam:
		if item["x"] < left - 20.0 or item["x"] > right + 20.0:
			continue
		var texture := Assets.tex("sea/%s.png" % item["kind"])
		draw_set_transform(_origin + Vector2(item["x"], surf(item["x"]) + 5.0).round(), sin(tick * 0.05 + item["x"]) * 0.14)
		draw_texture(texture, Vector2(-texture.get_width() * 0.5, -texture.get_height() + 6.0).round())
		draw_set_transform(Vector2.ZERO)
	var crest_tex := Assets.tex("sea/wave_crest.png")
	for crest in g.sailing.crests:
		if crest["x"] < left - 40.0 or crest["x"] > right + 40.0 or g.sailing.crest_height(crest) < 5.0:
			continue
		Ui.sprite(self, crest_tex, _origin + Vector2(crest["x"], surf(crest["x"]) + 4.0), Vector2(0.5, 1.0), true)
	var vortex_x := Sea.place_x("vortex")
	if absf(vortex_x - cam.x) < 400.0:
		Ui.sprite(self, Assets.frame("sea/vortex", tick), _origin + Vector2(vortex_x, surf(vortex_x) + 8.0))


## 물: 수면 높이를 따라 물기둥을 세우고(물속 겹의 위쪽이 파도를 탄다), 그 아래는 깊이에 따라 어두워지는 띠로 잇는다.
func _water(mix: Array, left: float, right: float, deep_tone: Color, tick: int) -> void:
	var bottom := cam.y + 184.0
	var parallax := roundf(cam.x * 0.3)
	for i in 2:
		var alpha: float = 1.0 if i == 0 else mix[2]
		if alpha <= 0.0 or (i == 0 and mix[2] >= 1.0):
			continue
		var texture := Assets.tex("sea/under_%s.png" % mix[i])
		var height := texture.get_height()
		if cam.y - 184.0 > height:
			continue
		var tint := Color(1, 1, 1, alpha)
		var x := floorf(left / COL) * COL
		while x < right:
			var top := roundf(surf(x + COL * 0.5))
			var h := minf(height, bottom - top)
			if h > 0.0:
				draw_texture_rect_region(texture, Rect2(_origin.x + x, _origin.y + top, COL, h), Rect2(x - parallax, 0, COL, h), tint)
			x += COL
	# 물속 겹보다 깊은 곳
	var first_height := Assets.tex("sea/under_%s.png" % mix[0]).get_height()
	var row := maxf(first_height - 28.0, floorf((cam.y - 184.0) / 24.0) * 24.0)
	var floor_px := 150.0 * Data.Y_PX
	while row < bottom:
		var t := clampf((row - first_height) / (floor_px - first_height), 0.0, 1.0)
		draw_rect(Rect2(0, _origin.y + row, 640, 24), deep_tone.lerp(Data.DEEP_WATER, pow(t, 0.7)))
		row += 24.0
	# 빛줄기가 느리게 일렁인다.
	if cam.y - 184.0 < 300.0:
		for i in 4:
			var rx := i * 220.0 - fposmod(cam.x * 0.5, 220.0) + 60.0 + sin(tick * 0.008 + i * 1.7) * 18.0
			var glow := 0.05 + 0.04 * sin(tick * 0.02 + i * 2.1)
			draw_colored_polygon(PackedVector2Array([Vector2(rx, _origin.y + 16), Vector2(rx + 34, _origin.y + 16),
				Vector2(rx - 50, _origin.y + 280), Vector2(rx - 110, _origin.y + 280)]), Color(Pal.WHITE, glow))
	# 떠다니는 알갱이: 카메라가 움직일 때 깊이와 속도를 느끼게 한다.
	var cell := 96.0
	var gx := floorf(left / cell) * cell
	while gx < right:
		var gy := maxf(cell, floorf((cam.y - 184.0) / cell) * cell)
		while gy < bottom:
			var seed_value := int(gx * 0.37 + gy * 1.31)
			var px := gx + posmod(seed_value * 17, 96) + sin(tick * 0.02 + seed_value) * 6.0
			var py := gy + posmod(seed_value * 29, 96) - fposmod(tick * 0.1, cell)
			if py > 30.0 and py < Sea.bed_y(px):
				draw_rect(Rect2((_origin + Vector2(px, py)).round(), Vector2(2, 2)), Color(Pal.WHITE, 0.3))
			gy += cell
		gx += cell
	# 수면선
	var line := PackedVector2Array()
	var shade := PackedVector2Array()
	for i in _surf.size():
		var p := _origin + Vector2(_surf_from + i * COL, roundf(_surf[i]))
		line.append(p)
		shade.append(p + Vector2(0, 3))
	draw_polyline(shade, Color(Pal.TEAL_D, 0.6), 2.0)
	draw_polyline(line, Pal.WHITE, 2.0)


## 바닥: 16px 너비로 잘라 바닥 높이에 맞춰 놓는다. 그 위에 유적, 누각, 암초, 난파선.
func _bed(left: float, right: float) -> void:
	var bottom := cam.y + 184.0
	if Sea.bed_y(left) > bottom + 8.0 and Sea.bed_y(right) > bottom + 8.0 and Sea.bed_y(cam.x) > bottom + 8.0:
		return
	var x := floorf(left / BED_COL) * BED_COL
	while x < right:
		var bed := roundf(Sea.bed_y(x + BED_COL * 0.5))
		if bed < bottom:
			var zone: String = Data.ZONES[maxi(1, Sea.zone_index(x))]["id"]
			var rel := "sea/bed_%s.png" % zone
			var texture := Assets.tex(rel)
			var h := texture.get_height()
			draw_texture_rect_region(texture, Rect2(_origin.x + x, _origin.y + bed, BED_COL, h), Rect2(x, 0, BED_COL, h))
			if bed + h < bottom:
				draw_rect(Rect2(_origin.x + x, _origin.y + bed + h, BED_COL, bottom - bed - h), _bottom_color(rel))
		x += BED_COL
	for i in RUIN_SPOTS_M.size():
		_on_bed("sea/ruin_%d.png" % (i % 3 + 1), RUIN_SPOTS_M[i] * Data.X_PX, left, right, i % 2 == 1)
	for m in PAVILION_SPOTS_M:
		_on_bed("sea/pavilion.png", m * Data.X_PX, left, right)
	var reef: Dictionary = Data.PLACES["reef"]
	for k in [-0.3, 0.02, 0.32]:
		_on_bed("sea/reef.png", (reef["x"] + reef["w"] * k) * Data.X_PX, left, right, k < 0.0)
	_on_bed("sea/wreck.png", Sea.place_x("wreck"), left, right)


func _on_bed(rel: String, x: float, left: float, right: float, flip := false) -> void:
	var texture := Assets.tex(rel)
	if x < left - texture.get_width() or x > right + texture.get_width():
		return
	Ui.sprite(self, texture, _origin + Vector2(x, Sea.bed_y(x) + 6.0), Vector2(0.5, 1.0), flip)


func _fish(g: Game, left: float, right: float, tick: int) -> void:
	var bottom := cam.y + 220.0
	var top := cam.y - 220.0
	for f in g.shoal.fish:
		if f["x"] < left - 90.0 or f["x"] > right + 90.0 or f["y"] > bottom or f["y"] < top:
			continue
		var sp: Dictionary = f["sp"]
		var hooked: bool = f["state"] == "hooked"
		var pulling := hooked and g.fishing.phase == "pull"
		var base := "fish/%s_swim" % sp["id"]
		if sp["id"] == "legend" and not hooked:
			base = "fish/legend_shadow_swim"
		var texture := Assets.frame(base, tick * (2 if pulling else 1) + int(f["phase"] * 10.0))
		var size := texture.get_size()
		var squash := 0.6 if f["squash"] > 0 else 1.0
		var turn := sin(tick * 0.7) * 0.2 if pulling else 0.0
		var alpha := clampf((tick - f.get("born", 0)) / 30.0, 0.0, 1.0)
		var pos := _origin + Vector2(f["x"], f["y"]).round()
		draw_set_transform(pos, turn * f["dir"], Vector2(f["dir"] * squash, 1.0))
		draw_texture(texture, (-size * 0.5).round(), Color(1, 1, 1, alpha))
		draw_set_transform(Vector2.ZERO)
		var mark := ""
		match f["state"]:
			"sniff":
				mark = "?"
			"nibble":
				mark = "…"
			"hooked":
				mark = "!" if pulling else ""
		if mark != "":
			Ui.label_center(self, pos.x, pos.y - size.y * 0.5 - 18.0 + roundf(sin(tick * 0.3) * 2.0), mark, Pal.CREAM)


## 낚싯줄: 낚싯대 끝에서 바늘까지. 느슨하면 처지고, 당기면 팽팽해지며 밝아지고, 입질에는 떤다.
func _line(g: Game) -> void:
	var fishing := g.fishing
	var tip := _boat_point(g, _rod_tip_local(g))
	var hook := Vector2(fishing.hook_x(g), maxf(fishing.hook_y, tip.y + 14.0))
	var color := Pal.CREAM
	var sag := sin(g.tick * 0.05) * 4.0 + clampf(fishing.hook_v * 0.03, -6.0, 6.0)
	if fishing.fighting:
		var f: Dictionary = fishing.engaged
		var size: Vector2 = Assets.frame("fish/%s_swim" % f["id"], 0).get_size()
		hook = Vector2(f["x"] + f["dir"] * size.x * 0.4, f["y"])
		var t := fishing.tension
		color = Pal.CREAM.lerp(Color.WHITE, clampf(t * 1.4, 0.0, 1.0))
		if t > 0.85:
			color = Pal.ORANGE if g.tick % 6 < 3 else Color.WHITE
		sag = (1.0 - t) * 30.0 * (1.0 if fishing.off >= 0.0 else -1.0)
	var jitter := sin(g.tick * 2.1) * fx.twitch * 0.4
	var mid := (tip + hook) * 0.5 + Vector2(sag + jitter, 0.0)
	var points := PackedVector2Array()
	for i in 15:
		var t := i / 14.0
		points.append((_origin + tip.lerp(mid, t).lerp(mid.lerp(hook, t), t)).round())
	for i in points.size() - 1:
		Ui.pixel_line(self, points[i], points[i + 1], color)
	if fishing.fighting:
		return
	var at := (_origin + hook + Vector2(jitter, 0)).round()
	var hook_tex := Assets.tex("sea/hook.png")
	draw_texture(hook_tex, at - Vector2(hook_tex.get_width() * 0.5, 0))
	if g.inv.baits[g.inv.bait] > 0:
		var bait := Assets.tex("sea/bait_%s.png" % g.inv.bait)
		var pulse := 1.0 + (0.5 if fx.twitch > 0 and g.tick % 4 < 2 else 0.0)
		draw_texture_rect(bait, Rect2(at + Vector2(-bait.get_width() * 0.5 * pulse, hook_tex.get_height() - 4.0), bait.get_size() * pulse), false)


## 낚인 물고기가 물 밖으로 튀어 배로 날아든다.
func _fly(g: Game) -> void:
	if fx.fly.is_empty():
		return
	var t: float = fx.fly["t"] / float(Fx.FLY_TICKS)
	var from: Vector2 = fx.fly["from"]
	var to := Vector2(g.sailing.x, g.sailing.y - 20.0)
	var at := from.lerp(to, Ui.ease_out(t)) - Vector2(0, sin(t * PI) * 70.0)
	var texture := Assets.frame("fish/%s_swim" % fx.fly["id"], g.tick * 2)
	draw_set_transform(_origin + at.round(), -1.3 + t * 2.6, Vector2(-1, 1))
	draw_texture(texture, (-texture.get_size() * 0.5).round())
	draw_set_transform(Vector2.ZERO)


func _pointer(g: Game) -> void:
	var target := g.guide.target(g)
	if target.is_empty() or g.menu.busy():
		return
	var dir: int = target.get("dir", 0)
	var word := ""
	if dir == 0:
		var sx: float = _origin.x + target["x"]
		if sx < 20.0:
			dir = -1
		elif sx > 620.0:
			dir = 1
		else:
			draw_pointer(Vector2(sx, _origin.y + surf(target["x"]) - 96.0))
			return
		word = "← 어군" if dir < 0 else "어군 →"
	else:
		word = "← 항구" if dir < 0 else "→"
	if g.tick % 40 >= 28:
		return
	var push := roundf(absf(sin(g.tick * 0.1)) * 4.0)
	if dir < 0:
		Ui.label(self, Vector2(10 - push, 150), word, Pal.CREAM)
	else:
		Ui.label(self, Vector2(630 - Ui.width(word, "bold") + push, 150), word, Pal.CREAM)
