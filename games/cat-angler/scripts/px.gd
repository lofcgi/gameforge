class_name Px
## Image 에 도형을 찍는 작은 도구. 임시 그림(Placeholder)을 만들 때만 쓴다. 안티에일리어싱이 없다.


static func blank(w: int, h: int, color := Color(0, 0, 0, 0)) -> Image:
	var image := Image.create(w, h, false, Image.FORMAT_RGBA8)
	image.fill(color)
	return image


static func rect(image: Image, x: int, y: int, w: int, h: int, color: Color) -> void:
	var area := Rect2i(x, y, w, h).intersection(Rect2i(0, 0, image.get_width(), image.get_height()))
	if area.has_area():
		image.fill_rect(area, color)


## 테두리가 있는 사각형.
static func box(image: Image, x: int, y: int, w: int, h: int, fill: Color, edge: Color) -> void:
	rect(image, x, y, w, h, edge)
	rect(image, x + 1, y + 1, w - 2, h - 2, fill)


static func dot(image: Image, x: int, y: int, color: Color) -> void:
	if x >= 0 and y >= 0 and x < image.get_width() and y < image.get_height():
		image.set_pixel(x, y, color)


## 가운데 (cx, cy), 반지름 (rx, ry) 의 채운 타원. edge 를 주면 1px 테두리를 두른다.
static func oval(image: Image, cx: float, cy: float, rx: float, ry: float, fill: Color, edge := Color(0, 0, 0, 0)) -> void:
	if rx <= 0.0 or ry <= 0.0:
		return
	for y in range(int(floorf(cy - ry)), int(ceilf(cy + ry)) + 1):
		var dy := (y + 0.5 - cy) / ry
		if absf(dy) > 1.0:
			continue
		var half := rx * sqrt(1.0 - dy * dy)
		var from := int(roundf(cx - half))
		var to := int(roundf(cx + half))
		rect(image, from, y, to - from, 1, fill)
		if edge.a > 0.0:
			var dy_in := (y + 0.5 - cy) / maxf(0.5, ry - 1.0)
			var inner := (rx - 1.0) * sqrt(maxf(0.0, 1.0 - dy_in * dy_in)) if absf(dy_in) < 1.0 else 0.0
			var gap := maxi(1, int(roundf(half - inner)))
			rect(image, from, y, mini(gap, to - from), 1, edge)
			rect(image, maxi(from, to - gap), y, mini(gap, to - from), 1, edge)


## 볼록 다각형을 채운다(가로줄마다 양 끝을 찾는다).
static func poly(image: Image, points: Array, fill: Color) -> void:
	var top := INF
	var bottom := -INF
	for p in points:
		top = minf(top, p.y)
		bottom = maxf(bottom, p.y)
	for y in range(int(floorf(top)), int(ceilf(bottom))):
		var left := INF
		var right := -INF
		var sy := y + 0.5
		for i in points.size():
			var a: Vector2 = points[i]
			var b: Vector2 = points[(i + 1) % points.size()]
			if (a.y <= sy and b.y > sy) or (b.y <= sy and a.y > sy):
				var x := a.x + (sy - a.y) / (b.y - a.y) * (b.x - a.x)
				left = minf(left, x)
				right = maxf(right, x)
		if right >= left:
			rect(image, int(roundf(left)), y, maxi(1, int(roundf(right)) - int(roundf(left))), 1, fill)


static func line(image: Image, from: Vector2, to: Vector2, color: Color, width := 1) -> void:
	var steps := int(maxf(absf(to.x - from.x), absf(to.y - from.y))) + 1
	for i in steps + 1:
		var p := from.lerp(to, i / float(steps))
		rect(image, int(roundf(p.x)), int(roundf(p.y)), width, width, color)


## 두 색을 격자 무늬로 섞은 띠(그라데이션 대신 쓴다).
static func dither(image: Image, x: int, y: int, w: int, h: int, color: Color) -> void:
	for py in range(y, y + h):
		for px in range(x + (py % 2), x + w, 2):
			dot(image, px, py, color)


## 불투명한 픽셀의 바깥 둘레에 1px 테두리를 두른다.
static func outline(image: Image, color: Color) -> void:
	var w := image.get_width()
	var h := image.get_height()
	var source := image.duplicate()
	for y in h:
		for x in w:
			if source.get_pixel(x, y).a > 0.0:
				continue
			for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var nx: int = x + d.x
				var ny: int = y + d.y
				if nx >= 0 and ny >= 0 and nx < w and ny < h and source.get_pixel(nx, ny).a > 0.0:
					image.set_pixel(x, y, color)
					break
