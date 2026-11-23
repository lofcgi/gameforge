class_name GameAudio
extends Node
## 소리: 화면과 구간에 맞는 음악, 사건에 맞는 효과음. 파일(assets/game/audio/<이름>.wav)이 없으면 조용히 넘어가고
## 빠진 이름은 Assets.missing 에 오른다. 소리는 게임 상태를 바꾸지 않는다.

const EVENT_SOUNDS := {"gather": "pick", "door": "door", "sell": "coin", "buy": "buy", "craft": "craft", "repair": "repair",
	"nibble": "nibble", "bite": "bite", "reel": "reel", "snap": "snap", "cut": "snap", "slip": "slip", "hit": "wave_hit",
	"ride": "splash", "jig": "cast", "cursor": "ui_move", "open": "ui_ok", "close": "ui_cancel", "deny": "ui_cancel",
	"page": "page", "pickup": "pickup", "release": "release", "pull": "line_strain", "hop": "step", "skip": "ui_cancel",
	"saved": "ui_ok"}
const MUSIC_DB := -8.0

var _music: AudioStreamPlayer
var _music_name := ""
var _sfx := {}
var _typed := 0


func consume(g: Game, own_music: bool) -> void:
	for e in g.events:
		match e["type"]:
			"anchor":
				sfx("anchor_down" if e["down"] else "anchor_up")
			"catch":
				sfx("catch_big" if e["big"] else "catch_small")
				if e["new"]:
					sfx("codex_new")
			_:
				if EVENT_SOUNDS.has(e["type"]):
					sfx(EVENT_SOUNDS[e["type"]])
	if g.mode == "land" and absf(g.walk.vx) > 40.0 and g.tick % 18 == 0 and not g.menu.busy():
		sfx("step")
	if g.mode == "shop" and not g.shop.typed() and int(g.shop.shown) / 3 != _typed:
		_typed = int(g.shop.shown) / 3
		sfx("talk")
	music("" if own_music else _wanted(g))


## 끝낼 때: 재생을 멈추고 재생기를 놓는다(재생 중인 소리가 남으면 엔진이 종료하며 누수 경고를 낸다).
func release() -> void:
	for node in get_children():
		if node is AudioStreamPlayer:
			node.stop()
			node.stream = null
	_music = null
	_sfx.clear()
	# 믹서 스레드가 멈춘 재생을 내려놓을 틈을 준다. 없으면 종료할 때 재생 객체가 남았다는 경고가 가끔 난다.
	OS.delay_msec(40)


func _wanted(g: Game) -> String:
	match g.scene:
		"title":
			return "title"
		"intro":
			return "cutscene_intro"
		"ending":
			return "cutscene_ending"
		"sea":
			if g.fishing.fighting:
				return "legend_fight" if g.fishing.engaged["id"] == "legend" else "fight"
			return "sea_" + Data.ZONES[maxi(1, Sea.zone_index(g.sailing.x))]["id"]
	return "town"


func music(name: String) -> void:
	if name == _music_name:
		return
	_music_name = name
	if _music != null:
		_music.stop()
		_music.queue_free()
		_music = null
	if name == "" or Assets.stream(name) == null:
		return
	_music = _player(name, MUSIC_DB, true)
	_music.play()


func sfx(name: String) -> void:
	if not _sfx.has(name):
		_sfx[name] = _player(name, 0.0, false) if Assets.stream(name) != null else null
	if _sfx[name] != null:
		_sfx[name].play()


func _player(name: String, volume_db: float, loop: bool) -> AudioStreamPlayer:
	var path := Assets.ROOT + "audio/" + name + ".wav"
	var node: AudioStreamPlayer
	if ResourceLoader.exists(path):
		node = Sound.player(path, volume_db, loop)
	else:
		node = AudioStreamPlayer.new()
		node.stream = Assets.stream(name)
		node.volume_db = volume_db
		if loop and node.stream is AudioStreamWAV:
			node.stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
			node.stream.loop_end = roundi(node.stream.get_length() * node.stream.mix_rate)
		elif loop:
			node.stream.set("loop", true)
	node.name = name
	add_child(node)
	return node
