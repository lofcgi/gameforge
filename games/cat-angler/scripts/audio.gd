class_name GameAudio
extends Node
## 소리: 화면과 구간에 맞는 음악, 사건에 맞는 효과음. 파일(assets/game/audio/<이름>.wav)이 없으면 조용히 넘어가고
## 빠진 이름은 Assets.missing 에 오른다. 소리는 게임 상태를 바꾸지 않는다.

const EVENT_SOUNDS := {"gather": "pick", "door": "door", "sell": "coin", "buy": "buy", "craft": "craft", "repair": "repair",
	"nibble": "nibble", "bite": "bite", "reel": "reel", "snap": "snap", "cut": "snap", "slip": "slip", "hit": "wave_hit",
	"ride": "splash", "jig": "cast", "cursor": "ui_move", "open": "ui_ok", "close": "ui_cancel", "deny": "ui_cancel",
	"page": "page", "pickup": "pickup", "release": "release", "pull": "line_strain", "hop": "step", "skip": "ui_cancel",
	"saved": "ui_ok"}
## 소리 표: 파일(assets/game 기준)과 재생 음량(dB). 규격(design/asset-spec.md)의 소리는 모두 여기에 있다.
## 음악은 곡마다 음량이 달라(-12 ~ -18 LUFS) 게임 안에서 약 -24 LUFS(줄다리기는 -22)가 되게 낮춘다.
## 효과음 파일은 가장 큰 0.1초가 -16 dB 로 맞춰져 있어(assets/raw/_tools/audio_norm.py) 여기의 dB 가 곧 역할별 크기다:
## 알림·보상 -2 ~ -4, 동작 -3 ~ -7, 메뉴 -6 ~ -9, 걸음과 글자 소리 -9 ~ -10. page 는 파일이 4 dB 작아(피크뿐인 종이 소리) 0 이다.
const TRACKS := {
	"title": {"file": "audio/title.wav", "db": -11.5, "loop": true},
	"town": {"file": "audio/town.wav", "db": -8.0, "loop": true},
	"sea_shallow": {"file": "audio/sea_shallow.wav", "db": -5.5, "loop": true},
	"sea_open": {"file": "audio/sea_open.wav", "db": -8.5, "loop": true},
	"sea_deep": {"file": "audio/sea_deep.wav", "db": -6.5, "loop": true},
	"fight": {"file": "audio/fight.wav", "db": -8.0, "loop": true},
	"legend_fight": {"file": "audio/legend_fight.wav", "db": -9.5, "loop": true},
	"cutscene_intro": {"file": "audio/cutscene_intro.wav", "db": -10.0, "loop": true},
	"cutscene_ending": {"file": "audio/cutscene_ending.wav", "db": -10.0, "loop": true},
	"bite": {"file": "audio/bite.wav", "db": -2.0},
	"catch_big": {"file": "audio/catch_big.wav", "db": -2.0},
	"catch_small": {"file": "audio/catch_small.wav", "db": -3.0},
	"codex_new": {"file": "audio/codex_new.wav", "db": -4.0},
	"snap": {"file": "audio/snap.wav", "db": -2.0},
	"slip": {"file": "audio/slip.wav", "db": -3.0},
	"wave_hit": {"file": "audio/wave_hit.wav", "db": -2.0},
	"coin": {"file": "audio/coin.wav", "db": -3.0},
	"buy": {"file": "audio/buy.wav", "db": -3.0},
	"craft": {"file": "audio/craft.wav", "db": -4.0},
	"repair": {"file": "audio/repair.wav", "db": -3.0},
	"pickup": {"file": "audio/pickup.wav", "db": -2.0},
	"release": {"file": "audio/release.wav", "db": -4.0},
	"pick": {"file": "audio/pick.wav", "db": -3.0},
	"door": {"file": "audio/door.wav", "db": -5.0},
	"anchor_down": {"file": "audio/anchor_down.wav", "db": -4.0},
	"anchor_up": {"file": "audio/anchor_up.wav", "db": -5.0},
	"splash": {"file": "audio/splash.wav", "db": -5.0},
	"cast": {"file": "audio/cast.wav", "db": -5.0},
	"reel": {"file": "audio/reel.wav", "db": -6.0},
	"line_strain": {"file": "audio/line_strain.wav", "db": -6.0},
	"nibble": {"file": "audio/nibble.wav", "db": -7.0},
	"page": {"file": "audio/page.wav", "db": 0.0},
	"ui_ok": {"file": "audio/ui_ok.wav", "db": -6.0},
	"ui_cancel": {"file": "audio/ui_cancel.wav", "db": -7.0},
	"ui_move": {"file": "audio/ui_move.wav", "db": -9.0},
	"step": {"file": "audio/step.wav", "db": -10.0},
	"talk": {"file": "audio/talk.wav", "db": -9.0},
}
## 대사 글자 몇 개마다 talk 를 내는가. 글자는 1초에 45개 찍히므로 4 면 1초에 11번, 소리 하나(45ms)가 끝난 뒤에 다음이 난다.
const TALK_EVERY := 4

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
	if g.mode == "shop" and not g.shop.typed() and int(g.shop.shown) / TALK_EVERY != _typed:
		_typed = int(g.shop.shown) / TALK_EVERY
		# 같은 소리가 줄지어 나면 금세 거슬려서 높이를 조금씩(±9%) 바꾼다. 난수를 쓰지 않아 재생이 어긋나지 않는다.
		sfx("talk", 1.0 + 0.03 * ((_typed * 5) % 7 - 3))
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
	_music = _player(name)
	_music.play()


func sfx(name: String, pitch := 1.0) -> void:
	if not _sfx.has(name):
		_sfx[name] = _player(name) if Assets.stream(name) != null else null
	if _sfx[name] != null:
		_sfx[name].pitch_scale = pitch
		_sfx[name].play()


func _player(name: String) -> AudioStreamPlayer:
	var track: Dictionary = TRACKS[name]
	var path: String = Assets.ROOT + track["file"]
	var loop: bool = track.get("loop", false)
	var node: AudioStreamPlayer
	if ResourceLoader.exists(path):
		node = Sound.player(path, track["db"], loop)
	else:
		node = AudioStreamPlayer.new()
		node.stream = Assets.stream(name)
		node.volume_db = track["db"]
		if loop and node.stream is AudioStreamWAV:
			node.stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
			node.stream.loop_end = roundi(node.stream.get_length() * node.stream.mix_rate)
		elif loop:
			node.stream.set("loop", true)
	node.name = name
	add_child(node)
	return node
