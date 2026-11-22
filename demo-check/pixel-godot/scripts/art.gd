class_name Art
## 그레이박스 도형 위에 올리는 그림. 충돌과 규칙은 Graybox 노드가 그대로 맡고, 여기서는 보이는 것만 바꾼다.

const GROUND := "res://assets/game/sprites/ground.png"
const SPIKES := "res://assets/game/sprites/spikes.png"
const LANTERN := "res://assets/game/sprites/lantern.png"
const TILE := 16


## 바닥 타일(32x32: 위 절반은 이끼, 아래 절반은 돌)을 상자 크기에 맞게 깐다. 이끼는 맨 윗줄에만 온다.
static func ground(size: Vector2) -> Node2D:
	var image: Image = load(GROUND).get_image()
	var top := ImageTexture.create_from_image(image.get_region(Rect2i(0, 0, 32, TILE)))
	var fill := ImageTexture.create_from_image(image.get_region(Rect2i(0, TILE, 32, TILE)))
	var root := Node2D.new()
	root.add_child(_strip(top, Rect2(-size / 2, Vector2(size.x, minf(TILE, size.y)))))
	if size.y > TILE:
		root.add_child(_strip(fill, Rect2(-size.x / 2, -size.y / 2 + TILE, size.x, size.y - TILE)))
	return root


static func _strip(texture: Texture2D, area: Rect2) -> TextureRect:
	var node := TextureRect.new()
	node.texture = texture
	node.stretch_mode = TextureRect.STRETCH_TILE
	node.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	node.position = area.position
	node.size = area.size
	node.clip_contents = true
	return node


## 그림의 아래 가운데가 상자의 아래 가운데에 오게 놓는다.
static func standing(path: String, box: Vector2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.centered = false
	var size := sprite.texture.get_size()
	sprite.position = Vector2(-floorf(size.x / 2), box.y / 2 - size.y)
	return sprite


## 먼 배경: 밤하늘 띠와 기둥 실루엣. 전경보다 어둡고 차갑게 둔다.
static func backdrop(width: float) -> Node2D:
	var root := Node2D.new()
	root.z_index = -10
	root.add_child(Graybox.rect(Rect2(-320, 0, width + 640, 180), Color("1a1c2c")))
	root.add_child(Graybox.rect(Rect2(-320, 96, width + 640, 84), Color("202a44")))
	for x in range(40, int(width), 112):
		var tall := 70 + (x * 7) % 40
		root.add_child(Graybox.rect(Rect2(x, 156 - tall, 18, tall), Color("29366f")))
		root.add_child(Graybox.rect(Rect2(x - 3, 156 - tall, 24, 5), Color("333c57")))
	return root
