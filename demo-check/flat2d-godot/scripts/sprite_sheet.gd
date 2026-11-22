class_name SpriteSheet
## assets/game/ 의 그림을 노드로 만든다. 좌표와 크기는 모두 레벨 단위(기준 해상도 320x180)다.
## 그림 픽셀 ÷ 단위당 픽셀(project.godot 의 gameforge/art/pixels_per_unit: 픽셀 아트 1, 고해상도 2D 4) = 화면에서의 크기.
## 예: SpriteSheet.make_sprite("res://assets/game/player_sheet.png", Vector2i(16, 16), {"run": [2, 3, 4, 5]})


static func pixels_per_unit() -> float:
	return float(ProjectSettings.get_setting("gameforge/art/pixels_per_unit", 1))


static func load_frames(path: String, cell: Vector2i, animations: Dictionary, fps := 8.0) -> SpriteFrames:
	var sheet: Texture2D = load(path)
	var columns: int = sheet.get_width() / cell.x
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	for animation in animations:
		frames.add_animation(animation)
		frames.set_animation_speed(animation, fps)
		for index in animations[animation]:
			var atlas := AtlasTexture.new()
			atlas.atlas = sheet
			atlas.region = Rect2(Vector2(index % columns, index / columns) * Vector2(cell), cell)
			frames.add_frame(animation, atlas)
	return frames


static func make_sprite(path: String, cell: Vector2i, animations: Dictionary) -> AnimatedSprite2D:
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames = load_frames(path, cell, animations)
	sprite.scale = Vector2.ONE / pixels_per_unit()
	return sprite


## `gf post sheet` 가 만든 SpriteFrames(.tres)를 불러온다. 그 안의 애니메이션 하나를 move 라는 이름으로 쓰고,
## 첫 프레임을 "idle" 로 둔다. 프레임의 아래 가운데(발)가 노드 원점에서 feet_y 만큼 아래에 오게 놓는다
## (post align 이 발 기준선을 프레임 바닥에 맞춰 두었다).
static func from_frames(path: String, move: String, feet_y: float) -> AnimatedSprite2D:
	var frames: SpriteFrames = load(path).duplicate()
	var source := frames.get_animation_names()[0]
	if source != move:
		frames.rename_animation(source, move)
	frames.add_animation("idle")
	frames.add_frame("idle", frames.get_frame_texture(move, 0))
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.centered = false
	var size := frames.get_frame_texture(move, 0).get_size()
	var ppu := pixels_per_unit()
	sprite.scale = Vector2.ONE / ppu
	sprite.offset = Vector2(-floorf(size.x / 2), feet_y * ppu - size.y)
	return sprite


## 정지 그림 한 장을, 아래 가운데가 box(레벨 단위)의 아래 가운데에 오게 놓는다. box 의 중심이 부모의 원점이다.
## 그림이 상자보다 커도 늘리지 않는다(판정 상자와 보이는 크기는 따로다).
static func standing(path: String, box: Vector2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.centered = false
	var size := sprite.texture.get_size()
	var ppu := pixels_per_unit()
	sprite.scale = Vector2.ONE / ppu
	sprite.offset = Vector2(-floorf(size.x / 2), box.y / 2 * ppu - size.y)
	return sprite


## 그림(또는 그 일부 source: 그림 픽셀)을 area(레벨 단위, 부모 기준)에 늘리지 않고 반복해서 깐다. 넘치는 부분은 잘린다.
## 예: 위 절반은 풀, 아래 절반은 흙인 타일이면 맨 윗줄에 위 절반을, 그 아래에 아래 절반을 깐다.
static func tiled(path: String, area: Rect2, source := Rect2i()) -> TextureRect:
	var image: Image = load(path).get_image()
	if source.has_area():
		image = image.get_region(source)
	var node := TextureRect.new()
	var ppu := pixels_per_unit()
	node.texture = ImageTexture.create_from_image(image)
	node.stretch_mode = TextureRect.STRETCH_TILE
	node.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	node.position = area.position
	node.size = area.size * ppu
	node.scale = Vector2.ONE / ppu
	node.clip_contents = true
	return node
