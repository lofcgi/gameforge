extends Node2D
## 레벨을 세우고 규칙(목표, 위험물, 낙사)을 판정한다. 브리지에 상태와 액션을 알린다.

const SOLID_COLOR := Color(0.42, 0.45, 0.52)
const HAZARD_COLOR := Color(0.9, 0.25, 0.2)
const GOAL_COLOR := Color(0.3, 0.85, 0.45)

var deaths := 0
var goal_reached := false

var _player: Player

@onready var _camera: Camera2D = $Camera
@onready var _status: Label = $Hud/Status


func _ready() -> void:
	for area in Level.SOLIDS:
		add_child(Graybox.solid(area, SOLID_COLOR))
	for area in Level.HAZARDS:
		var hazard := Graybox.zone(area, HAZARD_COLOR)
		hazard.body_entered.connect(func(_body): _kill())
		add_child(hazard)
	var goal := Graybox.zone(Level.GOAL, GOAL_COLOR)
	goal.body_entered.connect(func(_body): goal_reached = true)
	add_child(goal)
	_player = Player.new()
	_player.position = Level.SPAWN
	add_child(_player)
	_camera.limit_left = 0
	_camera.limit_right = Level.WIDTH
	_camera.limit_top = 0
	_camera.limit_bottom = 180
	GfBridge.info = {
		"dim": "2d",
		"actions": {"left": {"move": [-1, 0]}, "right": {"move": [1, 0]}, "jump": {}},
		"probe": ["right", "left", "jump"],
	}
	GfBridge.state_provider = _gf_state


func _physics_process(_delta: float) -> void:
	if _player.position.y > Level.KILL_Y:
		_kill()
	_camera.position = _player.position
	_status.text = "GOAL!" if goal_reached else "deaths %d" % deaths


## body_entered 는 물리 콜백 중에 오므로 위치 변경을 틱 끝으로 미룬다.
func _kill() -> void:
	deaths += 1
	_respawn.call_deferred()


func _respawn() -> void:
	_player.position = Level.SPAWN
	_player.velocity = Vector2.ZERO


func _gf_state() -> Dictionary:
	return {
		"level": Level.NAME,
		"player": {
			"pos": [_player.position.x, _player.position.y],
			"vel": [_player.velocity.x, _player.velocity.y],
			"on_floor": _player.is_on_floor(),
		},
		"goal": {"pos": [Level.GOAL.get_center().x, Level.GOAL.get_center().y], "reached": goal_reached},
		"deaths": deaths,
	}
