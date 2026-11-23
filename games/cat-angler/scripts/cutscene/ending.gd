extends CutsceneStage
## 닫는 컷신 (데모의 끝). 컷의 내용과 시간표는 design/cutscene-script.md 와 같아야 한다.


func _shots() -> Array[Dictionary]:
	return [
		{
			"dur": 9.0, "build": _b_arrive, "update": _u_arrive, "sub_top": true, "music": "cutscene_ending",
			"subs": [
				[0.6, 3.6, "", "첫 번째 전설의 물고기가 용궁에 닿았습니다."],
				[4.0, 8.6, TURTLE, "전하! 뭍의 사냥꾼이 해냈나이다!"],
			],
			"sfx": [[0.4, "bubbles"], [3.5, "chime"]],
		},
		{
			"dur": 11.4, "build": _b_arrive, "update": _u_better, "sub_top": true, "enter": "cut",
			"subs": [
				[2.0, 4.8, KING, "오오… 한결 낫구나!"],
				[5.5, 7.4, KING, "…콜록. 아직 조금 남았느니라."],
				[7.9, 11.0, KING, "약속대로 보물과 새 낚싯대를 주마."],
			],
			"sfx": [[1.5, "chime"], [5.0, "cough"], [9.7, "ding"]],
		},
		{
			"dur": 10.0, "build": _b_next, "update": _u_next,
			"subs": [
				[0.6, 4.3, TURTLE, "헌데 더 먼 바다에, 더 큰 전설이 있다 하옵니다."],
				[4.9, 6.6, CAT, "…더 큰 놈?"],
				[6.9, 9.4, CAT, "좋아. 다음."],
			],
			"sfx": [[0.5, "bubbles"], [5.4, "ding"]],
		},
	]


# ---------- 1·2. 용궁에 바친다, 용왕이 나아진다 ----------

const CAT_STOP := 216.0
const TURTLE_STOP := 484.0
## 고양이가 밀고 온 전설의 물고기가 멈춰 떠 있는 자리(가운데).
const FISH_REST := Vector2(364, 326)

func _b_arrive(root: Node2D) -> void:
	build_throne(root)
	n.chest = actor(n.world, "props/p_chest", Vector2(-40, 392))
	n.turtle = actor(n.world, "chars/turtle_l_stand", Vector2(0, 388))
	n.cat = actor(n.world, "chars/cat_l_stand", Vector2(0, 390))
	n.ring = Sprite2D.new()
	n.ring.texture = ring_texture(84)
	n.world.add_child(n.ring)
	# 게임에서 낚은 바로 그 전설의 물고기. 용왕 쪽(오른쪽)을 보고 떠 있다.
	n.fish = Swimmer.new()
	n.fish.texture = game_tex("fish/legend_swim.png")
	n.fish.frames = 4
	n.fish.head_right = true
	n.fish.sway = 3.0
	n.fish.scale.x = -1.0
	n.world.add_child(n.fish)
	n.rise = make_burst(n.world, 8, 3)
	n.burst = make_burst(n.world, 12, 4)
	n.twinkles = make_burst(n.world, 6, 3)
	n.shine = make_burst(n.world, 9, 3)


## 잠수 방울을 쓴 고양이. pose 는 "stand" | "reach" | "arms" | "walk".
func _place_cat(t: float, x: float, pose: String) -> void:
	var cat: Sprite2D = n.cat
	if pose == "walk":
		cat.texture = walk_tex("cat_l", x, false, CAT_STRIDE)
	elif pose == "stand" and fposmod(t + 0.4, 2.9) > 2.76:
		cat.texture = tex("chars/cat_l_blink")
	else:
		cat.texture = tex("chars/cat_l_" + pose)
	cat.position = Vector2(x, 390.0).round()
	n.ring.position = cat.position + Vector2(2, -64 + roundf(sin(t * 2.0) * 1.0))


## 전설의 물고기. glowing 이면 둘레에 빛 알갱이가 반짝인다.
func _place_fish(t: float, at: Vector2, glowing: bool) -> void:
	var fish: Swimmer = n.fish
	update_swimmer(fish, t, at + Vector2(0, sin(t * 1.7) * 3.0), 3.0)
	if glowing:
		update_twinkles(n.shine, t, fish.position, Vector2(180, 96))
	else:
		update_burst(n.shine, -1.0, Vector2.ZERO)


func _u_arrive(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 9.0, 20.0, 80.0)), -42.0)
	update_lanterns(n.lanterns, t)
	update_bubbles(n.bubbles, t)
	update_king(t, "chars/king_weak" if t > 4.6 else "chars/king_sick")
	n.chest.visible = false
	# 별주부가 앞장서고, 고양이가 전설의 물고기를 두 손으로 밀며 따라 들어온다.
	var walk := glide(t, 0.0, 3.0)
	var walking := t < 3.0
	var turtle: Sprite2D = n.turtle
	var turtle_x := lerpf(336.0, TURTLE_STOP, walk)
	var cheer := hop(t, 11.0, 5.0) if speaking(TURTLE) else 0.0
	turtle.texture = walk_tex("turtle_l", turtle_x, false, TURTLE_STRIDE) if walking else tex("chars/turtle_l_stand")
	turtle.position = Vector2(turtle_x, 388.0 + cheer).round()
	var cat_x := lerpf(40.0, CAT_STOP, walk)
	var pose := "walk"
	if t >= 5.2:
		pose = "arms"
	elif t >= 3.9:
		pose = "stand"
	elif t >= 3.0:
		pose = "reach"
	_place_cat(t, cat_x, pose)
	# 멈춰 서서 한 번 더 밀면 물고기가 용왕 앞으로 미끄러져 간다.
	var carried := Vector2(cat_x + 122.0, FISH_REST.y)
	_place_fish(t, carried.lerp(FISH_REST, glide(t, 3.2, 3.9)), true)
	update_burst(n.burst, t - 3.7, FISH_REST, 70.0, 0.9)
	update_burst(n.rise, -1.0, Vector2.ZERO)
	update_burst(n.twinkles, -1.0, Vector2.ZERO)


## 별주부가 보물을 가지러 가는 길. 기침 소리(5.0초)에 멈춰 돌아봤다가 다시 달려 화면 밖으로 나가고, 상자를 밀고 돌아온다.
func _fetch_x(t: float) -> float:
	if t < 5.0:
		return TURTLE_STOP - 135.0 * clampf(t - 3.5, 0.0, 1.5)
	if t < 8.0:
		return 281.5 - 142.5 * clampf(t - 5.6, 0.0, 2.2)
	return lerpf(-32.0, 78.0, clampf((t - 8.0) / 1.5, 0.0, 1.0))


func _u_better(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 11.4, 80.0, 52.0)), -42.0 + roundf(pulse(t, 1.6, 0.3) * 2.0))
	update_lanterns(n.lanterns, t + 9.0)
	update_bubbles(n.bubbles, t + 9.0)
	var healed := t >= 1.6
	update_king(t, "chars/king_better" if healed else "chars/king_weak", [5.0])
	# 나아지는 순간 몸이 한 번 부푼다.
	var pop := pulse(t, 1.6, 0.35) * 0.08
	n.king.scale += Vector2(-pop * 0.5, pop)
	_place_cat(t, CAT_STOP, "arms" if t >= 5.3 else "stand")
	# 물고기의 빛이 용왕에게 건너가고, 물고기는 빛을 잃은 채 그 자리에 떠 있다.
	_place_fish(t, FISH_REST, t < 1.3)
	var from: Vector2 = FISH_REST
	var to: Vector2 = KING_AT + Vector2(-34, -128)
	for i in n.rise.size():
		var spark: Sprite2D = n.rise[i]
		var along: float = (t - 0.2 - i * 0.12) / 1.1
		spark.visible = along > 0.0 and along < 1.0
		spark.position = (from.lerp(to, along) + Vector2(sin(along * 9.0 + i) * 8.0, -sin(along * PI) * 40.0)).round()
	update_burst(n.burst, t - 1.6, to, 80.0, 1.0)
	if healed and t < 4.8:
		update_twinkles(n.twinkles, t, to + Vector2(0, 10), Vector2(170, 120))
	else:
		update_burst(n.twinkles, -1.0, Vector2.ZERO)
	# 별주부: 기뻐 뛰다가 보물 상자를 가지러 달려간다.
	var turtle: Sprite2D = n.turtle
	var x := _fetch_x(t)
	var moving := absf(_fetch_x(t + 1.0 / TICKS) - x) > 0.01
	var pushing := t >= 8.0
	turtle.flip_h = t >= 3.5 and not pushing and not (t >= 5.0 and t < 5.6)
	turtle.texture = walk_tex("turtle_l", x, turtle.flip_h, TURTLE_STRIDE) if moving else tex("chars/turtle_l_stand")
	var joy := hop(t, 11.0, 4.0) if (t > 1.6 and t < 3.3) else 0.0
	turtle.position = Vector2(x, 388.0 + joy - pulse(t, 5.02, 0.3) * 7.0).round()
	var chest: Sprite2D = n.chest
	var opened := t >= 9.7
	chest.visible = pushing
	chest.texture = tex("props/p_chest_open" if opened else "props/p_chest")
	chest.position = Vector2(x + 62.0, 392.0 - roundf(pulse(t, 9.7, 0.25) * 5.0)).round()
	if opened:
		update_twinkles(n.twinkles, t, chest.position + Vector2(0, -52), Vector2(70, 40))


# ---------- 3. 다음 전설 ----------

func _b_next(root: Node2D) -> void:
	build_deep(root, "props/legend_b", 1, false)
	n.legend.sway = 10.0
	n.legend.wave = 3.4
	# 고양이의 얼굴이 뜨는 작은 창.
	n.inset = Control.new()
	n.inset.clip_contents = true
	n.inset.size = Vector2(176, 132)
	root.add_child(n.inset)
	var back := ColorRect.new()
	back.color = Color("426a96")
	back.size = n.inset.size
	n.inset.add_child(back)
	n.inset_bubbles = make_bubbles(n.inset, 6, Rect2(0, 0, 176, 132), 77)
	n.cat = actor(n.inset, "chars/cat_m_bored", Vector2(86, 208))
	n.burst = make_burst(n.inset, 8, 3)
	var frame := ReferenceRect.new()
	frame.border_color = PAPER
	frame.border_width = 2.0
	frame.editor_only = false
	frame.size = n.inset.size
	n.inset.add_child(frame)


## 화면에 다 들어오지 않는 큰 그림자의 가운데.
func _next_at(t: float) -> Vector2:
	return Vector2(glide(t, -1.5, 8.0, 990.0, 600.0), 184.0 + sin(t * 0.8) * 9.0 + sin(t * 0.31 + 2.0) * 5.0)


func _next_fin(t: float) -> Vector2:
	return _next_at(t) + Vector2(60.0, 70.0 + sin(t * 1.6 - 2.0) * 5.0)


func _u_next(t: float) -> void:
	var drift := roundf(sin(t * 0.4 + 1.0) * 5.0)
	n.world.position = Vector2(-roundf(t * 4.0), -14.0 + drift)
	n.near.position = Vector2(-roundf(t * 8.0), roundf(drift * 1.6))
	update_school(n.school, t)
	update_bubbles(n.bubbles, t)
	update_motes(n.far_motes, t, Vector2(4.0, -2.0))
	update_motes(n.near_motes, t, Vector2(10.0, -5.0))
	var legend: Swimmer = n.legend
	update_swimmer(legend, t, _next_at(t), 1.6)
	update_wake(n.wake, t, _next_fin)
	# 이마의 초롱과 눈이 번갈아 반짝인다.
	n.glint.position = legend.position + legend.point(Vector2(8, 52) if int(t * 0.8) % 2 == 0 else Vector2(92, 72))
	n.glint.visible = fposmod(t, 1.25) < 0.3
	# 고양이 창이 아래에서 올라온다.
	var inset: Control = n.inset
	inset.position = Vector2(18.0, roundf(glide(t, 4.5, 4.9, 370.0, 146.0)))
	update_bubbles(n.inset_bubbles, t)
	var face := "bored"
	if t >= 5.4 and t < 6.9:
		face = "sparkle"
	elif t >= 6.9:
		face = "smirk"
	if face == "bored" and fposmod(t, 2.7) > 2.56:
		face = "blink"
	var cat: Sprite2D = n.cat
	cat.texture = tex("chars/cat_m_" + face)
	var pop := pulse(t, 5.4, 0.3) * 0.1 + pulse(t, 6.9, 0.25) * 0.04
	cat.scale = Vector2(1.0 - pop * 0.5, 1.0 + pop)
	cat.position = Vector2(86.0, 208.0 + (hop(t, 11.0, 2.0) if speaking(CAT) else 0.0)).round()
	update_burst(n.burst, t - 5.4, Vector2(78, 80), 80.0, 0.9)
