extends Screen
## 컷신 자리. scenes/cutscenes/<intro|ending>.tscn 을 자식으로 넣어 재생하고, 그 씬이 finished 를 내면 코어에 알린다.
## 규칙(design/asset-spec.md 의 컷신 절): 루트에 signal finished, 진행은 물리 틱으로.
## 건너뛰기는 씬에 skip() 이 있으면 그것을 부르고, 씬이 스스로 처리하면(루트에 skippable 변수) 맡겨 두고, 둘 다 없으면 그 자리에서 끝낸다.
## 씬이 아직 없으면 "준비 중" 임시 카드를 보여 주고 넘어간다. 글 카드로 이야기를 대신하지 않는다.

const HOLD_TICKS := 240
const TITLES := {"intro": "여는 컷신", "ending": "닫는 컷신"}

var _scene: Node
var _own_music := false
var _skipped := false
var _held := 0


func setup(g: Game, effects: Fx) -> void:
	super.setup(g, effects)
	var path := "res://scenes/cutscenes/%s.tscn" % g.cut["kind"]
	if not ResourceLoader.exists(path):
		return
	_scene = load(path).instantiate()
	if not _scene.has_signal("finished"):
		push_error("컷신 씬의 루트에 signal finished 가 없다: " + path)
		_scene.free()
		_scene = null
		return
	_scene.connect("finished", game.cut_done)
	# 컷신 씬은 음악을 스스로 튼다. 게임이 틀게 하려면 씬의 루트에 plays_own_music := false 를 둔다.
	_own_music = _scene.get("plays_own_music") != false
	add_child(_scene)


func advance() -> void:
	if game.cut["skip"] and not _skipped:
		_skipped = true
		if _scene != null and _scene.has_method("skip"):
			_scene.call("skip")
		elif _scene == null or not ("skippable" in _scene):
			game.cut_done()
	if _scene == null:
		_held += 1
		var tapped := game.events.any(func(e): return e["type"] == "cut_action")
		if _held >= HOLD_TICKS or tapped:
			game.cut_done()
	queue_redraw()


## 컷신 씬이 달아 둔 소리 재생기를 멈추고 놓는다(재생 중인 채 사라지면 엔진이 종료하며 누수 경고를 낸다).
func _exit_tree() -> void:
	if _scene == null:
		return
	for player in _scene.find_children("*", "AudioStreamPlayer", true, false):
		player.stop()
		player.stream = null


func owns_music() -> bool:
	return _own_music


func _draw() -> void:
	if _scene != null:
		return
	var kind: String = game.cut["kind"]
	draw_rect(Rect2(Vector2.ZERO, Ui.SCREEN), Pal.NIGHT)
	for i in 16:
		draw_rect(Rect2(i * 80 - fposmod(_held * 0.5, 80.0), 0, 40, 6), Pal.INDIGO)
		draw_rect(Rect2(i * 80 - 80 + fposmod(_held * 0.5, 80.0), 354, 40, 6), Pal.INDIGO)
	Ui.box(self, "panel", Rect2(140, 116, 360, 110))
	Ui.text_center(self, 320, 132, "%s — 준비 중" % TITLES[kind], Pal.BARK)
	Ui.text_center(self, 320, 158, "이 자리에 scenes/cutscenes/%s.tscn 이 재생된다." % kind, Pal.WOOD)
	Ui.text_center(self, 320, 178, "(임시 카드. 실제 장면은 움직이는 그림 컷신이다)", Pal.SAGE)
	Ui.gauge(self, Rect2(260, 202, 120, 12), _held / float(HOLD_TICKS), Pal.AQUA_D)
