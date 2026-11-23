class_name Screen
extends Node2D
## 화면 씬의 바탕. 코어(Game)의 상태를 읽어 그리기만 한다. main.gd 가 틱마다 advance 를 부른다.

var game: Game
var fx: Fx


func setup(g: Game, effects: Fx) -> void:
	game = g
	fx = effects


func advance() -> void:
	queue_redraw()


## 조리개 전환이 모이는 화면 좌표(보통 고양이가 있는 곳).
func focus() -> Vector2:
	return Ui.SCREEN * 0.5


## 이 화면이 음악을 스스로 트는가(컷신 씬이 그렇게 정했을 때).
func owns_music() -> bool:
	return false


## 고양이의 지금 동작 프레임을 발밑 가운데가 pos 에 오게 그린다.
func draw_cat(pos: Vector2, action: String, flip := false, start := 0, once := false) -> void:
	var texture := Assets.frame("chars/cat_" + action, game.tick, start, once)
	var foot := Layout.cat_foot()
	var size := texture.get_size()
	if flip:
		draw_texture_rect(texture, Rect2((pos - Vector2(size.x - foot.x, foot.y)).round(), Vector2(-size.x, size.y)), false)
	else:
		draw_texture(texture, (pos - foot).round())


## 세계 좌표의 입자·효과·떠오르는 글자를 그린다. origin 은 세계 원점의 화면 좌표.
func draw_effects(origin: Vector2) -> void:
	for s in fx.sprites:
		Ui.sprite(self, Assets.frame(s["base"], fx.tick, s["start"], true), origin + s["pos"])
	for p in fx.particles:
		draw_rect(Rect2((origin + p["pos"]).round(), Vector2(p["size"], p["size"])), p["color"])
	for f in fx.floaters:
		Ui.label(self, origin + f["pos"], f["text"], f["color"])


## 길잡이 화살표: 가리킬 곳 위에서 까딱거린다.
func draw_pointer(pos: Vector2) -> void:
	var bob := roundf(sin(game.tick * 0.15) * 3.0)
	Ui.sprite(self, Assets.tex("ui/arrow.png"), pos + Vector2(0, bob))
