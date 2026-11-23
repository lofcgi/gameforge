class_name CutscenePlayer
extends CanvasLayer
## 컷신 재생기. 컷(shot)의 목록을 순서대로 틀고, 자막·전환·건너뛰기·소리를 맡는다.
##
## 컷신 하나는 이 스크립트를 상속해 `_shots()` 만 채운다 (intro.gd, ending.gd).
## 시간은 물리 틱으로만 센다(벽시계를 읽지 않는다). 컷의 모든 움직임은 "컷 안에서 흐른 시간 t"의
## 함수라서, 같은 t 면 언제나 같은 화면이 나오고 아무 컷의 아무 시각으로 건너뛸 수 있다.
##
## 게임에서 쓰는 법:
##   var cs := preload("res://scenes/cutscenes/intro.tscn").instantiate()
##   add_child(cs); await cs.finished; cs.queue_free()
## 건너뛰기: `cancel` 액션을 SKIP_HOLD 초 동안 누르고 있는다.
## 디버그: 내보낸 변수 `start_shot`, `only_start_shot` 또는 명령줄 `-- --cs-shot=N [--cs-t=초] [--cs-only]`.
## 단독 실행(이 씬이 현재 씬일 때)에서는 끝나면 스스로 종료한다.

## 컷신이 끝났거나 건너뛰었을 때 한 번 낸다.
signal finished

const W := 640
const H := 360
const TICKS := 60.0
const SKIP_HOLD := 1.0
const TRANSITION := 0.5
const ART := "res://assets/game/cutscenes/"
const AUDIO := "res://assets/game/cutscenes/audio/"
const FONT_DIR := "res://assets/game/fonts/"

const INK := Color("17121b")
const NAVY := Color("1b2139")
const BROWN_DARK := Color("5e342b")
const BROWN := Color("8c533c")
const TEAL_DARK := Color("28706f")
const TEAL := Color("54a9a7")
const CYAN := Color("76d7d9")
const MINT := Color("baeadc")
const CREAM := Color("e5ddc8")
const PAPER := Color("e9f3e2")
const ORANGE := Color("d79966")

## 몇 번째 컷부터 틀지 (0부터).
@export var start_shot := 0
## 참이면 start_shot 한 컷만 틀고 끝낸다.
@export var only_start_shot := false
@export var skippable := true
@export var music_db := -8.0
@export var sfx_db := -3.0

var shots: Array[Dictionary] = []
var shot_index := -1
## 지금 컷 안에서 흐른 시간(초).
var shot_time := 0.0

var _tick := 0
var _shot_tick := 0
var _done := false
var _skip_ticks := 0
var _skipping := false
var _outro_ticks := -1
var _standalone := false
var _snap_jobs: Array = []
var _snap_dir := ""
var _record_fps := 10

var _frame: Control
var _world: Node2D
var _shot_root: Node2D
var _fx: Node2D
var _sub_panel: Panel
var _sub_name: Label
var _sub_text: Label
var _skip_box: Control
var _font: Font
var _music: Dictionary = {}
var _music_now := ""
var _sfx_done: Dictionary = {}
var _tex_cache: Dictionary = {}
var _transition_kind := "fade"
var _cover := 0.0
var _uncover_from_left := false


## 상속한 스크립트가 컷 목록을 돌려준다. 컷 하나:
## { "dur": 초, "build": Callable(root: Node2D), "update": Callable(t: float),
##   "subs": [[시작, 끝, 화자, 문장], ...], "sfx": [[시각, 이름], ...],
##   "music": 이름(바뀔 때만), "enter": "fade"|"cut"|"wave", "sub_top": 자막을 위에 둘지 }
func _shots() -> Array[Dictionary]:
	return []


func _ready() -> void:
	layer = 80
	process_mode = Node.PROCESS_MODE_ALWAYS
	_standalone = get_tree().current_scene == self
	_font = _find_font()
	_build_frame()
	shots = _shots()
	var only := only_start_shot
	var first := start_shot
	var first_t := 0.0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--cs-shot="):
			first = int(arg.trim_prefix("--cs-shot="))
		elif arg.begins_with("--cs-t="):
			first_t = float(arg.trim_prefix("--cs-t="))
		elif arg == "--cs-only":
			only = true
		elif arg.begins_with("--cs-snap="):
			_snap_dir = arg.trim_prefix("--cs-snap=")
		elif arg.begins_with("--cs-fps="):
			_record_fps = int(arg.trim_prefix("--cs-fps="))
		elif arg.begins_with("--cs-times="):
			for item in arg.trim_prefix("--cs-times=").split(","):
				var pair := item.split(":")
				_snap_jobs.append([int(pair[0]), float(pair[1])])
	only_start_shot = only
	start_shot = clampi(first, 0, shots.size() - 1)
	get_viewport().size_changed.connect(_fit)
	_fit()
	if _snap_dir != "" and _standalone:
		set_physics_process(false)
		get_window().always_on_top = true
		if _snap_jobs.is_empty():
			_enter_shot(start_shot, first_t)
			_run_recording()
		else:
			_run_snaps()
		return
	_enter_shot(start_shot, first_t)


## 컷 index 의 t 초로 바로 간다. 화면은 그 시각의 모습 그대로다.
func seek(index: int, t := 0.0) -> void:
	_enter_shot(clampi(index, 0, shots.size() - 1), t)


func total_duration() -> float:
	var sum := 0.0
	for shot in shots:
		sum += float(shot["dur"])
	return sum


func _physics_process(_delta: float) -> void:
	if _done:
		return
	_tick += 1
	if _outro_ticks >= 0:
		_outro_ticks += 1
		_cover = clampf(_outro_ticks / (TRANSITION * TICKS), 0.0, 1.0)
		_transition_kind = "fade"
		_fade_music(1.0 - _cover)
		_fx.queue_redraw()
		if _cover >= 1.0:
			_finish()
		return
	_read_skip()
	_shot_tick += 1
	shot_time = _shot_tick / TICKS
	var shot: Dictionary = shots[shot_index]
	if shot_time >= float(shot["dur"]):
		if only_start_shot or shot_index + 1 >= shots.size():
			_outro_ticks = int(TRANSITION * TICKS)
			_cover = 1.0
			_finish()
			return
		_enter_shot(shot_index + 1, 0.0)
		return
	_apply(shot)


func _enter_shot(index: int, t: float) -> void:
	shot_index = index
	_shot_tick = int(round(t * TICKS))
	shot_time = _shot_tick / TICKS
	if _shot_root:
		_shot_root.free()
	_shot_root = Node2D.new()
	_world.add_child(_shot_root)
	_sfx_done.clear()
	var shot: Dictionary = shots[index]
	(shot["build"] as Callable).call(_shot_root)
	# 이 컷까지 오는 동안 마지막으로 정해진 음악을 튼다 (중간 컷으로 건너뛰어도 맞는 곡이 나온다).
	var track := ""
	for i in range(index + 1):
		track = shots[i].get("music", track)
	_play_music(track)
	# 건너뛰어 들어온 경우 이미 지난 효과음은 내지 않는다.
	for cue in shot.get("sfx", []):
		if float(cue[0]) < shot_time - 0.05:
			_sfx_done[cue] = true
	_apply(shot)


func _apply(shot: Dictionary) -> void:
	(shot["update"] as Callable).call(shot_time)
	_update_subs(shot)
	_update_transition(shot)
	for cue in shot.get("sfx", []):
		if shot_time >= float(cue[0]) and not _sfx_done.has(cue):
			_sfx_done[cue] = true
			play_sfx(cue[1])


func _update_transition(shot: Dictionary) -> void:
	var dur := float(shot["dur"])
	var kind_in: String = shot.get("enter", "fade")
	var kind_out := "fade"
	if shot_index + 1 < shots.size() and not only_start_shot:
		kind_out = shots[shot_index + 1].get("enter", "fade")
	_cover = 0.0
	if kind_in != "cut" and shot_time < TRANSITION:
		_cover = 1.0 - shot_time / TRANSITION
		_transition_kind = kind_in
		_uncover_from_left = true
	elif kind_out != "cut" and shot_time > dur - TRANSITION:
		_cover = (shot_time - (dur - TRANSITION)) / TRANSITION
		_transition_kind = kind_out
		_uncover_from_left = false
	_fx.queue_redraw()


func _finish() -> void:
	if _done:
		return
	_done = true
	_sub_panel.visible = false
	_skip_box.visible = false
	for player: AudioStreamPlayer in _music.values():
		player.stop()
	_fx.queue_redraw()
	finished.emit()
	if _standalone:
		get_tree().quit()


# ---------- 건너뛰기 ----------

func _read_skip() -> void:
	if not skippable or not InputMap.has_action("cancel"):
		return
	if Input.is_action_pressed("cancel"):
		_skip_ticks += 1
	else:
		_skip_ticks = maxi(0, _skip_ticks - 3)
	_skip_box.visible = _skip_ticks > 0
	_skip_box.queue_redraw()
	if _skip_ticks >= int(SKIP_HOLD * TICKS):
		_skipping = true
		_outro_ticks = 0


func _draw_skip() -> void:
	var ratio := clampf(_skip_ticks / (SKIP_HOLD * TICKS), 0.0, 1.0)
	_skip_box.draw_rect(Rect2(0, 0, 92, 18), PAPER)
	_skip_box.draw_rect(Rect2(0, 0, 92, 18), BROWN, false, 1.0)
	_skip_box.draw_string(_font, Vector2(5, 13), "건너뛰기", HORIZONTAL_ALIGNMENT_LEFT, -1, _font_size(), BROWN_DARK)
	_skip_box.draw_rect(Rect2(54, 6, 32, 6), CREAM)
	_skip_box.draw_rect(Rect2(54, 6, roundf(32 * ratio), 6), TEAL_DARK)
	_skip_box.draw_rect(Rect2(54, 6, 32, 6), BROWN, false, 1.0)


# ---------- 화면 틀 ----------

func _build_frame() -> void:
	var backdrop := ColorRect.new()
	backdrop.color = INK
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(backdrop)
	_frame = Control.new()
	_frame.size = Vector2(W, H)
	_frame.clip_contents = true
	_frame.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_frame)
	_world = Node2D.new()
	_frame.add_child(_world)
	_fx = Node2D.new()
	_fx.draw.connect(_draw_fx)
	_frame.add_child(_fx)
	_build_subtitles()
	_skip_box = Control.new()
	_skip_box.position = Vector2(W - 100, 8)
	_skip_box.size = Vector2(92, 18)
	_skip_box.visible = false
	_skip_box.draw.connect(_draw_skip)
	_frame.add_child(_skip_box)


func _fit() -> void:
	var view := get_viewport().get_visible_rect().size
	var factor := minf(view.x / W, view.y / H)
	if factor >= 1.0:
		factor = floorf(factor)
	_frame.scale = Vector2(factor, factor)
	_frame.position = ((view - Vector2(W, H) * factor) / 2.0).round()


func _find_font() -> Font:
	# 12px 에 맞춰 그려진 본문용 글꼴을 먼저 찾고, 없으면 폴더의 첫 글꼴을 쓴다.
	var names: Array = ["Galmuri11.ttf"]
	var dir := DirAccess.open(FONT_DIR)
	if dir:
		var found := Array(dir.get_files())
		found.sort()
		names.append_array(found)
	for file: String in names:
		var lower := file.to_lower()
		if not (lower.ends_with(".ttf") or lower.ends_with(".otf") or lower.ends_with(".fnt")):
			continue
		if ResourceLoader.exists(FONT_DIR + file):
			var font := load(FONT_DIR + file)
			if font is Font:
				return font
	# 픽셀 글꼴이 없으면 엔진 기본 글꼴(한글은 시스템 글꼴로 대체)을 쓴다.
	return ThemeDB.fallback_font


func _font_size() -> int:
	return 12


# ---------- 자막 ----------

func _build_subtitles() -> void:
	_sub_panel = Panel.new()
	var box := StyleBoxFlat.new()
	box.bg_color = PAPER
	box.border_color = BROWN
	box.set_border_width_all(1)
	box.set_corner_radius_all(2)
	box.anti_aliasing = false
	box.shadow_color = Color(INK, 0.35)
	box.shadow_size = 0
	_sub_panel.add_theme_stylebox_override("panel", box)
	_sub_panel.position = Vector2(70, 300)
	_sub_panel.size = Vector2(500, 50)
	_sub_panel.visible = false
	_sub_panel.draw.connect(_draw_sub_ornament)
	_frame.add_child(_sub_panel)
	_sub_name = Label.new()
	_sub_name.position = Vector2(12, 5)
	_sub_name.add_theme_font_override("font", _font)
	_sub_name.add_theme_font_size_override("font_size", _font_size())
	_sub_name.add_theme_color_override("font_color", TEAL_DARK)
	_sub_panel.add_child(_sub_name)
	_sub_text = Label.new()
	_sub_text.position = Vector2(12, 5)
	_sub_text.size = Vector2(476, 40)
	_sub_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_sub_text.add_theme_font_override("font", _font)
	_sub_text.add_theme_font_size_override("font_size", _font_size())
	_sub_text.add_theme_color_override("font_color", BROWN_DARK)
	_sub_text.add_theme_constant_override("line_spacing", 2)
	_sub_panel.add_child(_sub_text)


## 창 모서리의 물결 문양 한 조각.
func _draw_sub_ornament() -> void:
	for i in 3:
		var centre := Vector2(_sub_panel.size.x - 14.0 - i * 9.0, _sub_panel.size.y - 3.0)
		_sub_panel.draw_arc(centre, 5.0, PI, TAU, 8, TEAL, 1.0, false)
		_sub_panel.draw_arc(centre, 2.0, PI, TAU, 6, TEAL, 1.0, false)


func _update_subs(shot: Dictionary) -> void:
	var active: Array = []
	for sub in shot.get("subs", []):
		if shot_time >= float(sub[0]) and shot_time < float(sub[1]):
			active = sub
	if active.is_empty():
		_sub_panel.visible = false
		return
	_sub_panel.visible = true
	_sub_panel.position.y = 10.0 if shot.get("sub_top", false) else 300.0
	var speaker: String = active[2]
	var text: String = active[3]
	_sub_name.text = speaker
	_sub_name.visible = speaker != ""
	# 나레이션은 가운데, 대사는 이름 아래 왼쪽 정렬.
	if speaker == "":
		_sub_text.position = Vector2(12, 5)
		_sub_text.size = Vector2(476, 40)
		_sub_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_sub_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	else:
		_sub_text.position = Vector2(12, 21)
		_sub_text.size = Vector2(476, 26)
		_sub_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		_sub_text.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_sub_text.text = text
	# 타자기: 한 글자씩 나타난다. 문장이 끝나기 0.8초 전에는 다 보이게 속도를 맞춘다.
	var span := maxf(0.3, float(active[1]) - float(active[0]) - 1.2)
	var rate := maxf(22.0, text.length() / span)
	_sub_text.visible_characters = mini(text.length(), int((shot_time - float(active[0])) * rate) + 1)


## 지금 자막의 화자 ("" 이면 나레이션이거나 자막 없음). 말하는 동안 입을 움직이는 데 쓴다.
func speaking(who: String) -> bool:
	return _sub_panel.visible and _sub_name.text == who and _sub_text.visible_characters < _sub_text.text.length()


# ---------- 전환 ----------

func _draw_fx() -> void:
	if _cover <= 0.0:
		return
	if _transition_kind == "wave":
		_draw_wave_wipe()
		return
	# 페이드: 반투명 대신 4단계 디더 무늬로 덮는다.
	var level := clampi(int(ceil(_cover * 4.0)), 1, 4)
	if level >= 4:
		_fx.draw_rect(Rect2(0, 0, W, H), INK)
		return
	var step := 4
	@warning_ignore("integer_division")
	for y in range(0, H, step):
		for x in range(0, W, step):
			var cell := ((x / step) % 2) + ((y / step) % 2) * 2
			var on := (level == 1 and cell == 0) or (level == 2 and (cell == 0 or cell == 3)) or (level == 3 and cell != 1)
			if on:
				_fx.draw_rect(Rect2(x, y, step, step), INK)


## 물결이 화면을 쓸고 지나간다. 덮을 때는 왼쪽에서 밀려오고, 걷힐 때는 오른쪽으로 빠져나간다.
func _draw_wave_wipe() -> void:
	var travel := W + 200.0
	var progress := (1.0 - _cover) if _uncover_from_left else _cover
	var row_h := 4.0
	var rows := int(H / row_h)
	for row in rows:
		var y := row * row_h
		# 큰 물결 하나에 잔물결을 얹은 가장자리.
		var wobble := sin(y * 0.035 + progress * 7.0) * 34.0 + sin(y * 0.11 - progress * 9.0) * 9.0
		var edge := roundf((-90.0 + travel * progress + wobble) / 2.0) * 2.0
		var bands: Array = [[0.0, 6.0, PAPER], [6.0, 16.0, CYAN], [22.0, 22.0, TEAL]]
		if _uncover_from_left:
			_fx.draw_rect(Rect2(edge, y, W - edge + 100.0, row_h), TEAL_DARK)
			for band: Array in bands:
				_fx.draw_rect(Rect2(edge - band[0] - band[1], y, band[1], row_h), band[2])
		else:
			_fx.draw_rect(Rect2(-100.0, y, edge + 100.0, row_h), TEAL_DARK)
			for band: Array in bands:
				_fx.draw_rect(Rect2(edge + band[0], y, band[1], row_h), band[2])


# ---------- 소리 ----------

func _play_music(track: String) -> void:
	if track == _music_now:
		return
	if _music.has(_music_now):
		(_music[_music_now] as AudioStreamPlayer).stop()
	_music_now = track
	if track == "":
		return
	if not _music.has(track):
		var path := AUDIO + track + ".wav"
		if not ResourceLoader.exists(path):
			return
		var player := AudioStreamPlayer.new()
		var stream: AudioStream = load(path)
		if stream is AudioStreamWAV:
			var wav: AudioStreamWAV = stream
			wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
			wav.loop_begin = 0
			wav.loop_end = roundi(wav.get_length() * wav.mix_rate)
		player.stream = stream
		add_child(player)
		_music[track] = player
	var now: AudioStreamPlayer = _music[track]
	now.volume_db = music_db
	now.play()


func _fade_music(ratio: float) -> void:
	if _music.has(_music_now):
		(_music[_music_now] as AudioStreamPlayer).volume_db = music_db + linear_to_db(maxf(ratio, 0.01))


## 효과음 한 번. 화면이나 진행에는 영향을 주지 않는다.
func play_sfx(sound: String) -> void:
	var path := AUDIO + sound + ".wav"
	if not ResourceLoader.exists(path):
		return
	var player := AudioStreamPlayer.new()
	player.stream = load(path)
	player.volume_db = sfx_db
	add_child(player)
	player.finished.connect(player.queue_free)
	player.play()


# ---------- 컷을 만드는 도구 (상속한 스크립트가 쓴다) ----------

func tex(path: String) -> Texture2D:
	if not _tex_cache.has(path):
		_tex_cache[path] = load(ART + path + ".png")
	return _tex_cache[path]


## 왼쪽 위 기준으로 놓는 그림 한 장.
func layer_sprite(root: Node, path: String, at := Vector2.ZERO) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = tex(path)
	sprite.centered = false
	sprite.position = at
	root.add_child(sprite)
	return sprite


## 발밑 가운데 기준으로 놓는 캐릭터. 눌림·늘어남(scale)이 발밑에서 일어난다.
func actor(root: Node, path: String, feet := Vector2.ZERO) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = tex(path)
	sprite.centered = false
	sprite.offset = Vector2(-sprite.texture.get_width() / 2.0, -sprite.texture.get_height())
	sprite.position = feet
	root.add_child(sprite)
	return sprite


func group(root: Node) -> Node2D:
	var node := Node2D.new()
	root.add_child(node)
	return node


## a → b 를 t0~t1 동안 부드럽게.
static func glide(t: float, t0: float, t1: float, a: float = 0.0, b: float = 1.0) -> float:
	var x := clampf((t - t0) / maxf(t1 - t0, 0.0001), 0.0, 1.0)
	return lerpf(a, b, x * x * (3.0 - 2.0 * x))


## t0 에서 시작해 dur 동안 튀었다 가라앉는 값 (0 → 1 → 0).
static func pulse(t: float, t0: float, dur: float) -> float:
	var x := (t - t0) / dur
	if x < 0.0 or x > 1.0:
		return 0.0
	return sin(x * PI)


## 시드로 정해지는 0~1 값. 입자의 자리·속도를 고정하는 데 쓴다.
static func rnd(i: int, salt: int = 0) -> float:
	var n := (i * 374761393 + salt * 668265263) & 0x7fffffff
	n = ((n ^ (n >> 13)) * 1274126177) & 0x7fffffff
	return float(n % 10007) / 10007.0


## 작은 공기방울 그림 (지름 d). 코드로 찍는 1x 픽셀.
func bubble_texture(d: int) -> Texture2D:
	var key := "bubble%d" % d
	if _tex_cache.has(key):
		return _tex_cache[key]
	var image := Image.create(d, d, false, Image.FORMAT_RGBA8)
	var c := (d - 1) / 2.0
	for y in d:
		for x in d:
			var dist := Vector2(x - c, y - c).length()
			if dist <= c + 0.3 and dist >= c - 0.75:
				image.set_pixel(x, y, MINT)
	if d >= 5:
		image.set_pixel(int(c * 0.6), int(c * 0.6), PAPER)
	_tex_cache[key] = ImageTexture.create_from_image(image)
	return _tex_cache[key]


## 큰 공기 방울 고리 (고양이의 잠수 방울). 안은 비어 있고 테두리와 빛 조각만 있다.
func ring_texture(d: int) -> Texture2D:
	var key := "ring%d" % d
	if _tex_cache.has(key):
		return _tex_cache[key]
	var image := Image.create(d, d, false, Image.FORMAT_RGBA8)
	var c := (d - 1) / 2.0
	for y in d:
		for x in d:
			var v := Vector2(x - c, y - c)
			var dist := v.length()
			if dist <= c + 0.3 and dist >= c - 1.0:
				image.set_pixel(x, y, MINT)
			elif dist < c - 1.0 and dist > c * 0.78 and v.angle() < -PI * 0.55 and v.angle() > -PI * 0.9:
				image.set_pixel(x, y, PAPER)
	_tex_cache[key] = ImageTexture.create_from_image(image)
	return _tex_cache[key]


## 체크 무늬로 퍼지는 마름모 빛 (반투명 없이 만드는 빛무리).
func glow_texture(r: int, colour: Color) -> Texture2D:
	var key := "glow%d%s" % [r, colour.to_html()]
	if _tex_cache.has(key):
		return _tex_cache[key]
	var d := r * 2 + 1
	var image := Image.create(d, d, false, Image.FORMAT_RGBA8)
	for y in d:
		for x in d:
			var dist: int = absi(x - r) + absi(y - r)
			if dist <= r / 3:
				image.set_pixel(x, y, colour)
			elif dist <= r * 2 / 3 and (x + y) % 2 == 0:
				image.set_pixel(x, y, colour)
			elif dist <= r and x % 2 == 0 and y % 2 == 0:
				image.set_pixel(x, y, colour)
	_tex_cache[key] = ImageTexture.create_from_image(image)
	return _tex_cache[key]


## 네 갈래 반짝임.
func sparkle_texture(r: int) -> Texture2D:
	var key := "sparkle%d" % r
	if _tex_cache.has(key):
		return _tex_cache[key]
	var d := r * 2 + 1
	var image := Image.create(d, d, false, Image.FORMAT_RGBA8)
	for i in range(-r, r + 1):
		image.set_pixel(r + i, r, PAPER)
		image.set_pixel(r, r + i, PAPER)
	if r >= 3:
		for sx: int in [-1, 1]:
			for sy: int in [-1, 1]:
				image.set_pixel(r + sx, r + sy, MINT)
	_tex_cache[key] = ImageTexture.create_from_image(image)
	return _tex_cache[key]


## 위로 떠오르는 공기방울 무리. area 안에서 돌고 돈다. update_bubbles 로 움직인다.
func make_bubbles(root: Node, count: int, area: Rect2, salt: int = 1) -> Array:
	var list: Array = []
	for i in count:
		var sprite := Sprite2D.new()
		sprite.texture = bubble_texture([3, 3, 4, 5, 7][int(rnd(i, salt) * 5.0)])
		root.add_child(sprite)
		list.append({
			"node": sprite,
			"x": area.position.x + rnd(i, salt + 1) * area.size.x,
			"phase": rnd(i, salt + 2),
			"speed": 14.0 + rnd(i, salt + 3) * 26.0,
			"sway": 2.0 + rnd(i, salt + 4) * 5.0,
			"area": area,
		})
	return list


func update_bubbles(list: Array, t: float) -> void:
	for bubble: Dictionary in list:
		var area: Rect2 = bubble["area"]
		var travel := fposmod(bubble["phase"] * area.size.y + t * bubble["speed"], area.size.y)
		var node: Sprite2D = bubble["node"]
		node.position = Vector2(
			bubble["x"] + sin(t * 1.7 + bubble["phase"] * 20.0) * bubble["sway"],
			area.end.y - travel
		).round()


## 깜빡이는 등불 빛무리들. positions 는 배경 그림 안의 좌표.
func make_lanterns(root: Node, positions: Array, radius := 7) -> Array:
	var list: Array = []
	for at: Vector2 in positions:
		var sprite := Sprite2D.new()
		sprite.texture = glow_texture(radius, CYAN)
		sprite.position = at
		root.add_child(sprite)
		list.append(sprite)
	return list


func update_lanterns(list: Array, t: float) -> void:
	for i in list.size():
		var sprite: Sprite2D = list[i]
		# 등불마다 다른 박자로 커졌다 작아진다 (세 단계).
		var wave := sin(t * (2.2 + rnd(i, 7) * 2.0) + rnd(i, 8) * TAU)
		sprite.visible = wave > -0.55
		sprite.scale = Vector2.ONE * (2.0 if wave > 0.45 else 1.0)


## 일렁이는 빛줄기. 위가 좁고 아래가 넓은 띠.
func make_shafts(root: Node, xs: Array, top: float, length: float, colour: Color) -> Array:
	var list: Array = []
	for x: float in xs:
		var shaft := Polygon2D.new()
		shaft.color = colour
		shaft.position = Vector2(x, top)
		root.add_child(shaft)
		list.append({"node": shaft, "length": length, "x": x})
	return list


func update_shafts(list: Array, t: float) -> void:
	for i in list.size():
		var shaft: Dictionary = list[i]
		var lean := sin(t * 0.5 + i * 1.3) * 26.0 + 40.0
		var width := 22.0 + sin(t * 0.8 + i * 2.1) * 8.0
		var length: float = shaft["length"]
		(shaft["node"] as Polygon2D).polygon = PackedVector2Array([
			Vector2(-6, 0), Vector2(6, 0), Vector2(lean + width, length), Vector2(lean - width, length),
		])


## 한 방향으로 헤엄쳐 지나가는 물고기 그림자들.
func make_school(root: Node, path: String, count: int, area: Rect2, speed: float, salt: int = 3) -> Array:
	var list: Array = []
	for i in count:
		var sprite := Sprite2D.new()
		sprite.texture = tex(path)
		sprite.flip_h = speed < 0.0
		root.add_child(sprite)
		list.append({
			"node": sprite, "area": area,
			"phase": rnd(i, salt), "y": area.position.y + rnd(i, salt + 1) * area.size.y,
			"speed": speed * (0.8 + rnd(i, salt + 2) * 0.5),
		})
	return list


func update_school(list: Array, t: float) -> void:
	for fish: Dictionary in list:
		var area: Rect2 = fish["area"]
		var span := area.size.x + 80.0
		var along := fposmod(fish["phase"] * span + t * fish["speed"], span)
		var node: Sprite2D = fish["node"]
		node.position = Vector2(area.position.x - 40.0 + along, fish["y"] + sin(t * 2.0 + fish["phase"] * 9.0) * 3.0).round()
		# 꼬리짓 대신 몸이 살짝 눌렸다 펴진다.
		node.scale.x = 1.0 if int(t * 4.0 + fish["phase"] * 7.0) % 2 == 0 else 0.9


# ---------- 캡처 (디버그) ----------

## `-- --cs-snap=<폴더> [--cs-fps=10]` 만 주면 처음(또는 --cs-shot)부터 끝까지 실제 순서대로 틀면서
## 프레임마다 PNG 를 남긴다. 엔진의 --write-movie 와 달리 화면이 실제로 그려진 뒤에만 다음 틱으로 넘어가므로,
## 창이 가려져 그리기가 멈춰도 같은 그림이 반복해 찍히지 않는다.
func _run_recording() -> void:
	DirAccess.make_dir_recursive_absolute(_snap_dir)
	var frame := 0
	var ticks_per_frame := int(TICKS / _record_fps)
	while not _done:
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/f%05d.png" % [_snap_dir, frame])
		frame += 1
		for i in ticks_per_frame:
			if not _done:
				_physics_process(1.0 / TICKS)


## `-- --cs-snap=<폴더> --cs-times=컷:초,컷:초,...` 로 실행하면 그 시각의 화면을 PNG 로 남기고 끝낸다.
func _run_snaps() -> void:
	DirAccess.make_dir_recursive_absolute(_snap_dir)
	for job in _snap_jobs:
		seek(job[0], job[1])
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		image.save_png("%s/s%02d_t%05.2f.png" % [_snap_dir, job[0], job[1]])
	get_tree().quit()
