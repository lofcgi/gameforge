extends Node
## gameforge 브리지. `gf engine ...` 명령이 게임을 조종하고 관찰하는 유일한 통로다.
## 계약은 templates/README.md 에 있다. 이 파일은 godot-2d 와 godot-3d 에서 같은 내용이어야 한다.
##
## 게임 쪽에서 할 일은 두 가지다.
##   GfBridge.info = {"actions": {...}, "probe": [...]}
##   GfBridge.state_provider = func() -> Dictionary
##
## `--` 뒤 인자가 없으면 아무 일도 하지 않는다.
##   --gf-port=N      하네스(127.0.0.1:N)에 접속해 JSON 줄 명령을 받는다
##   --gf-lockstep    step 명령을 받은 만큼만 물리 틱을 진행한다 (결정적 실행)
##   --gf-record=F    사람의 입력과 상태 표본을 F(jsonl)에 남긴다
##   --gf-seed=N      전역 난수 시드
##   --gf-auto        사람 대신 하네스가 입력을 넣는다. 창이 키보드를 받지 않고, 앱 포커스가 바뀌어도 넣은 입력이 유지된다
##   --gf-audio       소리 측정을 켠다 (마스터 버스의 피크·RMS 시간표, 재생이 시작된 소리 목록)

const VERSION := 1
## 하네스와 맞추는 브리지 버전. 명령이나 동작이 바뀌면 올린다 (tools/gf/engine/adapter.py 의 BRIDGE_VERSION).
const BRIDGE := 2
const SAMPLE_TICKS := 6
const COMMAND_TIMEOUT_MS := 30000
const FOCUS_QUIET_MS := 150
const FOCUS_SETTLE_MAX_MS := 1500
const AUDIO_BIN_MS := 100
const AUDIO_FLOOR_DB := -200.0
## 이보다 작은 표본(-80 dBFS)이 이어지면 끊김으로 센다.
const AUDIO_SILENT_LEVEL := 0.0001
const AUDIO_PLAYER_CLASSES := ["AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D"]

var info: Dictionary = {}
var state_provider: Callable
var seed_value := 0

var _args: Dictionary = {}
var _peer: StreamPeerTCP
var _buffer := ""
var _lockstep := false
var _step_target := -1
var _tick := 0
var _greeted := false
var _record: FileAccess
var _perf_on := false
var _frame_ms: Array[float] = []
var _last_frame_usec := 0
var _auto := false
## 하네스가 눌러 둔 키 (물리 키코드 → 누름 이벤트). --gf-auto 에서만 쓴다.
var _held: Dictionary = {}
var _app_active := true
var _focus_changed_ms := 0
var _pinning := false
## 기록 중에 사람이 누르고 있는 키 (물리 키 이름 → 기록한 항목).
var _recorded_keys: Dictionary = {}
var _audio_on := false
var _capture: AudioEffectCapture
var _audio_start_ms := 0
var _audio_timeline: Array = []
var _audio_events: Array = []
var _audio_players: Dictionary = {}
var _bin_start_ms := -1
var _bin_peak := 0.0
var _bin_square_sum := 0.0
var _bin_frames := 0
var _bin_quiet_frames := 0
var _bin_bus_peak: Dictionary = {}
var _quiet_run := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = -1000
	# _process 는 게임의 모든 _process 뒤에 돈다. 거기서 멈춰 명령을 받는다(_serve_lockstep 의 설명).
	process_priority = 1000
	_args = _parse_args(OS.get_cmdline_user_args())
	if _args.is_empty():
		set_process(false)
		set_physics_process(false)
		set_process_input(false)
		return
	if _args.has("seed"):
		seed_value = int(_args["seed"])
		seed(seed_value)
	_lockstep = _args.has("lockstep")
	_auto = _args.has("auto")
	if _auto:
		# 자동 실행 중에 사용자가 치는 키가 게임에 섞여 들어가 결과를 바꾸지 않게 한다.
		get_window().unfocusable = true
		# 이 스크립트의 _ready 보다 먼저 포커스를 잃었을 수 있다.
		if not _app_active:
			_pin_focus()
	if _args.has("audio"):
		_start_audio_probe()
	if _args.has("port"):
		_connect(int(_args["port"]))
	set_process_input(_args.has("record"))


func _parse_args(raw: PackedStringArray) -> Dictionary:
	var parsed := {}
	for arg in raw:
		if not arg.begins_with("--gf-"):
			continue
		var pair := arg.trim_prefix("--gf-").split("=", true, 1)
		parsed[pair[0]] = pair[1] if pair.size() > 1 else ""
	return parsed


func _connect(port: int) -> void:
	_peer = StreamPeerTCP.new()
	var err := _peer.connect_to_host("127.0.0.1", port)
	var give_up := Time.get_ticks_msec() + 5000
	while err == OK and _peer.get_status() == StreamPeerTCP.STATUS_CONNECTING:
		_peer.poll()
		if Time.get_ticks_msec() > give_up:
			break
		OS.delay_msec(1)
	if _peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		_abort("하네스 포트 %d 에 접속하지 못했다" % port)
	_peer.set_no_delay(true)


func _abort(message: String) -> void:
	push_error("GfBridge: " + message)
	get_tree().quit(1)


func _physics_process(_delta: float) -> void:
	if not _greeted:
		_greet()
	if _record != null and _tick % SAMPLE_TICKS == 0:
		_write_record({"type": "state", "tick": _tick, "t": _time(), "state": state()})
	if _audio_on:
		_scan_audio_players()
	# 첫 틱 전(목표 없음)과, 한 프레임에 물리 틱이 두 번 돌아 목표를 지나치려는 때에만 여기서 멈춘다.
	if _peer != null and _lockstep and (_step_target < 0 or _tick >= _step_target):
		_serve_lockstep()
	_tick += 1


func _process(_delta: float) -> void:
	if _peer != null and _greeted:
		if _lockstep:
			_serve_lockstep()
		else:
			_serve_live()
	if _audio_on:
		_sample_audio()
	if not _perf_on:
		return
	var now := Time.get_ticks_usec()
	if _last_frame_usec > 0:
		_frame_ms.append((now - _last_frame_usec) / 1000.0)
	_last_frame_usec = now


## 첫 물리 틱에 인사한다. 이때는 메인 씬의 _ready 가 끝나 info 와 state_provider 가 채워져 있다.
func _greet() -> void:
	_greeted = true
	if not state_provider.is_valid():
		_abort("state_provider 가 설정되지 않았다. 메인 씬의 _ready 에서 GfBridge.state_provider 를 지정한다.")
		return
	if _args.has("record"):
		_open_record(_args["record"])
	if _auto:
		_wait_focus(FOCUS_SETTLE_MAX_MS, false)
	if _peer != null:
		_send({"hello": VERSION, "bridge": BRIDGE, "header": _header()})


func _header() -> Dictionary:
	var size := get_window().size
	return {
		"type": "header",
		"version": VERSION,
		"engine": "godot",
		"tick_rate": Engine.physics_ticks_per_second,
		"seed": seed_value,
		"size": [size.x, size.y],
		"info": _info_with_keys(),
	}


## 액션마다 입력 맵의 키 이름(물리 키)을 붙인다. 하네스가 OS 키 이벤트를 보낼 때 쓴다.
func _info_with_keys() -> Dictionary:
	var described := info.duplicate(true)
	for action in described.get("actions", {}):
		if described["actions"][action].has("keys") or not InputMap.has_action(action):
			continue
		var keys := []
		for event in InputMap.action_get_events(action):
			if event is InputEventKey:
				keys.append(OS.get_keycode_string(event.physical_keycode if event.physical_keycode != KEY_NONE else event.keycode))
		described["actions"][action]["keys"] = keys
	return described


func _time() -> float:
	return float(_tick) / Engine.physics_ticks_per_second


func state() -> Dictionary:
	var snapshot: Dictionary = state_provider.call()
	snapshot["tick"] = _tick
	snapshot["t"] = _time()
	snapshot["fps"] = Engine.get_frames_per_second()
	return snapshot


# --- 명령 처리 ---


## lockstep: 목표 틱까지 왔으면 상태를 돌려주고, 다음 step 명령이 올 때까지 멈춰서 명령을 처리한다.
##
## 멈추는 자리는 물리 틱 안이 아니라 프레임의 _process 끝이다. Godot 은 입력이 들어온 "다음" 물리 틱에
## is_action_just_pressed 를 참으로 만든다(물리 틱 안에서 넣은 입력은 그 틱에 is_action_pressed 만 참이 되고
## just_pressed 는 한 틱 늦는다). 사람의 키는 틱과 틱 사이에 도착하므로, 주입도 틱 사이에 해야 눌림과 "방금 눌림"이
## 사람이 누를 때와 같은 틱에 보인다. 실측: 물리 틱 안에서 넣던 때에는 OS 키로 기록한 플레이를 재생하면 점프가
## 매번 한 틱 늦었다. 첫 틱 전에 보낸 입력만은 물리 틱 안에서 들어가 just_pressed 가 한 틱 늦다.
func _serve_lockstep() -> void:
	if _tick < _step_target:
		return
	if _step_target >= 0:
		_send({"ok": true, "state": state()})
		_step_target = -1
	var waited_since := Time.get_ticks_msec()
	while _step_target < 0:
		var line := _read_line()
		if line == "":
			if Time.get_ticks_msec() - waited_since > COMMAND_TIMEOUT_MS:
				_abort("하네스 명령이 %d ms 동안 오지 않았다" % COMMAND_TIMEOUT_MS)
				return
			OS.delay_usec(200)
			continue
		waited_since = Time.get_ticks_msec()
		if not _handle(line):
			return


func _serve_live() -> void:
	var line := _read_line()
	while line != "":
		if not _handle(line):
			return
		line = _read_line()


func _read_line() -> String:
	_peer.poll()
	if _peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		_peer = null
		_step_target = 0
		get_tree().quit()
		return ""
	var available := _peer.get_available_bytes()
	if available > 0:
		_buffer += _peer.get_utf8_string(available)
	var end := _buffer.find("\n")
	if end < 0:
		return ""
	var line := _buffer.substr(0, end)
	_buffer = _buffer.substr(end + 1)
	return line


func _send(message: Dictionary) -> void:
	_peer.put_data((JSON.stringify(message) + "\n").to_utf8_buffer())


## 처리 후 계속 명령을 읽어도 되면 true.
func _handle(line: String) -> bool:
	var message = JSON.parse_string(line)
	if typeof(message) != TYPE_DICTIONARY:
		_send({"ok": false, "error": "JSON 객체가 아니다: " + line})
		return true
	match message.get("cmd", ""):
		"step":
			if not _lockstep:
				_send({"ok": false, "error": "step 은 --gf-lockstep 에서만 쓴다"})
				return true
			_step_target = _tick + int(message["n"])
			return false
		"state":
			_send({"ok": true, "state": state()})
		"action":
			_send(_inject_action(message["name"], message["down"]))
		"input":
			_send(_inject_raw(message))
		"screenshot":
			_send(_screenshot(message["path"]))
		"yield_focus":
			_wait_focus(int(message.get("wait_ms", 1000)), true)
			_send({"ok": true, "app_active": _app_active})
		"audio":
			_send(_audio_report())
		"perf_start":
			_frame_ms.clear()
			_last_frame_usec = 0
			_perf_on = true
			_send({"ok": true})
		"perf_stop":
			_perf_on = false
			_send({"ok": true, "frame_ms": _frame_ms, "counters": _perf_counters()})
		"quit":
			_send({"ok": true})
			_peer = null
			_step_target = 0
			get_tree().quit()
			return false
		_:
			_send({"ok": false, "error": "모르는 명령: " + str(message.get("cmd"))})
	return true


# --- 입력 주입: 사람의 키와 같은 경로(Input → InputMap → _input)를 탄다 ---


func _inject_action(action: String, down: bool) -> Dictionary:
	if not InputMap.has_action(action):
		return {"ok": false, "error": "입력 맵에 없는 액션: " + action}
	for event in InputMap.action_get_events(action):
		if event is InputEventKey:
			var key: InputEventKey = event.duplicate()
			key.pressed = down
			_dispatch(key)
			return {"ok": true}
	return {"ok": false, "error": "액션 %s 에 키 이벤트가 없다" % action}


func _inject_raw(message: Dictionary) -> Dictionary:
	var down: bool = message["down"]
	match message.get("device", ""):
		"key":
			var code := OS.find_keycode_from_string(message["code"])
			if code == KEY_NONE:
				return {"ok": false, "error": "모르는 키: " + str(message["code"])}
			var key := InputEventKey.new()
			key.physical_keycode = code
			key.keycode = code
			key.pressed = down
			_dispatch(key)
		"mouse":
			var button := InputEventMouseButton.new()
			button.button_index = int(message["code"])
			button.position = Vector2(message["pos"][0], message["pos"][1])
			button.global_position = button.position
			button.pressed = down
			_dispatch(button)
		"joy":
			var pad := InputEventJoypadButton.new()
			pad.button_index = int(message["code"])
			pad.pressed = down
			_dispatch(pad)
		_:
			return {"ok": false, "error": "모르는 입력 장치: " + str(message.get("device"))}
	return {"ok": true}


func _dispatch(event: InputEvent) -> void:
	if _auto and event is InputEventKey:
		if event.pressed:
			_held[event.physical_keycode] = event
		else:
			_held.erase(event.physical_keycode)
	Input.parse_input_event(event)
	Input.flush_buffered_events()


# --- 앱 포커스 (--gf-auto) ---
#
# Godot 은 앱이 포커스를 잃으면(NOTIFICATION_APPLICATION_FOCUS_OUT) Input.release_pressed_events() 로 눌린 키와
# 액션을 전부 뗀다(scene_tree.cpp). Input.parse_input_event 로 넣은 키도 같은 상태에 들어 있어 함께 풀린다.
# 실측한 포커스 상실 두 가지:
#   1. 터미널에서 실행한 Godot 은 창을 띄운 직후 스스로 포커스를 내줬다가 되찾는다(macOS 의
#      forceUnbundledWindowActivationHack: 약 60ms 에 걸쳐 FOCUS_IN → OUT → IN). lockstep 은 틱 사이에만 OS 이벤트를
#      처리하므로 이 OUT 이 몇 번째 틱에 올지는 하네스가 얼마나 빨리 틱을 넘기느냐에 달려 있었다.
#   2. 실행 도중 사용자가 다른 창을 누르거나 다른 앱이 뜨면 그 틱에 OUT 이 온다.
# 대응: 인사 전에 1번이 끝나기를 기다리고, 하네스가 원래 앞에 있던 앱을 다시 활성화해 Godot 을 일부러 비활성으로
# 만든다(yield_focus). 비활성인 앱은 더 잃을 포커스가 없다. OUT 을 받으면 곧바로 트리에 FOCUS_IN 을 한 번 보내
# Input 의 application_focused 를 참으로 되돌린다. 이 값이 거짓인 동안에는 창 이동·최소화만으로도 키가 풀리기 때문이다.
# 그래도 누가 Godot 창을 직접 활성화했다가 떠나면 OUT 이 한 번 더 온다. 그때는 풀린 키를 다시 누르고 오류로 남긴다
# (그 틱에 is_action_just_pressed 가 한 번 더 참이 될 수 있어 실행이 원본과 달라질 수 있다).


func _notification(what: int) -> void:
	if _pinning:
		return
	if what == NOTIFICATION_APPLICATION_FOCUS_IN:
		_app_active = true
		_focus_changed_ms = Time.get_ticks_msec()
	elif what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_app_active = false
		_focus_changed_ms = Time.get_ticks_msec()
		if _auto and is_inside_tree():
			_pin_focus()
			_restore_held()
		elif _record != null:
			_record_focus_release()


## 사람이 키를 누른 채 다른 창으로 가면 Godot 이 그 키를 떼지만 키를 뗐다는 이벤트는 오지 않는다.
## 기록에 뗌을 남겨야 재생이 원본처럼 멈춘다(실측: 남기지 않던 때에는 재생이 계속 걸어가 위치가 200 단위 넘게 벌어졌다).
func _record_focus_release() -> void:
	for code in _recorded_keys:
		var entry: Dictionary = _recorded_keys[code].duplicate()
		entry.merge({"tick": _tick, "t": _time(), "down": false, "cause": "focus_out"}, true)
		_write_record(entry)
	_recorded_keys.clear()


func _pin_focus() -> void:
	_pinning = true
	get_tree().notification(NOTIFICATION_APPLICATION_FOCUS_IN)
	_pinning = false


func _restore_held() -> void:
	var lost: PackedStringArray = []
	for code in _held:
		if not Input.is_physical_key_pressed(code):
			lost.append(OS.get_keycode_string(code))
			Input.parse_input_event(_held[code].duplicate())
	if lost.is_empty():
		return
	Input.flush_buffered_events()
	push_error("GfBridge: 앱이 포커스를 잃어 눌러 둔 키 %s 가 풀렸다 (tick %d). 다시 눌렀지만 이 실행은 원본과 다를 수 있다. 실행 중에는 게임 창을 누르지 말고 다시 돌린다." % [", ".join(lost), _tick])


## OS 이벤트를 처리하며 기다린다. until_inactive 면 앱이 비활성이 될 때까지, 아니면 포커스 변화가 FOCUS_QUIET_MS 동안
## 없을 때까지. 물리 틱 안에서 부르므로 게임 시간은 흐르지 않는다.
func _wait_focus(max_ms: int, until_inactive: bool) -> void:
	var started := Time.get_ticks_msec()
	_focus_changed_ms = started
	while Time.get_ticks_msec() - started < max_ms:
		DisplayServer.process_events()
		if until_inactive and not _app_active:
			return
		if not until_inactive and Time.get_ticks_msec() - _focus_changed_ms >= FOCUS_QUIET_MS:
			return
		OS.delay_msec(2)


# --- 소리 측정 (--gf-audio) ---
#
# 스피커가 아니라 엔진 믹서의 마스터 버스를 잰다. 소리는 벽시계로 흐르므로 실시간 실행에서 의미가 있다.


func _start_audio_probe() -> void:
	_audio_on = true
	_audio_start_ms = Time.get_ticks_msec()
	_capture = AudioEffectCapture.new()
	_capture.buffer_length = 1.0
	AudioServer.add_bus_effect(0, _capture)


func _decibels(level: float) -> float:
	return maxf(linear_to_db(level), AUDIO_FLOOR_DB) if level > 0.0 else AUDIO_FLOOR_DB


func _sample_audio() -> void:
	var now := Time.get_ticks_msec()
	if _bin_start_ms < 0:
		_bin_start_ms = now
	var frames := _capture.get_buffer(_capture.get_frames_available())
	for frame in frames:
		var level := maxf(absf(frame.x), absf(frame.y))
		if level > _bin_peak:
			_bin_peak = level
		_bin_square_sum += (frame.x * frame.x + frame.y * frame.y) * 0.5
		if level < AUDIO_SILENT_LEVEL:
			_quiet_run += 1
			if _quiet_run > _bin_quiet_frames:
				_bin_quiet_frames = _quiet_run
		else:
			_quiet_run = 0
	_bin_frames += frames.size()
	for bus in AudioServer.bus_count:
		var name := AudioServer.get_bus_name(bus)
		var peak := maxf(AudioServer.get_bus_peak_volume_left_db(bus, 0), AudioServer.get_bus_peak_volume_right_db(bus, 0))
		_bin_bus_peak[name] = maxf(_bin_bus_peak.get(name, AUDIO_FLOOR_DB), maxf(peak, AUDIO_FLOOR_DB))
	if now - _bin_start_ms < AUDIO_BIN_MS:
		return
	_audio_timeline.append({
		"ms": _bin_start_ms - _audio_start_ms,
		"tick": _tick,
		"peak_db": _decibels(_bin_peak),
		"rms_db": _decibels(sqrt(_bin_square_sum / _bin_frames)) if _bin_frames > 0 else AUDIO_FLOOR_DB,
		"quiet_ms": 1000.0 * _bin_quiet_frames / AudioServer.get_mix_rate(),
		"bus_peak_db": _bin_bus_peak,
	})
	_bin_start_ms = now
	_bin_peak = 0.0
	_bin_square_sum = 0.0
	_bin_frames = 0
	_bin_quiet_frames = _quiet_run
	_bin_bus_peak = {}


## 씬 트리의 오디오 플레이어를 훑어 이번 틱에 재생이 시작됐거나 반복 지점을 넘은 소리를 적는다.
func _scan_audio_players() -> void:
	var seen := {}
	for type in AUDIO_PLAYER_CLASSES:
		for node in get_tree().root.find_children("*", type, true, false):
			var id: int = node.get_instance_id()
			var position: float = node.get_playback_position() if node.playing else 0.0
			var before: Dictionary = _audio_players.get(id, {"playing": false, "position": 0.0})
			if node.playing and node.stream != null:
				var length: float = node.stream.get_length()
				if not before["playing"]:
					_note_audio_event("start", node, length)
				elif position + 0.05 < before["position"]:
					var wrapped: bool = _stream_loops(node.stream) and before["position"] > length - 0.5
					_note_audio_event("loop" if wrapped else "start", node, length)
			seen[id] = {"playing": node.playing, "position": position}
	_audio_players = seen


func _stream_loops(stream: AudioStream) -> bool:
	if stream is AudioStreamWAV:
		return stream.loop_mode != AudioStreamWAV.LOOP_DISABLED
	return stream.get("loop") == true


func _note_audio_event(kind: String, node: Node, length: float) -> void:
	_audio_events.append({
		"kind": kind,
		"tick": _tick,
		"t": _time(),
		"ms": Time.get_ticks_msec() - _audio_start_ms,
		"sound": node.stream.resource_path,
		"length_s": length,
		"loop": _stream_loops(node.stream),
		"bus": String(node.bus),
		"volume_db": node.volume_db,
	})


func _audio_report() -> Dictionary:
	if not _audio_on:
		return {"ok": false, "error": "소리 측정은 --gf-audio 로 실행했을 때만 쓴다"}
	var report := {
		"mix_rate": AudioServer.get_mix_rate(),
		"timeline": _audio_timeline,
		"events": _audio_events,
	}
	_audio_timeline = []
	_audio_events = []
	return {"ok": true, "audio": report}


# --- 스크린샷과 성능 ---


func _screenshot(path: String) -> Dictionary:
	# 명령은 이번 프레임을 그리기 전(_process)에 받는다. 뷰포트에는 아직 한 틱 전 화면이 있으므로 지금 상태를 그린 뒤 읽는다.
	RenderingServer.force_draw(false)
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		return {"ok": false, "error": "뷰포트 이미지를 얻지 못했다 (headless 렌더러인가?)"}
	# 창에 보이는 그대로 만든다. 스트레치 모드 viewport 에서는 루트 뷰포트가 기준 해상도라 정수배로 키우고,
	# 창의 비율이 달라 남는 자리에는 Godot 이 그리는 것과 같은 검은 띠를 둔다.
	var window := get_window().size
	var factor: int = mini(window.x / image.get_width(), window.y / image.get_height())
	if factor > 1:
		image.resize(image.get_width() * factor, image.get_height() * factor, Image.INTERPOLATE_NEAREST)
	if image.get_size() != window and image.get_width() <= window.x and image.get_height() <= window.y:
		var framed := Image.create(window.x, window.y, false, image.get_format())
		framed.fill(Color.BLACK)
		framed.blit_rect(image, Rect2i(Vector2i.ZERO, image.get_size()), (window - image.get_size()) / 2)
		image = framed
	var err := image.save_png(path)
	if err != OK:
		return {"ok": false, "error": "PNG 저장 실패(%d): %s" % [err, path]}
	return {"ok": true, "size": [image.get_width(), image.get_height()]}


func _perf_counters() -> Dictionary:
	return {
		"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		"objects_drawn": Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		"nodes": Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
		"objects": Performance.get_monitor(Performance.OBJECT_COUNT),
		"memory_mb": Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0,
		"video_memory_mb": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0,
	}


# --- 사람 입력 기록 ---


func _open_record(path: String) -> void:
	_record = FileAccess.open(path, FileAccess.WRITE)
	if _record == null:
		_abort("기록 파일을 열지 못했다: " + path)
		return
	_write_record(_header())


func _write_record(entry: Dictionary) -> void:
	_record.store_line(JSON.stringify(entry))
	_record.flush()


func _input(event: InputEvent) -> void:
	if _record == null:
		return
	var entry := {"type": "input", "tick": _tick, "t": _time(), "down": event.is_pressed()}
	if event is InputEventKey:
		if event.echo:
			return
		var code: int = event.physical_keycode if event.physical_keycode != KEY_NONE else event.keycode
		entry["device"] = "key"
		entry["code"] = OS.get_keycode_string(code)
	elif event is InputEventMouseButton:
		entry["device"] = "mouse"
		entry["code"] = event.button_index
		# _input 의 위치는 뷰포트 좌표다(스트레치 배율로 나뉜 값). 재생은 창 좌표로 넣으므로 창 좌표로 되돌려 적는다.
		var at: Vector2 = get_viewport().get_final_transform() * event.position
		entry["pos"] = [at.x, at.y]
	elif event is InputEventJoypadButton:
		entry["device"] = "joy"
		entry["code"] = event.button_index
	else:
		return
	entry["actions"] = _game_actions(event)
	if event is InputEventKey:
		if event.pressed:
			_recorded_keys[entry["code"]] = entry
		elif not _recorded_keys.erase(entry["code"]):
			return  # 포커스를 잃을 때 이미 뗀 것으로 적었다
	_write_record(entry)


func _game_actions(event: InputEvent) -> Array:
	var matched := []
	for action in info.get("actions", {}):
		if InputMap.has_action(action) and event.is_action(action):
			matched.append(action)
	return matched
