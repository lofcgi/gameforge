extends Screen
## 타이틀: 움직이는 바다 배경 위의 로고. 메뉴 항목은 Overlays 가 그린다.

const WATER_Y := 226.0
const BOAT_X := 516.0
const ZOOM := 2.0


func _draw() -> void:
	var tick := game.tick
	draw_texture(Assets.tex("places/title.png"), Vector2.ZERO)
	# 수면 문양이 천천히 흐르고, 나룻배가 그 위에서 흔들린다. 바다 화면과 같은 두 배 크기로 그린다.
	var pattern := Assets.tex("sea/surface_pattern.png")
	var pw := pattern.get_width()
	var drift := fposmod(tick * 0.1, pw)
	draw_set_transform(Vector2(0, WATER_Y), 0.0, Vector2(ZOOM, ZOOM))
	var x := -drift - pw
	while x < 320.0:
		var lift := roundf(sin((x + tick * 0.4) * 0.04) * 1.5)
		draw_texture(pattern, Vector2(roundf(x), -pattern.get_height() + lift))
		x += pw
	var bob := sin(tick * 0.04) * 1.5
	var tilt := sin(tick * 0.03 + 1.0) * 0.04
	var boat := Layout.boat(0)
	draw_set_transform(Vector2(BOAT_X, WATER_Y + 4.0 + roundf(bob) * ZOOM), tilt, Vector2(ZOOM, ZOOM))
	draw_texture(Assets.tex("boats/boat1.png"), -boat["pivot"])
	draw_cat(boat["seat"], "sit_fish")
	var rim: float = boat["rim"]
	var hull := Assets.tex("boats/boat1.png")
	draw_texture_rect_region(hull, Rect2(-boat["pivot"].x, rim - boat["pivot"].y, hull.get_width(), hull.get_height() - rim),
		Rect2(0, rim, hull.get_width(), hull.get_height() - rim))
	draw_set_transform(Vector2.ZERO)
	# 로고: 그림이 있으면 그것을, 없으면 임시 판에 글자를 쓴다.
	var logo := Assets.tex("ui/logo.png")
	var top := 40.0 + roundf(sin(tick * 0.03) * 2.0)
	draw_texture(logo, Vector2(roundf(320.0 - logo.get_width() * 0.5), top))
	if not Assets.exists("ui/logo.png"):
		Ui.text_center(self, 320, top + 22, "고양이 낚시꾼", Pal.BARK, "large")
		Ui.text_center(self, 320, top + 58, "별주부전 낚시 이야기", Pal.WOOD)
	if Save.exists():
		Ui.label_center(self, 320, 312, "저장된 항해가 있다", Pal.CREAM)


func focus() -> Vector2:
	return Vector2(BOAT_X, WATER_Y - 40.0)
