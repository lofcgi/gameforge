class_name Player
extends CharacterBody2D
## 옆에서 본 캐릭터 컨트롤러. 입력은 입력 맵 액션(left/right/jump)으로만 읽는다.

const SPEED := 90.0
const JUMP_VELOCITY := -230.0
const GRAVITY := 700.0
const SIZE := Vector2(10, 14)
const SHEET := "res://assets/game/player_sheet.png"
## `gf post sheet --name player_walk` 가 만든 SpriteFrames. 있으면 그리드 시트보다 먼저 쓴다.
const WALK := "res://assets/game/sprites/player_walk.tres"

signal jumped

var _sprite: AnimatedSprite2D


func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = SIZE
	add_child(shape)
	if ResourceLoader.exists(WALK):
		_sprite = SpriteSheet.from_frames(WALK, "run", SIZE.y / 2)
		add_child(_sprite)
	elif ResourceLoader.exists(SHEET):
		_sprite = SpriteSheet.make_sprite(SHEET, Vector2i(16, 16), {"idle": [0, 1], "run": [2, 3, 4, 5]})
		add_child(_sprite)
	else:
		add_child(Graybox.rect(Rect2(-SIZE / 2, SIZE), Color(0.95, 0.85, 0.35)))


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
		jumped.emit()
	velocity.x = Input.get_axis("left", "right") * SPEED
	move_and_slide()
	if _sprite != null:
		_animate()


func _animate() -> void:
	_sprite.play("run" if absf(velocity.x) > 1.0 else "idle")
	if velocity.x != 0.0:
		_sprite.flip_h = velocity.x < 0.0
