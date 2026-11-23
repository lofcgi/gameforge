class_name CutsceneStage
extends CutscenePlayer
## 여는 컷신과 닫는 컷신이 함께 쓰는 무대(용궁 대전, 깊은 바다)와 소도구.
## 무대를 만드는 함수는 노드들을 `n` 에 이름으로 넣어 두고, 컷의 update 가 꺼내 쓴다.

const KING := "용왕"
const TURTLE := "별주부"
const CAT := "고양이"

## 지금 컷의 노드들. 컷이 바뀌면 비운다.
var n: Dictionary = {}


## 용궁 대전. 조개 침상에 용왕이 누워 있다.
func build_throne(root: Node2D) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/throne")
	n.lanterns = make_lanterns(n.world, [
		Vector2(144, 112), Vector2(187, 121), Vector2(277, 117), Vector2(442, 117), Vector2(527, 121), Vector2(570, 112),
	], 6)
	n.king = actor(n.world, "chars/king_sick", Vector2(606, 338))
	n.king.flip_h = true
	n.puff = make_puff(n.world, 7)
	n.bubbles = make_bubbles(n.world, 9, Rect2(20, 40, 680, 330), 21)


## 용왕의 숨, 기침. coughs 는 기침이 시작되는 시각들.
func update_king(t: float, frame: String, coughs: Array = []) -> void:
	var king: Sprite2D = n.king
	var jolt := 0.0
	var coughing := false
	for at: float in coughs:
		for k in 2:
			var start := at + k * 0.42
			if t >= start and t < start + 0.26:
				coughing = true
				jolt = pulse(t, start, 0.26)
		update_puff(n.puff, t - at, king.position + Vector2(-44, -98), Vector2(-1, -0.25))
	king.texture = tex("chars/king_cough" if coughing else frame)
	king.position.x = 606.0 - roundf(jolt * 4.0)
	king.scale = Vector2(1.0, 1.0 + sin(t * 1.7) * 0.012 - jolt * 0.03)


## 한 번 뿜고 흩어지는 공기방울.
func make_puff(root: Node, count: int) -> Array:
	var list: Array = []
	for i in count:
		var sprite := Sprite2D.new()
		sprite.texture = bubble_texture([3, 4, 5, 7][i % 4])
		sprite.visible = false
		root.add_child(sprite)
		list.append(sprite)
	return list


## since: 뿜은 뒤 흐른 시간. origin 에서 dir 쪽으로 퍼지며 떠오른다.
func update_puff(list: Array, since: float, origin: Vector2, dir := Vector2.UP) -> void:
	if since < 0.0 or since > 1.4:
		if since > 1.4 or since < -0.02:
			for sprite: Sprite2D in list:
				sprite.visible = false
		return
	for i in list.size():
		var sprite: Sprite2D = list[i]
		var spread := Vector2(dir.x + (rnd(i, 31) - 0.5) * 0.9, dir.y + (rnd(i, 32) - 0.5) * 0.9)
		var reach := (1.0 - exp(-since * 3.0)) * (18.0 + rnd(i, 33) * 26.0)
		sprite.visible = since < 0.7 + rnd(i, 34) * 0.7
		sprite.position = (origin + spread * reach + Vector2(0, -since * since * 22.0)).round()


## 사방으로 튀는 반짝임. since 는 터진 뒤 흐른 시간.
func make_burst(root: Node, count: int, radius := 3) -> Array:
	var list: Array = []
	for i in count:
		var sprite := Sprite2D.new()
		sprite.texture = sparkle_texture(radius if i % 2 == 0 else radius - 1)
		sprite.visible = false
		root.add_child(sprite)
		list.append(sprite)
	return list


func update_burst(list: Array, since: float, origin: Vector2, reach := 60.0, life := 0.9) -> void:
	for i in list.size():
		var sprite: Sprite2D = list[i]
		if since < 0.0 or since > life:
			sprite.visible = false
			continue
		var angle := TAU * i / list.size() + rnd(i, 41) * 0.5
		var dist := (1.0 - exp(-since * 5.0)) * reach * (0.6 + rnd(i, 42) * 0.6)
		# 끝나갈 때는 깜빡이며 사라진다.
		sprite.visible = since < life * 0.6 or int(since * 20.0 + i) % 2 == 0
		sprite.position = (origin + Vector2.from_angle(angle) * dist).round()


## 제자리에서 반짝이는 별들 (보물, 나아진 용왕).
func update_twinkles(list: Array, t: float, origin: Vector2, area: Vector2) -> void:
	for i in list.size():
		var sprite: Sprite2D = list[i]
		var cycle := fposmod(t * (0.7 + rnd(i, 51) * 0.6) + rnd(i, 52), 1.0)
		sprite.visible = cycle < 0.45
		sprite.position = (origin + Vector2((rnd(i, 53) - 0.5) * area.x, (rnd(i, 54) - 0.5) * area.y - cycle * 8.0)).round()


## 깊은 바다. 전설의 물고기 그림자가 지나간다.
func build_deep(root: Node2D, legend: String) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/deep")
	n.school = make_school(n.world, "props/p_fish_b", 5, Rect2(0, 60, 704, 200), 34.0, 5)
	n.legend = Sprite2D.new()
	n.legend.texture = tex(legend)
	n.world.add_child(n.legend)
	n.glint = Sprite2D.new()
	n.glint.texture = sparkle_texture(4)
	n.world.add_child(n.glint)
	n.near = group(root)
	n.bubbles = make_bubbles(n.near, 14, Rect2(0, -20, 760, 420), 61)


## 걷는 듯 통통 튀는 높이.
static func hop(t: float, rate := 9.0, height := 2.0) -> float:
	return -absf(sin(t * rate)) * height
