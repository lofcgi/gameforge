extends Node2D
## 입력을 읽어 코어(Game)를 고정 틱마다 한 번 진행하고, 화면과 브리지에 상태를 넘긴다.

const ACTIONS := ["left", "right", "up", "down", "action", "cancel", "bait", "hold", "codex"]

var game: Game

@onready var _world: WorldView = $World
@onready var _hud: Hud = $Hud/Draw


func _ready() -> void:
	# 브리지가 시드를 정한 뒤(오토로드의 _ready 뒤)에 만들어야 처음 채우는 바다가 실행마다 같다.
	game = Game.new()
	game.apply_start(_start_config())
	_world.game = game
	_hud.game = game
	_hud.world = _world
	var actions := {}
	for action in ACTIONS:
		actions[action] = {}
	actions["left"]["move"] = [-1, 0]
	actions["right"]["move"] = [1, 0]
	GfBridge.info = {"dim": "2d", "actions": actions, "probe": ["cancel", "right", "left", "action"], "data": _bot_data()}
	GfBridge.state_provider = game.snapshot


func _physics_process(_delta: float) -> void:
	var held := {}
	var pressed := {}
	for action in ACTIONS:
		held[action] = Input.is_action_pressed(action)
		pressed[action] = Input.is_action_just_pressed(action)
	game.step(held, pressed)
	_world.advance()
	_hud.advance()
	game.events.clear()


## 봇 정책이 균형 표를 따로 베껴 두지 않게 브리지 info 에 실어 준다(색은 뺀다).
func _bot_data() -> Dictionary:
	var strip := func(entry: Dictionary) -> Dictionary:
		var copy := entry.duplicate()
		for key in ["color", "sky", "water", "bed_color"]:
			copy.erase(key)
		return copy
	return {
		"fish": Data.FISH.map(strip), "rods": Data.RODS, "boats": Data.BOATS, "zones": Data.ZONES.map(strip),
		"places": Data.PLACES, "stations": Data.STATIONS, "baits": Data.BAIT_ORDER, "x_px": Data.X_PX,
		"pier_px": Sailing.left_limit(), "island_dock_px": Sailing.island_dock(), "island_px": Sea.place_x("island"),
		"island_stations": Data.ISLAND_STATIONS,
	}


## 디버그 시작: 실행 인자 `-- --start=coins=500,rod=2` 또는 환경 변수 CA_START (gf engine 명령은 인자를 넘기지 못한다).
func _start_config() -> Dictionary:
	var text := OS.get_environment("CA_START")
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--start="):
			text = arg.trim_prefix("--start=")
	var config := {}
	for pair in text.split(",", false):
		var parts := pair.split("=", true, 1)
		config[parts[0]] = parts[1] if parts.size() > 1 else "1"
	return config
