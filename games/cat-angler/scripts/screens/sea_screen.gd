class_name SeaScreen
extends Screen
## 바다 화면: 항해와 낚시. 구간마다의 겹(하늘·먼 배경·중간 배경·물속·바닥)을 카메라 위치에 따라 서서히 바꿔 그리고,
## 실제 파도 위에 배와 고양이를 놓는다. 닻을 내리면 카메라가 미끼를 따라 내려간다.
## 그리기 명령을 아끼려고 수면 높이는 틱마다 한 번만 재서(_surf) 수면선, 물기둥, 문양, 배가 함께 쓴다.

const ZOOM := 2.0                # 바다는 두 배로 당겨 그린다(기준 화면의 비율). 화면 한 칸 = 그림 픽셀 2x2
const VIEW := Vector2(320, 180)  # 당겨 본 세계의 크기(세계 px)
const SURFACE_LINES := [100.0, 124.0, 124.0]   # 항해 중 수면선의 자리(VIEW 의 y). 돛이 있는 배는 더 아래에 둔다
const ANCHOR_DIP := 16.0        # 닻을 내리면 카메라가 이만큼 잠긴다
const COL := 4.0                # 물기둥 하나의 너비
const BED_FADE_M := 90.0        # 구간 경계에서 바닥 그림이 섞이는 거리
const ROD_COLORS := [Pal.SAND, Pal.WOOD, Pal.TEAL_D]
const RUIN_SPOTS_M := [1004.0, 1045.0, 1090.0, 1340.0, 1385.0, 1500.0, 1545.0, 1720.0, 1765.0]
const PAVILION_SPOTS_M := [1960.0, 2310.0]
## 바닥 장식: 구간마다 놓일 그림(sea/<이름>.png). 자리는 x 에서 정해지는 번호로 고른다.
const DRESS := {
	"shallow": ["weed_1", "weed_2", "rock_1", "coral_1", "weed_3", "coral_2", "rock_2", "shell_1"],
	"open": ["kelp_1", "rock_3", "kelp_2", "weed_2", "rock_4", "weed_3"],
	"deep": ["glow_1", "kelp_2", "glow_2", "pearl_1", "lantern_1", "kelp_1"],
}
## 가파른 비탈에서는 바닥 그림의 무늬 없는 한 줄(이 x)만 늘려 써서, 조개와 돌이 비스듬히 찢겨 보이지 않게 한다.
const BED_PLAIN_X := {"shallow": 209.0, "open": 307.0, "deep": 80.0}
const SWAYING := ["weed_1", "weed_2", "weed_3", "kelp_1", "kelp_2"]
const DRESS_CELL := 38.0
## 멀리 떼 지어 다니는 잔고기(낚이지 않는 배경). 구간마다 물색보다 한 단계 짙은 색.
const MINNOW_TINT := {"shallow": Color("#2E3068"), "open": Color("#2E3068"), "deep": Color("#426A96")}
const MINNOW_CELL := 210.0
const JELLY_CELL := 260.0
const SCHOOL_HINT_M := 220.0    # 이 거리 안의 어군은 화면 밖에 있어도 쪽을 알려 준다

var cam := Vector2.ZERO

var _origin := Vector2.ZERO
var _snapped := false
var _surf := PackedFloat32Array()
var _surf_from := 0.0
var _bottoms := {}            # 텍스처 경로 -> 맨 아랫줄의 색
var _texts: Array = []        # 이번 프레임에 제 크기(1배)로 얹을 글자와 표시


func _ready() -> void:
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	scale = Vector2(ZOOM, ZOOM)


func setup(g: Game, effects: Fx) -> void:
	super.setup(g, effects)
	# 처음 나타나는 순간에 읽느라 멈칫하지 않게 바다의 그림을 미리 읽어 둔다.
	for sp in Data.FISH:
		Assets.anim("fish/%s_swim" % sp["id"])
	for base in ["fish/legend_shadow_swim", "sea/splash", "sea/bubble", "sea/sparkle", "sea/bird", "sea/vortex",
			"sea/school_small", "sea/school_mid", "sea/school_big", "sea/minnow", "sea/jelly", "chars/cat_sit_fish", "chars/cat_reel",
			"chars/cat_strain", "chars/cat_cheer", "chars/cat_sad"]:
		Assets.anim(base)
	for zone in ["shallow", "open", "deep"]:
		for layer in ["sky", "far", "mid", "under", "bed", "deco_far", "deco_far2"]:
			Assets.tex("sea/%s_%s.png" % [layer, zone])
		for name in DRESS[zone]:
			Assets.tex("sea/%s.png" % name)
	Assets.tex("sea/ray.png")
	_move_camera()
	_sample_surface()


func advance() -> void:
	_move_camera()
	_origin = (VIEW * 0.5 - cam + fx.offset / ZOOM).round()
	_sample_surface()
	queue_redraw()


func focus() -> Vector2:
	return (_origin + Vector2(game.sailing.x, game.sailing.y - 24.0)) * ZOOM


# ---- 카메라와 수면 ----

func _move_camera() -> void:
	var g := game
	var s := g.sailing
	var surface_line: float = SURFACE_LINES[g.inv.boat]
	# 가는 쪽을 조금 앞서 보여 준다.
	var target := Vector2(s.x + clampf(s.vx * 0.3, -56.0, 56.0), VIEW.y * 0.5 - surface_line)
	if g.mode == "fish":
		var f := g.fishing
		target.x = f.hook_x(g) - 24.0 + (f.off * 0.5 if f.fighting else 0.0)
		# 닻을 내리면 바로 조금 잠기고, 그 뒤로는 미끼를 따라 내려간다. 바닥이 화면 아래 3분의 1에 걸리면 멈춘다.
		var shallowest := target.y + ANCHOR_DIP
		var deepest := maxf(shallowest, Sea.bed_y(f.hook_x(g)) - 46.0)
		target.y = clampf(f.hook_y - 24.0, shallowest, deepest)
	target.x = clampf(target.x, Sailing.left_limit() - 40.0, Data.SEA_END_M * Data.X_PX - VIEW.x * 0.5)
	if not _snapped:
		cam = target
		_snapped = true
		_origin = (VIEW * 0.5 - cam).round()
	cam.x += (target.x - cam.x) * 0.08
	cam.y += (target.y - cam.y) * 0.07


func _sample_surface() -> void:
	_surf_from = floorf((cam.x - VIEW.x * 0.5 - 8.0) / COL) * COL
	var count := int((VIEW.x + 16.0) / COL) + 3
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


## 세계 x 의 바닥 섞임: 비탈을 내려가는 동안 다음 구간의 바닥으로 바뀐다.
func _bed_mix(x: float) -> Array:
	var m := x / Data.X_PX
	if m < 1350.0:
		return ["shallow", "open", smoothstep(900.0, 900.0 + BED_FADE_M, m)]
	return ["open", "deep", smoothstep(1800.0, 1800.0 + BED_FADE_M, m)]


func _bottom_color(rel: String) -> Color:
	if not _bottoms.has(rel):
		var image := Assets.tex(rel).get_image()
		_bottoms[rel] = image.get_pixel(0, image.get_height() - 1)
	return _bottoms[rel]


## x 에서 정해지는 번호(장식과 배경 생물의 자리를 난수 없이 고른다).
static func _pick(cell: float, salt: int) -> int:
	return posmod(int(cell) * 73856093 ^ salt * 19349663, 9973)


# ---- 그리기 ----

func _draw() -> void:
	var g := game
	var tick := g.tick
	var mix := _zone_mix()
	var left := cam.x - VIEW.x * 0.5 - 4.0
	var right := cam.x + VIEW.x * 0.5 + 4.0
	var horizon := _origin.y
	_texts.clear()
	var deep_tone: Color = _bottom_color("sea/under_%s.png" % mix[0]).lerp(_bottom_color("sea/under_%s.png" % mix[1]), mix[2])
	draw_rect(Rect2(Vector2.ZERO, VIEW), deep_tone)
	if horizon > -8.0:
		_backdrop("sky", mix, 0.03, horizon, 0.0)
		_backdrop("far", mix, 0.1, horizon, 12.0)
		_backdrop("mid", mix, 0.22, horizon, 16.0)
		_above_water(left, right, tick)
	_surface_things(g, left, right, tick)
	_boat(g)
	_water(mix, left, right, deep_tone, tick)
	if horizon > -40.0:
		_submerged_hull(g)
	_drifters(left, right, tick)
	_bed(left, right, tick)
	_fish(g, left, right, tick)
	if g.mode == "fish":
		_line(g)
	_fly(g)
	_effects()
	_pointer(g)
	_overlay_texts()


## 구간 겹 하나를 가로로 이어 깔고, 구간 경계에서는 다음 구간의 것을 겹쳐 서서히 바꾼다.
## 아래 가장자리가 수평선에서 lift 만큼 위에 온다(먼 섬의 밑동이 물결 문양 뒤에 잠겨 물 위에 앉아 보인다).
func _backdrop(layer: String, mix: Array, parallax: float, horizon: float, lift: float) -> void:
	for i in 2:
		var alpha: float = 1.0 if i == 0 else mix[2]
		if alpha <= 0.0 or (i == 0 and mix[2] >= 1.0):
			continue
		var texture := Assets.tex("sea/%s_%s.png" % [layer, mix[i]])
		var size := texture.get_size()
		draw_texture_rect_region(texture, Rect2(0, horizon - lift - size.y, VIEW.x, size.y),
			Rect2(roundf(cam.x * parallax), 0, VIEW.x, size.y), Color(1, 1, 1, alpha))


## 수면 위의 붙박이: 부두, 섬, 배 뒤의 물결 문양.
func _above_water(left: float, right: float, tick: int) -> void:
	# 전통 물결 문양: 수면선에 걸쳐 천천히 흐른다. 먼 섬과 부두는 그 앞에 선다.
	var pattern := Assets.tex("sea/surface_pattern.png")
	var pw := pattern.get_width()
	var ph := pattern.get_height()
	var flow := tick * 0.12
	# 8px 띠로 잘라 띠마다 수면을 따라 올리고 내린다(타일째 움직이면 타일 사이에 세로 이음매가 보인다).
	var px := floorf(left / 8.0) * 8.0
	while px < right:
		var lift := roundf(surf(px + 4.0) * 0.6) + 6.0
		draw_texture_rect_region(pattern, Rect2(_origin.x + px, _origin.y + lift - ph, 8, ph), Rect2(fposmod(px - roundf(flow), pw), 0, 8, ph))
		px += 8.0
	var pier := Assets.tex("sea/pier.png")
	var pier_right := Sailing.left_limit() - 56.0
	if pier_right > left:
		draw_texture(pier, _origin + Vector2(pier_right - pier.get_width(), 24.0 - pier.get_height()))
	var isle := Assets.tex("sea/island_far.png")
	var isle_x := Sea.place_x("island")
	if absf(isle_x - cam.x) < VIEW.x * 0.5 + isle.get_width():
		draw_texture(isle, _origin + Vector2(roundf(isle_x - isle.get_width() * 0.5), 16.0 - isle.get_height()))


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
		Ui.pixel_line(self, stern, stern + Vector2(-4, 30), Pal.SLATE)
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
		var birds := 4 - mini(slots, 3)
		# 배가 어군 위에 닻을 내리면 새들은 자리를 비킨다(고양이 머리 위에서 겹쳐 뭉개진다).
		if g.mode == "fish" and absf(s["x"] - g.sailing.x) < 90.0:
			birds = 0
		var tint := Color(1, 1, 1, alpha)
		var base := "sea/school_small" if slots == 1 else ("sea/school_mid" if slots == 2 else "sea/school_big")
		var center := _origin + Vector2(s["x"], surf(s["x"]))
		Ui.sprite(self, Assets.frame(base, tick), center + Vector2(0, 4), Vector2(0.5, 0.5), false, tint)
		for i in birds:
			var a: float = tick * 0.03 + i * TAU / birds + s["x"]
			var at := center + Vector2(cos(a) * (24.0 + slots * 4.0), -50.0 - slots * 4.0 + sin(a * 1.3) * 8.0)
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
	if absf(vortex_x - cam.x) < 260.0:
		Ui.sprite(self, Assets.frame("sea/vortex", tick), _origin + Vector2(vortex_x, surf(vortex_x) + 8.0))


## 물: 수면 높이를 따라 물기둥을 세우고(물속 겹의 위쪽이 파도를 탄다), 그 아래는 깊이에 따라 어두워지는 띠로 잇는다.
func _water(mix: Array, left: float, right: float, deep_tone: Color, tick: int) -> void:
	var top_edge := cam.y - VIEW.y * 0.5
	var bottom := cam.y + VIEW.y * 0.5 + 2.0
	var parallax := roundf(cam.x * 0.3)
	for i in 2:
		var alpha: float = 1.0 if i == 0 else mix[2]
		if alpha <= 0.0 or (i == 0 and mix[2] >= 1.0):
			continue
		var texture := Assets.tex("sea/under_%s.png" % mix[i])
		var height := texture.get_height()
		if top_edge > height:
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
	var row := maxf(first_height - 28.0, floorf(top_edge / 24.0) * 24.0)
	var floor_px := 150.0 * Data.Y_PX
	while row < bottom:
		var t := clampf((row - first_height) / (floor_px - first_height), 0.0, 1.0)
		draw_rect(Rect2(0, _origin.y + row, VIEW.x, 24), deep_tone.lerp(Data.DEEP_WATER, pow(t, 0.7)))
		row += 24.0
	_far_shapes(mix)
	# 빛줄기: 수면에서 비스듬히 내려와 느리게 일렁인다.
	if top_edge < 200.0:
		var ray := Assets.tex("sea/ray.png")
		var gap := 132.0
		var shift := fposmod(cam.x * 0.6, gap)
		for i in 4:
			var rx := cam.x - VIEW.x * 0.5 + i * gap - shift - 40.0 + roundf(sin(tick * 0.008 + i * 1.7) * 6.0)
			draw_texture(ray, _origin + Vector2(roundf(rx), roundf(surf(rx + 60.0)) + 2.0), Color(1, 1, 1, 0.1 + 0.04 * sin(tick * 0.02 + i * 2.1)))
	# 떠다니는 알갱이: 카메라가 움직일 때 깊이와 속도를 느끼게 한다. 깊은 곳의 것은 빛난다.
	var cell := 56.0
	var gx := floorf(left / cell) * cell
	while gx < right:
		var gy := maxf(0.0, floorf(top_edge / cell) * cell)
		while gy < bottom:
			var n := _pick(gx + gy * 7.0, 3)
			var px := gx + n % 56 + sin(tick * 0.02 + n) * 4.0
			var py := gy + (n / 56) % 56 - fposmod(tick * 0.06, cell)
			if py > 18.0 and py < Sea.bed_y(px):
				var glow: bool = py > 420.0 and n % 3 == 0
				draw_rect(Rect2((_origin + Vector2(px, py)).round(), Vector2(1, 1)), Pal.CYAN if glow else Color(Pal.WHITE, 0.45))
			gy += cell
		gx += cell
	# 수면선
	# 선체에 걸친 자리는 긋지 않는다(배 위에 흰 점이 끊겨 보인다).
	var hull: float = Layout.boat(game.inv.boat)["size"].x * 0.46
	var x := floorf(left / COL) * COL
	while x < right:
		var top := roundf(surf(x + COL * 0.5))
		if absf(x + COL * 0.5 - game.sailing.x) < hull:
			x += COL
			continue
		draw_rect(Rect2(_origin.x + x, _origin.y + top, COL, 1), Pal.WHITE)
		draw_rect(Rect2(_origin.x + x, _origin.y + top + 2.0, COL, 1), Color(Pal.TEAL_D, 0.5))
		x += COL


## 물속 먼 곳의 윤곽(바위, 해초 숲, 무너진 기둥): 카메라 아래 바닥에 앉아 세계보다 느리게 흐른다.
func _far_shapes(mix: Array) -> void:
	# 먼 겹: 수면에 있을 때는 5m 쯤 아래에 능선이 걸리고, 카메라가 내려가면 그 35% 속도로 따라 올라온다.
	var far_top := roundf(30.0 + maxf(0.0, cam.y + 34.0) * 0.65)
	# 가까운 겹: 바닥에 앉는다. 암초의 솟은 바닥은 따르지 않는다(밝은 물에 짙은 윤곽이 떠 보인다).
	var near_base := roundf(Sea._blend_exact(cam.x, "bed") * Data.Y_PX + 6.0)
	for layer in [["deco_far2", 0.3, far_top], ["deco_far", 0.55, -1.0]]:
		for i in 2:
			var alpha: float = 1.0 - mix[2] if i == 0 else mix[2]
			if alpha <= 0.0:
				continue
			var texture := Assets.tex("sea/%s_%s.png" % [layer[0], mix[i]])
			var size := texture.get_size()
			var top: float = layer[2] if layer[2] >= 0.0 else near_base - size.y
			if top > cam.y + VIEW.y * 0.5 or top + size.y < cam.y - VIEW.y * 0.5:
				continue
			draw_texture_rect_region(texture, Rect2(0, _origin.y + top, VIEW.x, size.y),
				Rect2(roundf(cam.x * layer[1]), 0, VIEW.x, size.y), Color(1, 1, 1, alpha))


## 낚이지 않는 배경 생물: 멀리 떼 지어 도는 잔고기와 깊은 물의 해파리. 자리는 x 칸의 번호와 틱만으로 정해진다.
func _drifters(left: float, right: float, tick: int) -> void:
	var top_edge := cam.y - VIEW.y * 0.5 - 20.0
	var bottom := cam.y + VIEW.y * 0.5 + 20.0
	var cx := floorf((left - MINNOW_CELL) / MINNOW_CELL) * MINNOW_CELL
	while cx < right + MINNOW_CELL:
		var n := _pick(cx, 11)
		var zone: Dictionary = Data.ZONES[maxi(1, Sea.zone_index(cx))]
		var swing := sin(tick * 0.004 + n)
		var heading := cos(tick * 0.004 + n) < 0.0
		var x := cx + MINNOW_CELL * 0.5 + swing * 96.0
		var bed := Sea.bed_y(x)
		var y := minf(28.0 + (n % 100) / 100.0 * (zone["bed"] * Data.Y_PX * 0.7), bed - 30.0) + sin(tick * 0.011 + n) * 6.0
		if y > top_edge and y < bottom and bed > 80.0:
			var tint: Color = MINNOW_TINT[zone["id"]]
			for k in 5 + n % 4:
				var kn := _pick(cx + k * 13.0, 5)
				var off := Vector2(kn % 44 - 22.0, (kn / 44) % 22 - 11.0) + Vector2(sin(tick * 0.03 + kn) * 2.0, 0)
				Ui.sprite(self, Assets.frame("sea/minnow", tick + kn), _origin + Vector2(x, y) + off, Vector2(0.5, 0.5), heading, tint)
		cx += MINNOW_CELL
	cx = floorf((left - JELLY_CELL) / JELLY_CELL) * JELLY_CELL
	while cx < right + JELLY_CELL:
		var n := _pick(cx, 23)
		var x := cx + n % int(JELLY_CELL) + sin(tick * 0.006 + n) * 14.0
		var bed := Sea.bed_y(x)
		if bed > 420.0 and x > left - 20.0 and x < right + 20.0:
			var y := 240.0 + (n / 7) % int(bed - 300.0) - fposmod(tick * 0.05 + n, 40.0) * 0.0 + sin(tick * 0.02 + n) * 8.0
			if y > top_edge and y < bottom:
				Ui.sprite(self, Assets.frame("sea/jelly", tick + n), _origin + Vector2(x, y), Vector2(0.5, 0.5))
		cx += JELLY_CELL


## 바닥: 높이가 같은 구간을 한 띠로 묶어 2px 단위로 놓아 비탈이 매끄럽다. 구간 경계의 비탈에서는 두 구간의 바닥이 섞인다.
## 그 위에 유적, 누각, 암초, 난파선, 구간별 장식.
func _bed(left: float, right: float, tick: int) -> void:
	for i in RUIN_SPOTS_M.size():
		_on_bed("sea/ruin_%d.png" % (i % 3 + 1), RUIN_SPOTS_M[i] * Data.X_PX, left, right, i % 2 == 1)
	for m in PAVILION_SPOTS_M:
		_on_bed("sea/pavilion.png", m * Data.X_PX, left, right)
	var reef: Dictionary = Data.PLACES["reef"]
	for k in [-0.3, 0.02, 0.32]:
		_on_bed("sea/reef.png", (reef["x"] + reef["w"] * k) * Data.X_PX, left, right, k < 0.0)
	_on_bed("sea/wreck.png", Sea.place_x("wreck"), left, right)
	var bottom := cam.y + VIEW.y * 0.5 + 2.0
	if Sea.bed_y(left) > bottom + 8.0 and Sea.bed_y(right) > bottom + 8.0 and Sea.bed_y(cam.x) > bottom + 8.0:
		return
	var x := floorf(left / 2.0) * 2.0
	while x < right:
		var bed := roundf(Sea.bed_y(x + 1.0))
		var run := 2.0
		while run < 32.0 and x + run < right and roundf(Sea.bed_y(x + run + 1.0)) == bed:
			run += 2.0
		if bed < bottom:
			var mix := _bed_mix(x)
			var steep := absf(Sea.bed_y(x + 5.0) - Sea.bed_y(x - 3.0)) > 4.0
			var fill := Color.BLACK
			for i in 2:
				var alpha: float = 1.0 if i == 0 else mix[2]
				if alpha <= 0.0 or (i == 0 and mix[2] >= 1.0):
					continue
				var rel := "sea/bed_%s.png" % mix[i]
				var texture := Assets.tex(rel)
				draw_texture_rect_region(texture, Rect2(_origin.x + x, _origin.y + bed, run, texture.get_height()),
					Rect2(BED_PLAIN_X[mix[i]] if steep else x, 0, run, texture.get_height()), Color(1, 1, 1, alpha))
				fill = _bottom_color(rel) if i == 0 or mix[2] >= 1.0 else fill.lerp(_bottom_color(rel), alpha)
			if bed + 64.0 < bottom:
				draw_rect(Rect2(_origin.x + x, _origin.y + bed + 64.0, run, bottom - bed - 64.0), fill)
		x += run
	_dressing(left, right, tick)


## 바닥에 놓는 큰 그림. 바닥이 울퉁불퉁해도 밑동이 뜨지 않게, 그림 너비 안에서 가장 깊은 곳까지 묻는다.
func _on_bed(rel: String, x: float, left: float, right: float, flip := false) -> void:
	var texture := Assets.tex(rel)
	var half := texture.get_width() * 0.5
	if x < left - half * 2.0 or x > right + half * 2.0:
		return
	var base := maxf(Sea.bed_y(x), maxf(Sea.bed_y(x - half * 0.8), Sea.bed_y(x + half * 0.8)))
	Ui.sprite(self, texture, _origin + Vector2(x, base + 6.0), Vector2(0.5, 1.0), flip)


## 구간별 바닥 장식(해초, 산호, 바위, 빛나는 것). 해초는 가로 띠로 잘라 위로 갈수록 크게 흔든다.
func _dressing(left: float, right: float, tick: int) -> void:
	var bottom := cam.y + VIEW.y * 0.5
	var gx := floorf((left - 40.0) / DRESS_CELL) * DRESS_CELL
	while gx < right + 40.0:
		var n := _pick(gx, 41)
		var x := gx + n % int(DRESS_CELL - 8.0)
		var bed := Sea.bed_y(x)
		gx += DRESS_CELL
		# 넷 중 하나는 비우고, 가파른 비탈과 암초 위에는 놓지 않는다.
		if n % 4 == 0 or bed - 100.0 > bottom or bed < 150.0 or absf(Sea.bed_y(x + 10.0) - Sea.bed_y(x - 10.0)) > 8.0:
			continue
		var names: Array = DRESS[Data.ZONES[maxi(1, Sea.zone_index(x))]["id"]]
		var name: String = names[(n / 4) % names.size()]
		var texture := Assets.tex("sea/%s.png" % name)
		var size := texture.get_size()
		var foot := _origin + Vector2(x, bed + 5.0).round()
		var flip := n % 2 == 1
		if name not in SWAYING:
			Ui.sprite(self, texture, foot, Vector2(0.5, 1.0), flip)
			continue
		var strip := 4.0
		var rows := int(ceilf(size.y / strip))
		for r in rows:
			var from_top := r * strip
			var h := minf(strip, size.y - from_top)
			var lift := 1.0 - (from_top + h) / size.y
			var sway := roundf(sin(tick * 0.035 + n + lift * 2.2) * 3.0 * lift)
			var dest := Rect2(foot.x - size.x * 0.5 + sway, foot.y - size.y + from_top, size.x, h)
			if flip:
				dest = Rect2(dest.position + Vector2(size.x, 0), Vector2(-size.x, h))
			draw_texture_rect_region(texture, dest, Rect2(0, from_top, size.x, h))


func _fish(g: Game, left: float, right: float, tick: int) -> void:
	var bottom := cam.y + VIEW.y * 0.5 + 40.0
	var top := cam.y - VIEW.y * 0.5 - 40.0
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
			_texts.append({"at": Vector2(pos.x, pos.y - size.y * 0.5 - 10.0 + roundf(sin(tick * 0.3))), "text": mark, "color": Pal.CREAM, "center": true})


## 낚싯줄: 낚싯대 끝에서 바늘까지. 느슨하면 처지고, 당기면 팽팽해지며 밝아지고, 입질에는 떤다.
func _line(g: Game) -> void:
	var fishing := g.fishing
	var tip := _boat_point(g, _rod_tip_local(g))
	var hook := Vector2(fishing.hook_x(g), maxf(fishing.hook_y, tip.y + 14.0))
	var color := Pal.CREAM
	var sag := sin(g.tick * 0.05) * 3.0 + clampf(fishing.hook_v * 0.03, -5.0, 5.0)
	if fishing.fighting:
		var f: Dictionary = fishing.engaged
		var size: Vector2 = Assets.frame("fish/%s_swim" % f["id"], 0).get_size()
		hook = Vector2(f["x"] + f["dir"] * size.x * 0.4, f["y"])
		var t := fishing.tension
		color = Pal.CREAM.lerp(Color.WHITE, clampf(t * 1.4, 0.0, 1.0))
		if t > 0.85:
			color = Pal.ORANGE if g.tick % 6 < 3 else Color.WHITE
		sag = (1.0 - t) * 22.0 * (1.0 if fishing.off >= 0.0 else -1.0)
	var jitter := sin(g.tick * 2.1) * fx.twitch * 0.3
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
		var grow := 1.0 if fx.twitch > 0 and g.tick % 4 < 2 else 0.0
		draw_texture(bait, at + Vector2(-bait.get_width() * 0.5, hook_tex.get_height() - 4.0 + grow))


## 낚인 물고기가 물 밖으로 튀어 배로 날아든다.
func _fly(g: Game) -> void:
	if fx.fly.is_empty():
		return
	var t: float = fx.fly["t"] / float(Fx.FLY_TICKS)
	var from: Vector2 = fx.fly["from"]
	var to := Vector2(g.sailing.x, g.sailing.y - 20.0)
	var at := from.lerp(to, Ui.ease_out(t)) - Vector2(0, sin(t * PI) * 50.0)
	var texture := Assets.frame("fish/%s_swim" % fx.fly["id"], g.tick * 2)
	draw_set_transform(_origin + at.round(), -1.3 + t * 2.6, Vector2(-1, 1))
	draw_texture(texture, (-texture.get_size() * 0.5).round())
	draw_set_transform(Vector2.ZERO)


## 세계의 입자와 효과. 떠오르는 글자는 제 크기로 얹는다.
func _effects() -> void:
	for s in fx.sprites:
		Ui.sprite(self, Assets.frame(s["base"], fx.tick, s["start"], true), _origin + s["pos"])
	for p in fx.particles:
		var side: float = maxf(1.0, p["size"] - 1.0)
		draw_rect(Rect2((_origin + p["pos"]).round(), Vector2(side, side)), p["color"])
	for f in fx.floaters:
		_texts.append({"at": _origin + f["pos"], "text": f["text"], "color": f["color"], "center": false})


## 길잡이 화살표와 어군이 있는 쪽. 길잡이가 끝난 뒤에도 가까운 어군이 화면 밖에 있으면 쪽과 거리를 알려 준다.
func _pointer(g: Game) -> void:
	if g.menu.busy():
		return
	var target := g.guide.target(g)
	var dir: int = target.get("dir", 0)
	var word := ""
	if target.is_empty():
		if g.mode != "sail":
			return
		var near := INF
		for school in g.sailing.schools:
			if absf(school["x"] - g.sailing.x) < absf(near - g.sailing.x):
				near = school["x"]
		var apart := absf(near - g.sailing.x) / Data.X_PX
		if near == INF or apart > SCHOOL_HINT_M or absf(near - cam.x) < VIEW.x * 0.5 - 10.0:
			return
		dir = -1 if near < cam.x else 1
		word = "← 어군 %dm" % int(apart) if dir < 0 else "어군 %dm →" % int(apart)
	elif dir == 0:
		var sx: float = _origin.x + target["x"]
		if sx < 10.0:
			dir = -1
		elif sx > VIEW.x - 10.0:
			dir = 1
		else:
			_texts.append({"at": Vector2(sx, _origin.y + surf(target["x"]) - 66.0), "arrow": true})
			return
		word = "← 어군" if dir < 0 else "어군 →"
	else:
		word = "← 항구" if dir < 0 else "→"
	if not target.is_empty() and g.tick % 40 >= 28:
		return
	var push := roundf(absf(sin(g.tick * 0.1)) * 4.0) if not target.is_empty() else 0.0
	var at := Vector2(10 - push, 150) if dir < 0 else Vector2(630 - Ui.width(word, "bold") + push, 150)
	_texts.append({"screen": at, "text": word, "color": Pal.CREAM, "center": false})


## 세계 위에 얹는 글자와 화살표는 당겨 그리지 않는다(글꼴과 UI 는 늘 1배다).
func _overlay_texts() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE / ZOOM)
	for t in _texts:
		if t.has("arrow"):
			draw_pointer(t["at"] * ZOOM)
			continue
		var at: Vector2 = t["screen"] if t.has("screen") else t["at"] * ZOOM
		if t["center"]:
			Ui.label_center(self, at.x, at.y, t["text"], t["color"])
		else:
			Ui.label(self, at, t["text"], t["color"])
	draw_set_transform(Vector2.ZERO)
