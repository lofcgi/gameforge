class_name CutsceneStage
extends CutscenePlayer
## 여는 컷신과 닫는 컷신이 함께 쓰는 무대(용궁 대전, 깊은 바다)와 소도구.
## 무대를 만드는 함수는 노드들을 `n` 에 이름으로 넣어 두고, 컷의 update 가 꺼내 쓴다.

const KING := "용왕"
const TURTLE := "별주부"
const CAT := "고양이"
const KING_AT := Vector2(606, 338)
const KING_MOUTH := Vector2(-52, -112)

## 걸음 한 주기(두 발)에 몸이 나아가는 거리. 디딘 두 발 사이의 거리(별주부 30px, 고양이 35px)의 두 배다.
## 걷는 프레임을 시간이 아니라 간 거리로 고르므로 속도가 변해도 발이 바닥에서 미끄러지지 않는다.
const TURTLE_STRIDE := 60.0
const CAT_STRIDE := 70.0
## 용왕 그림에서 이 줄 위(머리와 가슴)만 숨에 따라 오르내린다. 아래는 이불이다.
const KING_SPLIT := 152

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
	n.king = group(n.world)
	n.king.position = KING_AT
	var size := tex("chars/king_sick").get_size()
	n.king_top = _king_part(Rect2(0, 0, size.x, KING_SPLIT + 4))
	n.king_bed = _king_part(Rect2(0, KING_SPLIT, size.x, size.y - KING_SPLIT))
	n.puff = make_puff(n.world, 7)
	n.bubbles = make_bubbles(n.world, 9, Rect2(20, 40, 680, 330), 21)


func _king_part(region: Rect2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = tex("chars/king_sick")
	sprite.centered = false
	sprite.region_enabled = true
	sprite.region_rect = region
	sprite.flip_h = true
	sprite.offset = Vector2(-region.size.x / 2.0, region.position.y - sprite.texture.get_height())
	n.king.add_child(sprite)
	return sprite


## 용왕의 숨, 눈 깜빡임, 기침. coughs 는 기침이 시작되는 시각들.
func update_king(t: float, frame: String, coughs: Array = []) -> void:
	var king: Node2D = n.king
	var jolt := 0.0
	var coughing := false
	for at: float in coughs:
		for k in 2:
			var start := at + k * 0.42
			if t >= start and t < start + 0.26:
				coughing = true
				jolt = pulse(t, start, 0.26)
		update_puff(n.puff, t - at, KING_AT + KING_MOUTH, Vector2(-1, -0.25))
	var sick := frame == "chars/king_sick"
	if coughing:
		frame = "chars/king_cough"
	elif not sick and fposmod(t + 0.9, 3.3) > 3.14:
		frame += "_blink"
	n.king_top.texture = tex(frame)
	n.king_bed.texture = tex(frame)
	# 숨: 머리와 가슴이 이불 위로 오르내린다. 앓는 동안에는 가쁘고 깊다.
	var breath := sin(t * (2.3 if sick else 1.6)) * 0.5 + 0.5
	n.king_top.position.y = -roundf(breath * (3.0 if sick else 2.0)) - roundf(jolt * 2.0)
	king.position = KING_AT - Vector2(roundf(jolt * 4.0), 0)
	king.scale = Vector2.ONE


## 컷신 폴더 밖, 게임이 쓰는 그림 (전설의 물고기).
func game_tex(path: String) -> Texture2D:
	var key := "game/" + path
	if not _tex_cache.has(key):
		_tex_cache[key] = load("res://assets/game/" + path)
	return _tex_cache[key]


## 걷는 프레임. 바닥 위의 자리 x 로 프레임을 고르므로 디딘 발이 그 자리에 머문다. 왼쪽을 볼 때는 그림을 뒤집어 쓰므로 x 도 뒤집어 센다.
func walk_tex(who: String, x: float, facing_left: bool, stride: float) -> Texture2D:
	var along := -x if facing_left else x
	return tex("chars/%s_walk_%d" % [who, posmod(floori(along / (stride / 4.0)), 4)])


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


## 깊은 바다. 전설의 물고기 그림자가 지나간다. frames 는 그림에 가로로 놓인 프레임 수, head_right 는 그림 속 머리의 방향.
func build_deep(root: Node2D, legend: String, frames: int, head_right: bool) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/deep")
	n.far_motes = make_motes(n.world, 26, Rect2(0, 0, 704, 393), 131)
	n.school = make_school(n.world, "props/p_fish_b", 5, Rect2(0, 60, 704, 200), 34.0, 5)
	n.wake = make_wake(n.world, 16)
	n.legend = Swimmer.new()
	n.legend.texture = tex(legend)
	n.legend.frames = frames
	n.legend.head_right = head_right
	n.world.add_child(n.legend)
	n.glint = Sprite2D.new()
	n.glint.texture = sparkle_texture(4)
	n.world.add_child(n.glint)
	n.near = group(root)
	n.near_motes = make_motes(n.near, 14, Rect2(0, 0, 760, 393), 151)
	n.bubbles = make_bubbles(n.near, 14, Rect2(0, -20, 760, 420), 61)


## 헤엄치는 큰 물고기. 그림을 세로 줄로 잘라 줄마다 다른 높이에 그려 몸이 물결친다(머리는 거의 가만있고 꼬리로 갈수록 크게).
## 화면에서는 늘 왼쪽을 보고 헤엄친다. 원점은 그림의 가운데.
class Swimmer extends Node2D:
	var texture: Texture2D
	var frames := 1
	var frame := 0
	var head_right := false
	## 꼬리짓의 위상(라디안)과 꼬리 끝이 흔들리는 폭(px).
	var phase := 0.0
	var sway := 8.0
	## 몸을 따라 들어가는 물결의 수(라디안).
	var wave := 4.2

	func frame_size() -> Vector2:
		return Vector2(texture.get_width() / float(frames), texture.get_height())

	## 머리에서 along(0~1)만큼 간 곳이 위아래로 밀리는 양.
	func lift(along: float) -> float:
		return roundf(sin(phase - along * wave) * sway * (0.12 + 0.88 * along * along))

	## 그림 안의 점(프레임 왼쪽 위 기준)이 지금 놓이는 자리 (이 노드 기준).
	func point(at: Vector2) -> Vector2:
		var size := frame_size()
		var x := (size.x - 1.0 - at.x) if head_right else at.x
		return Vector2(x - size.x / 2.0, at.y - size.y / 2.0 + lift(x / size.x))

	func _draw() -> void:
		var size := frame_size()
		var width := int(size.x)
		for x in width:
			var source_x := (width - 1 - x) if head_right else x
			draw_texture_rect_region(
				texture,
				Rect2(x - size.x / 2.0, -size.y / 2.0 + lift(x / size.x), 1, size.y),
				Rect2(frame * size.x + source_x, 0, 1, size.y)
			)


func update_swimmer(swimmer: Swimmer, t: float, at: Vector2, beat := 2.1) -> void:
	swimmer.position = at.round()
	swimmer.phase = t * beat
	swimmer.frame = int(t * 3.0) % swimmer.frames
	swimmer.queue_redraw()


## 물에 떠다니는 작은 알갱이(플랑크톤). 제자리에서 깜빡이며 천천히 흐른다.
func make_motes(root: Node, count: int, area: Rect2, salt: int) -> Array:
	var list: Array = []
	for i in count:
		var mote := Polygon2D.new()
		var size := 2.0 if rnd(i, salt) > 0.8 else 1.0
		mote.polygon = PackedVector2Array([Vector2.ZERO, Vector2(size, 0), Vector2(size, size), Vector2(0, size)])
		mote.color = [MINT, CYAN, TEAL][i % 3]
		root.add_child(mote)
		list.append({"node": mote, "area": area, "at": Vector2(rnd(i, salt + 1), rnd(i, salt + 2)), "rate": 0.25 + rnd(i, salt + 3) * 0.5, "key": rnd(i, salt + 4)})
	return list


## drift: 초당 흐르는 양(px).
func update_motes(list: Array, t: float, drift: Vector2) -> void:
	for mote: Dictionary in list:
		var area: Rect2 = mote["area"]
		var key: float = mote["key"]
		var at: Vector2 = mote["at"] * area.size + drift * t * (0.6 + key * 0.8)
		at += Vector2(sin(t * 0.7 + key * 30.0) * 4.0, cos(t * 0.5 + key * 17.0) * 3.0)
		var node: Polygon2D = mote["node"]
		node.position = (area.position + Vector2(fposmod(at.x, area.size.x), fposmod(at.y, area.size.y))).round()
		node.visible = fposmod(t * mote["rate"] + key, 1.0) < 0.7


## 꼬리가 지나간 자리에 남는 물방울 줄기.
func make_wake(root: Node, count: int) -> Array:
	var list: Array = []
	for i in count:
		var sprite := Sprite2D.new()
		sprite.texture = bubble_texture([3, 3, 4, 5][i % 4])
		root.add_child(sprite)
		list.append(sprite)
	return list


## tail_at: 시각 → 그때 꼬리 끝이 있던 자리. 방울은 태어난 자리에서 위로 뜨며 흩어지다 사라진다.
func update_wake(list: Array, t: float, tail_at: Callable, life := 2.4) -> void:
	for i in list.size():
		var sprite: Sprite2D = list[i]
		var age := fposmod(t + life * i / list.size(), life)
		var born := t - age
		sprite.visible = born >= 0.0 and (age < life * 0.7 or int(age * 14.0 + i) % 2 == 0)
		if not sprite.visible:
			continue
		var origin: Vector2 = tail_at.call(born)
		var spread := Vector2((rnd(i, 141) - 0.3) * 30.0, (rnd(i, 142) - 0.5) * 50.0)
		sprite.position = (origin + spread * (1.0 - exp(-age * 1.5)) + Vector2(sin(age * 3.0 + i) * 3.0, -age * (6.0 + rnd(i, 143) * 10.0))).round()


## 제자리에서 통통 튀는 높이 (말할 때, 기뻐할 때). 바닥을 가로지르는 이동에는 걷는 프레임(walk_tex)을 쓴다.
static func hop(t: float, rate := 9.0, height := 2.0) -> float:
	return -absf(sin(t * rate)) * height
