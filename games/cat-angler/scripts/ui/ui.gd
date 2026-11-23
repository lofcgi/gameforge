class_name Ui
## UI 그리기 도우미: 9-slice 틀, 글자, 키 표시, 게이지. 틀과 아이콘은 assets/game/ui 의 텍스처를 쓴다(없으면 임시 그림).

const SCREEN := Vector2(640, 360)
const KEY_NAMES := {"left": "←", "right": "→", "up": "↑", "down": "↓", "action": "Space", "cancel": "X", "bait": "Q",
	"hold": "H", "codex": "C", "pause": "P", "lr": "← →", "ud": "↑ ↓", "arrows": "방향키"}

static var _boxes := {}


static func release() -> void:
	_boxes.clear()


static func fs() -> int:
	return Assets.font_size()


static func line_h() -> int:
	return fs() + 4


static func box(c: CanvasItem, name: String, rect: Rect2, margin := 12, tint := Color.WHITE) -> void:
	if not _boxes.has(name):
		var style := StyleBoxTexture.new()
		style.texture = Assets.tex("ui/%s.png" % name)
		style.set_texture_margin_all(margin)
		_boxes[name] = style
	var style_box: StyleBoxTexture = _boxes[name]
	style_box.modulate_color = tint
	c.draw_style_box(style_box, Rect2(rect.position.round(), rect.size.round()))


static func width(value: String, role := "body") -> float:
	return Assets.font(role).get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, Assets.font_size(role)).x


## pos 는 글자의 왼쪽 위다. 그린 너비를 돌려준다. role: body(본문), bold(굵게), small(작게), large(크게).
static func text(c: CanvasItem, pos: Vector2, value: String, color := Pal.BARK, role := "body") -> float:
	var font := Assets.font(role)
	var size := Assets.font_size(role)
	c.draw_string(font, (pos + Vector2(0, font.get_ascent(size))).round(), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
	return width(value, role)


static func text_center(c: CanvasItem, center_x: float, y: float, value: String, color := Pal.BARK, role := "body") -> void:
	text(c, Vector2(center_x - width(value, role) * 0.5, y), value, color, role)


static func text_right(c: CanvasItem, right_x: float, y: float, value: String, color := Pal.BARK, role := "body") -> void:
	text(c, Vector2(right_x - width(value, role), y), value, color, role)


## 세계 위에 바로 얹는 글자: 굵은 글꼴에 어두운 테두리를 둘러 어떤 배경에서도 읽히게 한다.
static func label(c: CanvasItem, pos: Vector2, value: String, color := Pal.WHITE, edge := Pal.INK, role := "bold") -> void:
	for d in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1), Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
		text(c, pos + d, value, edge, role)
	text(c, pos, value, color, role)


static func label_center(c: CanvasItem, center_x: float, y: float, value: String, color := Pal.WHITE, edge := Pal.INK, role := "bold") -> void:
	label(c, Vector2(center_x - width(value, role) * 0.5, y), value, color, edge, role)


## 여러 줄 글. 줄이 너비를 넘으면 낱말 사이에서 꺾는다. chars 를 주면 그 글자 수까지만 찍는다(대사).
static func paragraph(c: CanvasItem, area: Rect2, value: String, color := Pal.BARK, chars := -1) -> void:
	var shown := value if chars < 0 else value.substr(0, chars)
	var y := area.position.y
	for raw in shown.split("\n"):
		var line := ""
		for word in raw.split(" "):
			var trial := word if line == "" else line + " " + word
			if width(trial) > area.size.x and line != "":
				text(c, Vector2(area.position.x, y), line, color)
				y += line_h()
				line = word
			else:
				line = trial
		text(c, Vector2(area.position.x, y), line, color)
		y += line_h()


static func icon(c: CanvasItem, rel: String, pos: Vector2, tint := Color.WHITE) -> void:
	c.draw_texture(Assets.tex(rel), pos.round(), tint)


## 키 모양 하나와 설명. 그린 너비를 돌려준다.
static func key(c: CanvasItem, pos: Vector2, action: String, caption: String, color := Pal.WHITE) -> float:
	var name: String = KEY_NAMES.get(action, action)
	var w := width(name) + 10.0
	box(c, "button", Rect2(pos.x, pos.y, w, fs() + 6), 8)
	text(c, pos + Vector2(5, 2), name, Pal.BARK)
	label(c, pos + Vector2(w + 4, 2), caption, color)
	return w + 4.0 + width(caption, "bold") + 12.0


static func key_width(action: String, caption: String) -> float:
	return width(KEY_NAMES.get(action, action)) + 10.0 + 4.0 + width(caption, "bold") + 12.0


## 가로 게이지: 틀 안을 frac 만큼 채운다.
static func gauge(c: CanvasItem, rect: Rect2, frac: float, color: Color) -> void:
	box(c, "gauge_frame", rect, 4)
	var inner := rect.grow(-2.0)
	var w := roundf(inner.size.x * clampf(frac, 0.0, 1.0))
	if w > 0.0:
		c.draw_texture_rect(Assets.tex("ui/gauge_fill.png"), Rect2(inner.position, Vector2(w, inner.size.y)), false, color)


## 0→1 로 가며 끝에서 살짝 넘쳤다 돌아오는 값(튀어나오는 연출).
static func pop(t: float) -> float:
	t = clampf(t, 0.0, 1.0)
	var c1 := 1.70158
	return 1.0 + (c1 + 1.0) * pow(t - 1.0, 3.0) + c1 * pow(t - 1.0, 2.0)


static func ease_out(t: float) -> float:
	t = clampf(t, 0.0, 1.0)
	return 1.0 - (1.0 - t) * (1.0 - t)


## 그림을 가운데(pivot 비율) 기준으로 놓는다. flip 이 참이면 좌우를 뒤집는다.
static func sprite(c: CanvasItem, texture: Texture2D, pos: Vector2, pivot := Vector2(0.5, 1.0), flip := false, tint := Color.WHITE) -> void:
	var size := texture.get_size()
	var corner := (pos - Vector2(size.x * pivot.x, size.y * pivot.y)).round()
	if flip:
		# 너비를 음수로 주면 같은 자리에서 좌우만 뒤집힌다.
		corner = (pos - Vector2(size.x * (1.0 - pivot.x), size.y * pivot.y)).round()
		c.draw_texture_rect(texture, Rect2(corner, Vector2(-size.x, size.y)), false, tint)
	else:
		c.draw_texture(texture, corner, tint)


## 1px 선을 픽셀 사각형으로 찍는다. 픽셀 맞춤 설정에서 draw_line 의 가는 사선은 꼭짓점이 겹쳐 사라질 때가 있다.
static func pixel_line(c: CanvasItem, from: Vector2, to: Vector2, color: Color) -> void:
	var a := from.round()
	var b := to.round()
	var d := b - a
	if absf(d.y) >= absf(d.x):
		# 세로에 가까운 선: 같은 x 가 이어지는 구간을 사각형 하나로 묶는다.
		var step := 1.0 if d.y >= 0.0 else -1.0
		var rows := int(absf(d.y)) + 1
		var run_x := a.x
		var run_from := a.y
		for i in rows:
			var y := a.y + i * step
			var x := roundf(a.x + d.x * (i / maxf(1.0, rows - 1.0)))
			if x != run_x:
				c.draw_rect(Rect2(run_x, minf(run_from, y - step), 1, absf(y - step - run_from) + 1), color)
				run_x = x
				run_from = y
		c.draw_rect(Rect2(run_x, minf(run_from, b.y), 1, absf(b.y - run_from) + 1), color)
	else:
		var step := 1.0 if d.x >= 0.0 else -1.0
		var cols := int(absf(d.x)) + 1
		var run_y := a.y
		var run_from := a.x
		for i in cols:
			var x := a.x + i * step
			var y := roundf(a.y + d.y * (i / maxf(1.0, cols - 1.0)))
			if y != run_y:
				c.draw_rect(Rect2(minf(run_from, x - step), run_y, absf(x - step - run_from) + 1, 1), color)
				run_y = y
				run_from = x
		c.draw_rect(Rect2(minf(run_from, b.x), run_y, absf(b.x - run_from) + 1, 1), color)
