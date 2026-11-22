class_name Player
extends CharacterBody3D
## 3인칭 캐릭터 컨트롤러. 이동은 월드 축 기준(forward = -z)이고 입력은 입력 맵 액션으로만 읽는다.
## assets/game/models/player.glb 가 있으면 캡슐 대신 그 모델을 쓴다 (원점은 발밑, 모델의 정면은 +Z, 1 단위 = 1 m).
## 모델의 정면(+Z)이 이동 방향을 보도록 _visual 을 돌린다. 방향 규약은 하네스의 templates/README.md 7절.

const SPEED := 5.0
const JUMP_VELOCITY := 7.0
const GRAVITY := 18.0
const HEIGHT := 1.8
const RADIUS := 0.4
const MODEL := "res://assets/game/models/player.glb"

var _visual: Node3D
var _walk: AnimationPlayer


func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	var shape := CollisionShape3D.new()
	shape.shape = CapsuleShape3D.new()
	shape.shape.height = HEIGHT
	shape.shape.radius = RADIUS
	add_child(shape)
	_visual = _make_visual()
	_visual.rotation.y = _yaw(Vector2(0, -1))
	add_child(_visual)


func _make_visual() -> Node3D:
	if ResourceLoader.exists(MODEL):
		var model: Node3D = load(MODEL).instantiate()
		model.position.y = -HEIGHT / 2
		_walk = _find_walk(model)
		return model
	var mesh := MeshInstance3D.new()
	mesh.mesh = CapsuleMesh.new()
	mesh.mesh.height = HEIGHT
	mesh.mesh.radius = RADIUS
	mesh.material_override = Graybox.material(Color(0.95, 0.8, 0.3))
	return mesh


## 리깅된 모델(gf gen rig 의 걷기 GLB)이면 첫 애니메이션을 걷기로 쓴다. 고정 틱에 맞춰 돌려 캡처가 재현된다.
func _find_walk(model: Node) -> AnimationPlayer:
	var found := model.find_children("*", "AnimationPlayer")
	if found.is_empty():
		return null
	var player: AnimationPlayer = found[0]
	var names := player.get_animation_list()
	if names.is_empty():
		return null
	player.get_animation(names[0]).loop_mode = Animation.LOOP_LINEAR
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS
	player.play(names[0])
	player.pause()
	return player


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
	var direction := Input.get_vector("left", "right", "forward", "back")
	velocity.x = direction.x * SPEED
	velocity.z = direction.y * SPEED
	move_and_slide()
	if direction != Vector2.ZERO:
		_visual.rotation.y = _yaw(direction)
	if _walk != null:
		if direction != Vector2.ZERO and is_on_floor():
			_walk.play()
		else:
			_walk.pause()


## 모델의 정면(+Z)이 수평 방향 (x, z) 를 보게 하는 y 회전.
static func _yaw(direction: Vector2) -> float:
	return atan2(direction.x, direction.y)
