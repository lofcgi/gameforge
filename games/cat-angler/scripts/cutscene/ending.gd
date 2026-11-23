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
			"sfx": [[1.5, "chime"], [5.0, "cough"], [9.0, "ding"]],
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

func _b_arrive(root: Node2D) -> void:
	build_throne(root)
	n.halo = Sprite2D.new()
	n.halo.texture = glow_texture(15, CYAN)
	n.world.add_child(n.halo)
	n.chest = actor(n.world, "props/p_chest", Vector2(70, 392))
	n.turtle = actor(n.world, "chars/turtle_l_stand", Vector2(0, 388))
	n.cat = actor(n.world, "chars/cat_l_stand", Vector2(0, 390))
	n.ring = Sprite2D.new()
	n.ring.texture = ring_texture(84)
	n.world.add_child(n.ring)
	n.basket = actor(n.world, "props/p_basket")
	n.rise = make_burst(n.world, 8, 3)
	n.burst = make_burst(n.world, 12, 4)
	n.twinkles = make_burst(n.world, 6, 3)


## 고양이(잠수 방울을 쓴)와 바구니를 놓는다. carried 가 1 이면 들고 있고 0 이면 바닥에 내려놓았다.
func _place_cat(t: float, x: float, walking: bool, carried: float) -> void:
	var cat: Sprite2D = n.cat
	var bounce := hop(t, 8.0, 3.0) if walking else 0.0
	cat.position = Vector2(x, 390.0 + bounce).round()
	cat.scale = Vector2(1.0, 1.0 + (0.0 if walking else sin(t * 1.9) * 0.01))
	n.ring.position = cat.position + Vector2(3, -62 + roundf(sin(t * 2.0) * 1.0))
	var held := cat.position + Vector2(40, -14)
	var floor_at := Vector2(x + 72.0, 392.0)
	var arc := sin((1.0 - carried) * PI) * 14.0
	n.basket.position = (floor_at.lerp(held, carried) - Vector2(0, arc)).round()
	n.halo.position = n.basket.position + Vector2(12, -44)
	n.halo.scale = Vector2.ONE * (2.0 if sin(t * 4.0) > 0.0 else 1.0)


func _u_arrive(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 9.0, 20.0, 80.0)), -42.0)
	update_lanterns(n.lanterns, t)
	update_bubbles(n.bubbles, t)
	update_king(t, "chars/king_weak" if t > 4.6 else "chars/king_sick")
	n.chest.visible = false
	# 별주부가 앞장서고 고양이가 바구니를 들고 따라 들어온다.
	var walk := glide(t, 0.0, 3.0)
	var walking := t < 3.0
	var turtle: Sprite2D = n.turtle
	var cheer := hop(t, 11.0, 5.0) if speaking(TURTLE) else 0.0
	turtle.position = Vector2(lerpf(180.0, 478.0, walk), 388.0 + (hop(t, 10.0, 2.0) if walking else cheer)).round()
	_place_cat(t, lerpf(40.0, 330.0, walk), walking, 1.0 - glide(t, 3.2, 3.7))
	update_burst(n.burst, t - 3.6, n.basket.position + Vector2(12, -44), 46.0, 0.9)
	update_burst(n.rise, -1.0, Vector2.ZERO)
	update_burst(n.twinkles, -1.0, Vector2.ZERO)


func _u_better(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 11.4, 80.0, 52.0)), -42.0 + roundf(pulse(t, 1.6, 0.3) * 2.0))
	update_lanterns(n.lanterns, t + 9.0)
	update_bubbles(n.bubbles, t + 9.0)
	var healed := t >= 1.6
	update_king(t, "chars/king_better" if healed else "chars/king_weak", [5.0])
	# 나아지는 순간 몸이 한 번 부푼다.
	var pop := pulse(t, 1.6, 0.35) * 0.08
	n.king.scale += Vector2(-pop * 0.5, pop)
	_place_cat(t, 330.0, false, 0.0)
	# 별주부: 기뻐 뛰다가, 화면 밖으로 달려가 보물 상자를 밀고 돌아온다.
	var fetch := glide(t, 7.0, 7.8)
	var push := glide(t, 8.0, 8.8)
	var turtle: Sprite2D = n.turtle
	var turtle_x := lerpf(lerpf(478.0, -10.0, fetch), 196.0, push)
	var lively := (t > 1.6 and t < 4.6) or (t > 7.0 and t < 8.8)
	turtle.position = Vector2(turtle_x, 388.0 + (hop(t, 11.0, 4.0) if lively else 0.0)).round()
	turtle.flip_h = t > 7.0 and t < 7.9
	# 바구니의 빛이 용왕에게 올라간다.
	var from: Vector2 = n.basket.position + Vector2(12, -44)
	var to: Vector2 = n.king.position + Vector2(-30, -110)
	for i in n.rise.size():
		var spark: Sprite2D = n.rise[i]
		var along: float = (t - 0.2 - i * 0.12) / 1.1
		spark.visible = along > 0.0 and along < 1.0
		spark.position = (from.lerp(to, along) + Vector2(sin(along * 9.0 + i) * 8.0, -sin(along * PI) * 40.0)).round()
	update_burst(n.burst, t - 1.6, to, 80.0, 1.0)
	if healed and t < 4.8:
		update_twinkles(n.twinkles, t, to + Vector2(0, 10), Vector2(150, 110))
	else:
		update_burst(n.twinkles, -1.0, Vector2.ZERO)
	var chest: Sprite2D = n.chest
	chest.visible = t > 7.95
	chest.texture = tex("props/p_chest_open" if t >= 9.0 else "props/p_chest")
	chest.position = Vector2(lerpf(46.0, 252.0, push), 392.0 - roundf(pulse(t, 9.0, 0.25) * 5.0))
	if t >= 9.0:
		update_twinkles(n.twinkles, t, chest.position + Vector2(0, -52), Vector2(70, 40))


# ---------- 3. 다음 전설 ----------

func _b_next(root: Node2D) -> void:
	build_deep(root, "props/legend_b")
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


func _u_next(t: float) -> void:
	n.world.position.x = -roundf(t * 4.0)
	n.near.position.x = -roundf(t * 8.0)
	update_school(n.school, t)
	update_bubbles(n.bubbles, t)
	var legend: Sprite2D = n.legend
	legend.position = Vector2(glide(t, -1.5, 7.0, 860.0, 480.0), 200.0 + sin(t * 0.8) * 10.0).round()
	legend.rotation = sin(t * 0.8 + 1.0) * 0.02
	legend.scale = Vector2(1.0 + sin(t * 2.0) * 0.012, 1.0)
	# 이마의 초롱과 눈이 번갈아 반짝인다.
	n.glint.position = legend.position + (Vector2(-141, -24) if int(t * 0.8) % 2 == 0 else Vector2(-103, -12))
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
