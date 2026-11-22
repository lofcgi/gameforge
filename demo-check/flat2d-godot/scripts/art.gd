class_name Art
## 그레이박스 도형 위에 올리는 그림. 충돌과 규칙은 Graybox 노드가 그대로 맡고, 여기서는 보이는 것만 바꾼다.

const GROUND := "res://assets/game/sprites/ground.png"
const BRAMBLE := "res://assets/game/sprites/bramble.png"
const ACORN := "res://assets/game/sprites/acorn.png"
## 바닥 타일(128x128 px = 32 단위)의 위 절반은 풀, 아래 절반은 흙이다.
const TOP := Rect2i(0, 0, 128, 64)
const FILL := Rect2i(0, 64, 128, 64)
const TOP_UNITS := 16.0


## 풀은 맨 윗줄에만 깔고 그 아래는 흙으로 채운다.
static func ground(size: Vector2) -> Node2D:
	var root := Node2D.new()
	root.add_child(SpriteSheet.tiled(GROUND, Rect2(-size / 2, Vector2(size.x, minf(TOP_UNITS, size.y))), TOP))
	if size.y > TOP_UNITS:
		root.add_child(SpriteSheet.tiled(GROUND, Rect2(-size.x / 2, -size.y / 2 + TOP_UNITS, size.x, size.y - TOP_UNITS), FILL))
	return root


## 먼 배경: 낮 하늘과 겹친 언덕. 전경보다 옅고 채도가 낮다.
static func backdrop(width: float) -> Node2D:
	var root := Node2D.new()
	root.z_index = -10
	root.add_child(Graybox.rect(Rect2(-320, -180, width + 640, 540), Color("bfe3ee")))
	root.add_child(Graybox.rect(Rect2(-320, 110, width + 640, 250), Color("a9d8c9")))
	for x in range(-40, int(width) + 80, 150):
		root.add_child(_hill(Vector2(x, 150), 95, Color("9fd2b4")))
		root.add_child(_hill(Vector2(x + 75, 168), 80, Color("8cc7a2")))
	return root


static func _hill(centre: Vector2, radius: float, color: Color) -> Polygon2D:
	var hill := Polygon2D.new()
	var points := PackedVector2Array()
	for step in 33:
		var angle := PI + PI * step / 32.0
		points.append(centre + Vector2(cos(angle) * radius, sin(angle) * radius * 0.6))
	hill.polygon = points
	hill.color = color
	return hill
