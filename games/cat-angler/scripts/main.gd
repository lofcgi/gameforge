extends Node2D
## 씬 관리자. 입력을 읽어 코어(Game)를 고정 틱마다 한 번 진행하고, 코어의 scene 에 맞는 화면 씬을 Stage 에 올린다.
## 브리지 등록, 전환 연출, HUD, 소리, 디버그 시작(CA_START / --start=)도 여기서 묶는다.

const ACTIONS := ["left", "right", "up", "down", "action", "cancel", "bait", "hold", "codex", "pause", "debug"]
const SCREENS := {
	"title": "title", "intro": "cutscene", "ending": "cutscene", "town": "town", "forage": "forage", "island": "island",
	"in_bait": "in_bait", "in_market": "in_market", "in_yard": "in_yard", "in_tackle": "in_tackle", "sea": "sea",
}

var game: Game
var fx := Fx.new()
var screen: Screen

var _shown := ""
var _profile := OS.get_environment("CA_PROFILE") == "1"
var _spent := {"tick": 0.0, "worst": 0.0, "n": 0}

@onready var _stage: Node2D = $Stage
@onready var _hud: Hud = $Hud/Draw
@onready var _overlay: Overlays = $Overlay/Draw
@onready var _wipe: Wipe = $Trans/Wipe
@onready var _audio: GameAudio = $Audio


func _ready() -> void:
	_configure_save()
	Assets.probe()
	# 브리지가 시드를 정한 뒤(오토로드의 _ready 뒤)에 만들어야 처음 채우는 바다가 실행마다 같다.
	game = Game.new()
	game.debug = OS.get_environment("CA_DEBUG") == "1"
	game.apply_start(_start_config())
	_hud.setup(game, fx)
	_overlay.setup(game, fx)
	var actions := {}
	for action in ACTIONS:
		actions[action] = {}
	actions["left"]["move"] = [-1, 0]
	actions["right"]["move"] = [1, 0]
	GfBridge.info = {"dim": "2d", "actions": actions, "probe": ["down", "up", "action"], "data": _bot_data(),
		"missing_assets": Assets.missing_list()}
	GfBridge.state_provider = game.snapshot
	_show_scene()


func _physics_process(_delta: float) -> void:
	var began := Time.get_ticks_usec() if _profile else 0
	var held := {}
	var pressed := {}
	for action in ACTIONS:
		held[action] = Input.is_action_pressed(action)
		pressed[action] = Input.is_action_just_pressed(action)
	game.step(held, pressed)
	if game.scene != _shown:
		_show_scene()
	fx.consume(game)
	fx.step(game)
	screen.advance()
	_hud.advance()
	_overlay.advance()
	_wipe.advance(game, screen.focus())
	_audio.consume(game, screen.owns_music())
	game.events.clear()
	if _profile:
		_profile_tick(began)


## CA_PROFILE=1: 틱 하나(코어 진행 + 화면 갱신 준비)에 든 시간의 평균과 최악을 5초마다 출력한다. 재는 값은 게임 상태에 닿지 않는다.
func _profile_tick(began: int) -> void:
	var ms := (Time.get_ticks_usec() - began) / 1000.0
	_spent["tick"] += ms
	_spent["worst"] = maxf(_spent["worst"], ms)
	_spent["n"] += 1
	if _spent["n"] == 300:
		print("PROFILE scene=%s mode=%s tick_ms=%.3f worst_ms=%.3f draw_calls=%d" % [game.scene, game.mode, _spent["tick"] / 300.0,
			_spent["worst"], Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)])
		_spent = {"tick": 0.0, "worst": 0.0, "n": 0}


func _exit_tree() -> void:
	_audio.release()
	Assets.release()
	Ui.release()


## 코어의 scene 이 바뀌었다(전환의 가운데 틱, 화면이 가려진 때): 화면 씬을 갈아 끼운다.
func _show_scene() -> void:
	if screen != null:
		_stage.remove_child(screen)
		screen.free()
	_shown = game.scene
	var packed: PackedScene = load("res://scenes/screens/%s.tscn" % SCREENS[_shown])
	screen = packed.instantiate()
	screen.setup(game, fx)
	_stage.add_child(screen)


## 저장 칸: 환경 변수 CA_SAVE (off 면 저장하지 않는다). 자동 실행에서는 기본이 off 다.
func _configure_save() -> void:
	var slot := OS.get_environment("CA_SAVE")
	if slot == "":
		slot = "off" if OS.get_cmdline_user_args().has("--gf-auto") else "save"
	Save.slot = "" if slot == "off" else slot


## 봇 정책이 균형 표와 배치를 따로 베껴 두지 않게 브리지 info 에 실어 준다(색은 뺀다).
func _bot_data() -> Dictionary:
	var strip := func(entry: Dictionary) -> Dictionary:
		var copy := entry.duplicate()
		for key in ["color", "sky", "water", "bed_color"]:
			copy.erase(key)
		return copy
	var shops := {}
	for id in Data.SHOPS:
		shops[id] = {"scene": Data.SHOPS[id]["scene"], "panel": Data.SHOPS[id]["panel"]}
	return {
		"fish": Data.FISH.map(strip), "rods": Data.RODS, "boats": Data.BOATS, "zones": Data.ZONES.map(strip),
		"places": Data.PLACES, "baits": Data.BAIT_ORDER, "x_px": Data.X_PX, "shops": shops,
		"pier_px": Sailing.left_limit(), "island_dock_px": Sailing.island_dock(), "island_px": Sea.place_x("island"),
		"town": Layout.of("places/town"), "forage": Layout.of("places/forage"), "island": Layout.of("places/island"),
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
