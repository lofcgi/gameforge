class_name SpriteSheet
## assets/game/ 의 스프라이트 시트(PNG, 같은 크기 칸이 격자로 놓인 것)를 SpriteFrames 로 만든다.
## 예: SpriteSheet.make_sprite("res://assets/game/player_sheet.png", Vector2i(16, 16), {"run": [2, 3, 4, 5]})


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
	sprite.offset = Vector2(-floorf(size.x / 2), feet_y - size.y)
	return sprite
