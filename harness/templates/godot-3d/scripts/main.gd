extends Node3D
## 레벨을 세우고 규칙(목표, 위험물, 낙사)을 판정한다. 브리지에 상태와 액션을 알린다.

const SOLID_COLOR := Color(0.55, 0.58, 0.63)
const HAZARD_COLOR := Color(0.9, 0.25, 0.2)
const GOAL_COLOR := Color(0.3, 0.85, 0.45)
const CAMERA_OFFSET := Vector3(0, 6, 9)

var deaths := 0
var goal_reached := false

var _player: Player

@onready var _camera: Camera3D = $Camera
@onready var _sun: DirectionalLight3D = $Sun
@onready var _status: Label = $Hud/Status


func _ready() -> void:
	_sun.rotation_degrees = Vector3(-50, -35, 0)
	for box in Level.SOLIDS:
		add_child(Graybox.solid(box, SOLID_COLOR))
	for box in Level.HAZARDS:
		var hazard := Graybox.zone(box, HAZARD_COLOR)
		hazard.body_entered.connect(func(_body): _kill())
		add_child(hazard)
	var goal := Graybox.zone(Level.GOAL, GOAL_COLOR)
	goal.body_entered.connect(func(_body): goal_reached = true)
	add_child(goal)
	_player = Player.new()
	_player.position = Level.SPAWN
	add_child(_player)
	_follow_camera()
	GfBridge.info = {
		"dim": "3d",
		"actions": {
			"left": {"move": [-1, 0, 0]},
			"right": {"move": [1, 0, 0]},
			"forward": {"move": [0, 0, -1]},
			"back": {"move": [0, 0, 1]},
			"jump": {},
		},
		"probe": ["forward", "back", "left", "right", "jump"],
	}
	GfBridge.state_provider = _gf_state


func _physics_process(_delta: float) -> void:
	if _player.position.y < Level.KILL_Y:
		_kill()
	_follow_camera()
	_status.text = "GOAL!" if goal_reached else "deaths %d" % deaths


func _follow_camera() -> void:
	_camera.position = _player.position + CAMERA_OFFSET
	_camera.look_at(_player.position + Vector3(0, 0, -2))


## body_entered 는 물리 콜백 중에 오므로 위치 변경을 틱 끝으로 미룬다.
func _kill() -> void:
	deaths += 1
	_respawn.call_deferred()


func _respawn() -> void:
	_player.position = Level.SPAWN
	_player.velocity = Vector3.ZERO


func _gf_state() -> Dictionary:
	var pos := _player.position
	var vel := _player.velocity
	var goal: Vector3 = Level.GOAL[0]
	return {
		"level": Level.NAME,
		"player": {"pos": [pos.x, pos.y, pos.z], "vel": [vel.x, vel.y, vel.z], "on_floor": _player.is_on_floor()},
		"goal": {"pos": [goal.x, goal.y, goal.z], "reached": goal_reached},
		"deaths": deaths,
	}
