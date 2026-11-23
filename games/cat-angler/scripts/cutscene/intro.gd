extends CutsceneStage
## 여는 컷신. 컷의 내용과 시간표는 design/cutscene-script.md 와 같아야 한다.
## 컷마다 build(노드를 놓는다)와 update(t 초의 모습으로 만든다) 한 쌍이다.


func _shots() -> Array[Dictionary]:
	return [
		{
			"dur": 8.6, "build": _b_descent, "update": _u_descent, "music": "cutscene_intro",
			"subs": [[0.8, 4.0, "", "먼 바다, 아주 깊은 곳."], [4.4, 8.2, "", "빛이 닿지 않는 그 아래에 용궁이 있었습니다."]],
			"sfx": [[0.6, "bubbles"], [5.2, "bubbles"]],
		},
		{
			"dur": 9.0, "build": _b_palace, "update": _u_palace,
			"subs": [[0.7, 4.0, "", "옥빛 기와에 자개 마당. 고요하고 아름다운 곳."], [4.4, 8.6, "", "…다만 요즘은 조금 시끄러웠습니다."]],
			"sfx": [[6.6, "cough"], [6.7, "bubbles"]],
		},
		{
			"dur": 10.6, "build": build_throne, "update": _u_sickbed, "sub_top": true,
			"subs": [
				[0.6, 3.4, "", "용왕님이 그만 병이 나신 겁니다."],
				[3.8, 7.0, KING, "콜록, 콜록… 먹은 약만 벌써 삼백 첩이니라."],
				[7.3, 10.3, TURTLE, "전하! 이제 남은 약은 딱 하나뿐이옵니다."],
			],
			"sfx": [[1.4, "cough"], [4.0, "cough"]],
		},
		{
			"dur": 10.0, "build": _b_legend, "update": _u_legend, "enter": "cut",
			"subs": [
				[0.6, 4.3, TURTLE, "깊은 바다에 사는 전설의 물고기. 그것이 유일한 영약이옵니다."],
				[4.7, 9.5, TURTLE, "헌데 이 녀석, 입맛이 까다로워 뭍에서 난 미끼만 뭅니다."],
			],
			"sfx": [[5.9, "chime"], [1.0, "bubbles"]],
		},
		{
			"dur": 4.6, "build": build_throne, "update": _u_bow, "sub_top": true,
			"subs": [[0.4, 4.2, TURTLE, "소신이 뭍에 올라 사냥꾼을 구해 오겠나이다!"]],
		},
		{
			"dur": 6.2, "build": _b_ascend, "update": _u_ascend, "enter": "cut",
			"subs": [[0.8, 5.6, "", "그리하여 별주부는 난생처음 뭍으로 향했습니다."]],
			"sfx": [[0.3, "bubbles"], [3.0, "bubbles"]],
		},
		{
			"dur": 10.4, "build": _b_shore, "update": _u_shore, "enter": "wave", "sub_top": true, "music": "cutscene_intro_land",
			"subs": [[0.8, 4.4, "", "뭍에는 사냥꾼이 많았습니다."], [6.6, 9.9, TURTLE, "토끼는… 예전에 일이 좀 있었고."]],
			"sfx": [[0.0, "wave"], [5.4, "splash"]],
		},
		{
			"dur": 16.2, "build": _b_cat, "update": _u_cat, "enter": "cut", "sub_top": true,
			"subs": [
				[1.6, 4.5, TURTLE, "거기 사냥꾼 양반! 용왕님을 구해 주시오!"],
				[4.9, 6.8, CAT, "…관심 없어."],
				[7.2, 10.2, TURTLE, "전설의 물고기를 낚아야 하오! 보물도 드리리다!"],
				[10.7, 12.6, CAT, "…물고기?"],
				[12.9, 15.8, CAT, "세상 물고기는 전부 내가 낚을 거거든."],
			],
			"sfx": [[1.1, "splash"], [10.4, "ding"]],
		},
		{
			"dur": 5.0, "build": _b_deal, "update": _u_deal, "enter": "cut",
			"subs": [[1.3, 4.7, CAT, "충성도 의리도 없어. 하지만 거래라면 좋아."]],
			"sfx": [[0.85, "chime"], [1.0, "shake"]],
		},
		{
			"dur": 9.0, "build": _b_depart, "update": _u_depart, "enter": "wave",
			"subs": [[0.8, 4.2, "", "그렇게 고양이는 바다로 나갔습니다."], [4.6, 8.5, "", "용왕님을 위해서는 아니고, 그냥 낚고 싶어서."]],
			"sfx": [[0.0, "wave"], [1.2, "splash"]],
		},
	]


# ---------- 1. 깊은 바다로 내려간다 ----------

func _b_descent(root: Node2D) -> void:
	n.clear()
	n.far = group(root)
	n.world = group(root)
	layer_sprite(n.world, "bg/descent")
	n.shafts = make_shafts(n.world, [150.0, 250.0, 360.0, 470.0], 170, 380, Color(PAPER, 0.09))
	n.school_a = make_school(n.world, "props/p_fish_a", 6, Rect2(0, 330, 640, 150), 26.0, 3)
	n.school_b = make_school(n.world, "props/p_fish_b", 5, Rect2(0, 560, 640, 160), -34.0, 9)
	n.jelly = [actor(n.world, "props/p_jelly_a", Vector2(110, 800)), actor(n.world, "props/p_jelly_b", Vector2(520, 870)), actor(n.world, "props/p_jelly_b", Vector2(250, 930))]
	n.lanterns = make_lanterns(n.world, [
		Vector2(352, 968), Vector2(395, 950), Vector2(432, 978), Vector2(518, 938), Vector2(552, 946), Vector2(586, 946), Vector2(612, 940),
	], 4)
	n.near = group(root)
	n.bubbles = make_bubbles(n.near, 22, Rect2(0, 120, 640, 1300), 1)


func _u_descent(t: float) -> void:
	var cam := glide(t, 0.8, 7.9, 0.0, 778.0)
	n.world.position.y = -roundf(cam)
	n.near.position.y = -roundf(cam * 1.3)
	update_shafts(n.shafts, t)
	update_school(n.school_a, t)
	update_school(n.school_b, t)
	update_bubbles(n.bubbles, t)
	update_lanterns(n.lanterns, t)
	_float_jelly(t)


func _float_jelly(t: float) -> void:
	for i in n.jelly.size():
		var jelly: Sprite2D = n.jelly[i]
		var beat := sin(t * 2.2 + i * 1.7)
		# 오므렸다 펴며 조금씩 떠오른다.
		jelly.scale = Vector2(1.0 - beat * 0.08, 1.0 + beat * 0.1)
		jelly.position.y = [800.0, 870.0, 930.0][i] - t * 3.0 + roundf(beat * 3.0)


# ---------- 2. 용궁 전경 ----------

func _b_palace(root: Node2D) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/palace")
	n.shafts = make_shafts(n.world, [300.0, 360.0, 430.0], -10, 240, Color(MINT, 0.08))
	n.lanterns = make_lanterns(n.world, [
		Vector2(165, 303), Vector2(236, 284), Vector2(542, 293), Vector2(506, 330), Vector2(715, 292), Vector2(749, 331),
	], 9)
	n.school = make_school(n.world, "props/p_fish_a", 7, Rect2(100, 40, 760, 110), 22.0, 13)
	n.jelly = [actor(n.world, "props/p_jelly_a", Vector2(300, 150)), actor(n.world, "props/p_jelly_b", Vector2(470, 110)), actor(n.world, "props/p_jelly_b", Vector2(120, 120))]
	n.puff = make_puff(n.world, 7)
	n.bubbles = make_bubbles(n.world, 12, Rect2(0, 0, 848, 340), 5)
	n.fg = layer_sprite(root, "bg/palace_fg", Vector2(0, 6))
	n.near = group(root)
	n.near_bubbles = make_bubbles(n.near, 8, Rect2(0, 0, 960, 380), 9)


func _u_palace(t: float) -> void:
	var cam := glide(t, -1.5, 9.5, 0.0, 208.0)
	# 대전 안에서 기침 소리가 나면 화면이 한 번 흔들린다.
	var shake := roundf(sin(t * 60.0) * 2.0) if (t > 6.6 and t < 6.9) else 0.0
	n.world.position = Vector2(-roundf(cam), shake)
	n.fg.position.x = -roundf(cam * 1.54)
	n.near.position.x = -roundf(cam * 1.54)
	update_shafts(n.shafts, t)
	update_lanterns(n.lanterns, t)
	update_school(n.school, t)
	update_bubbles(n.bubbles, t)
	update_bubbles(n.near_bubbles, t * 1.4)
	update_puff(n.puff, t - 6.6, Vector2(633, 232), Vector2(0, -1))
	for i in n.jelly.size():
		var jelly: Sprite2D = n.jelly[i]
		var beat := sin(t * 2.0 + i * 2.1)
		jelly.scale = Vector2(1.0 - beat * 0.08, 1.0 + beat * 0.1)
		jelly.position = Vector2([300.0, 470.0, 120.0][i] + t * 4.0, [150.0, 110.0, 120.0][i] - t * 3.0 + beat * 3.0).round()


# ---------- 3. 병든 용왕 ----------

func _u_sickbed(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 11.0, 10.0, 80.0)), -42.0)
	if not n.has("turtle"):
		n.turtle = actor(n.world, "chars/turtle_l_stand", Vector2(400, 388))
	update_lanterns(n.lanterns, t)
	update_bubbles(n.bubbles, t)
	update_king(t, "chars/king_sick", [1.4, 4.0])
	var turtle: Sprite2D = n.turtle
	# 발을 동동 구르며 왔다 갔다 하다가, 아뢸 때는 용왕 앞에 선다.
	var pace := sin(t * 1.3) * 34.0
	var settle := glide(t, 6.6, 7.3)
	var x := lerpf(420.0 + pace, 468.0, settle)
	var facing_left := cos(t * 1.3) < 0.0 and settle < 0.5
	var startle := pulse(t, 1.45, 0.35) + pulse(t, 4.05, 0.35)
	if startle > 0.0:
		facing_left = false
	var bounce := hop(t, 9.0, 2.0) if settle < 1.0 else (hop(t, 12.0, 2.0) if speaking(TURTLE) else 0.0)
	turtle.flip_h = facing_left
	turtle.position = Vector2(x, 388.0 + bounce - startle * 9.0).round()
	turtle.scale = Vector2(1.0, 1.0 + startle * 0.08)


# ---------- 4. 전설의 물고기 ----------

func _b_legend(root: Node2D) -> void:
	build_deep(root, "props/legend_a")
	n.line = Line2D.new()
	n.line.width = 1.0
	n.line.default_color = CREAM
	n.world.add_child(n.line)
	n.halo = Sprite2D.new()
	n.halo.texture = glow_texture(11, ORANGE)
	n.world.add_child(n.halo)
	n.hook = actor(n.world, "props/p_hook")


func _u_legend(t: float) -> void:
	n.world.position.x = -roundf(t * 6.4)
	n.near.position.x = -roundf(t * 10.0)
	update_school(n.school, t)
	update_bubbles(n.bubbles, t)
	# 그림자가 오른쪽에서 천천히 들어오고, 미끼가 내려오면 그쪽으로 다가간다.
	var x := glide(t, -1.0, 6.0, 900.0, 520.0) - glide(t, 6.6, 9.6, 0.0, 120.0)
	var y := 200.0 + sin(t * 0.9) * 9.0
	var legend: Sprite2D = n.legend
	legend.position = Vector2(x, y).round()
	legend.rotation = sin(t * 0.9 + 1.2) * 0.025
	legend.scale = Vector2(1.0 + sin(t * 2.4) * 0.012, 1.0)
	var eye := legend.position + Vector2(-131, -4)
	n.glint.position = eye
	n.glint.visible = (t > 6.7 and t < 7.5 and int(t * 12.0) % 2 == 0) or (t > 2.6 and t < 2.9)
	# 뭍의 미끼를 단 낚싯바늘.
	var hook_x := 190.0 + t * 6.4 * 0.0
	var hook_y := glide(t, 4.9, 6.2, -40.0, 190.0) + sin(t * 2.3) * 2.0
	var sway := sin(t * 1.4) * 3.0
	n.hook.position = Vector2(hook_x + sway, hook_y).round()
	n.line.points = PackedVector2Array([Vector2(hook_x + 2.0, -10.0), Vector2(hook_x + sway + 2.0, hook_y - 23.0)])
	n.halo.position = n.hook.position + Vector2(2, -7)
	n.halo.visible = t > 5.9
	n.halo.scale = Vector2.ONE * (2.0 if sin(t * 5.0) > 0.2 else 1.0)


# ---------- 5. 별주부가 나선다 ----------

func _u_bow(t: float) -> void:
	n.world.position = Vector2(-roundf(glide(t, 0.0, 4.6, 80.0, 56.0)), -42.0)
	if not n.has("turtle"):
		n.turtle = actor(n.world, "chars/turtle_l_stand", Vector2(468, 388))
	update_lanterns(n.lanterns, t + 3.0)
	update_bubbles(n.bubbles, t + 3.0)
	update_king(t, "chars/king_weak" if t > 1.6 else "chars/king_sick")
	# 용왕이 고개를 끄덕인다.
	n.king.position.y = 338.0 + roundf(pulse(t, 2.5, 0.5) * 3.0)
	var turtle: Sprite2D = n.turtle
	var bowing := t > 1.0 and t < 2.4
	turtle.texture = tex("chars/turtle_l_bow" if bowing else "chars/turtle_l_stand")
	var squash := pulse(t, 1.0, 0.25) * 0.1 + pulse(t, 2.4, 0.25) * 0.1
	turtle.scale = Vector2(1.0 + squash, 1.0 - squash)
	# 돌아서서 달려 나간다.
	var leaving := t > 3.1
	turtle.flip_h = leaving
	var run := glide(t, 3.2, 4.6, 0.0, 190.0)
	var bounce := hop(t, 14.0, 3.0) if leaving else (hop(t, 12.0, 2.0) if (speaking(TURTLE) and not bowing) else 0.0)
	turtle.position = Vector2(468.0 - run, 388.0 + bounce - pulse(t, 3.0, 0.3) * 8.0).round()


# ---------- 6. 뭍으로 올라간다 ----------

func _b_ascend(root: Node2D) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/descent")
	n.shafts = make_shafts(n.world, [150.0, 250.0, 360.0, 470.0], 170, 380, Color(PAPER, 0.09))
	n.school_a = make_school(n.world, "props/p_fish_a", 6, Rect2(0, 330, 640, 150), 26.0, 3)
	n.school_b = make_school(n.world, "props/p_fish_b", 5, Rect2(0, 560, 640, 160), -34.0, 9)
	n.trail = group(root)
	n.trail_bubbles = make_bubbles(n.trail, 9, Rect2(-16, 0, 32, 150), 71)
	n.turtle = actor(root, "chars/turtle_l_swim_a")
	n.near = group(root)
	n.bubbles = make_bubbles(n.near, 22, Rect2(0, 120, 640, 1300), 1)


func _u_ascend(t: float) -> void:
	var cam := glide(t, 0.0, 5.7, 778.0, 0.0)
	n.world.position.y = -roundf(cam)
	n.near.position.y = -roundf(cam * 1.3)
	update_shafts(n.shafts, t)
	update_school(n.school_a, t)
	update_school(n.school_b, t)
	update_bubbles(n.bubbles, t)
	# 팔을 저을 때마다 쑥 올라간다.
	var stroke := fposmod(t, 0.6) / 0.6
	var pulling := stroke > 0.5
	var turtle: Sprite2D = n.turtle
	turtle.texture = tex("chars/turtle_l_swim_b" if pulling else "chars/turtle_l_swim_a")
	var surge := sin(stroke * TAU) * 5.0
	var rise := glide(t, 4.4, 6.0, 0.0, 70.0)
	turtle.position = Vector2(320.0 + sin(t * 1.1) * 18.0, 262.0 - surge - rise).round()
	turtle.scale = Vector2(1.0 - sin(stroke * TAU) * 0.05, 1.0 + sin(stroke * TAU) * 0.07)
	n.trail.position = turtle.position + Vector2(0, 4)
	# 지나온 자리에 남는 방울은 아래로 처진다.
	for i in n.trail_bubbles.size():
		var bubble: Dictionary = n.trail_bubbles[i]
		var age := fposmod(bubble["phase"] + t * 0.9, 1.0)
		(bubble["node"] as Sprite2D).position = Vector2(bubble["x"] + sin(t * 3.0 + i) * 3.0, age * 130.0).round()
		(bubble["node"] as Sprite2D).visible = age < 0.85


# ---------- 7. 뭍 ----------

func _b_shore(root: Node2D) -> void:
	n.clear()
	n.far = group(root)
	n.world = group(root)
	layer_sprite(n.world, "bg/shore")
	n.clouds = []
	for i in 3:
		n.clouds.append(layer_sprite(n.world, "props/p_cloud", Vector2(260 + i * 210, 30 + (i % 2) * 34)))
	n.cat = actor(n.world, "chars/cat_s_sit_a", Vector2(452, 251))
	n.line = Line2D.new()
	n.line.width = 1.0
	n.line.default_color = PAPER
	n.world.add_child(n.line)
	n.bobber = _dot(n.world, 3, ORANGE)
	n.turtle = Sprite2D.new()
	n.turtle.texture = tex("chars/turtle_l_stand")
	n.turtle.centered = false
	n.turtle.region_enabled = true
	n.world.add_child(n.turtle)
	n.ripple = [_bar(n.world, 22, PAPER), _bar(n.world, 14, PAPER)]
	n.splash = actor(n.world, "props/p_splash", Vector2(594, 332))
	n.wave = layer_sprite(n.world, "bg/wave_fg_shore", Vector2(214, 326))
	n.glints = []
	for i in 8:
		n.glints.append(_bar(n.world, 5 + int(rnd(i, 95) * 8.0), PAPER))
	n.mark = Sprite2D.new()
	n.mark.texture = _mark_texture()
	n.world.add_child(n.mark)
	n.leaves = []
	for i in 6:
		var leaf := Sprite2D.new()
		leaf.texture = _leaf_texture()
		n.world.add_child(leaf)
		n.leaves.append(leaf)


func _u_shore(t: float) -> void:
	var cam := glide(t, 0.6, 5.2, 0.0, 188.0) + glide(t, 5.2, 10.4, 0.0, 20.0)
	n.world.position.x = -roundf(cam)
	n.wave.position = Vector2(214.0 + roundf(sin(t * 1.1) * 6.0), 326.0 + roundf(sin(t * 1.7) * 2.0))
	for i in n.glints.size():
		var glint: Polygon2D = n.glints[i]
		var cycle := fposmod(t * (0.4 + rnd(i, 96) * 0.3) + rnd(i, 97), 1.0)
		glint.visible = cycle < 0.5
		glint.position = Vector2(250.0 + rnd(i, 98) * 170.0 + cycle * 10.0, 286.0 + rnd(i, 99) * 34.0).round()
	for i in n.clouds.size():
		(n.clouds[i] as Sprite2D).position.x = roundf(260.0 + i * 210.0 - t * (3.0 + i) + cam * 0.5)
	# 솔잎이 흩날린다.
	for i in n.leaves.size():
		var leaf: Sprite2D = n.leaves[i]
		var fall := fposmod(rnd(i, 81) * 260.0 + t * (24.0 + rnd(i, 82) * 14.0), 260.0)
		leaf.position = Vector2(40.0 + rnd(i, 83) * 260.0 + sin(t * 2.0 + i * 1.9) * 10.0 + fall * 0.25, 40.0 + fall).round()
		leaf.flip_h = int(t * 3.0 + i) % 2 == 0
		leaf.visible = fall < 190.0
	# 고양이: 꼬리가 가끔 올라갔다 내려온다. 찌가 까딱거린다.
	var cat: Sprite2D = n.cat
	var tail_up := fposmod(t, 1.7) < 0.45
	cat.texture = tex("chars/cat_s_sit_b" if tail_up else "chars/cat_s_sit_a")
	cat.offset.x = -cat.texture.get_width() + 27.0
	var tip := cat.position + Vector2(25, -58)
	var bob := roundf(sin(t * 3.0) * 1.0)
	var float_at := Vector2(tip.x + 20.0, 290.0 + bob)
	n.line.points = PackedVector2Array([tip, float_at])
	n.bobber.position = float_at + Vector2(-1, -1)
	# 별주부가 물 위로 고개를 내민다.
	var up := glide(t, 5.4, 5.8, 0.0, 78.0) + pulse(t, 5.4, 0.5) * 6.0
	var water_y := 364.0
	var turtle: Sprite2D = n.turtle
	var shown := clampf(up + sin(t * 3.0) * 1.5, 0.0, 84.0)
	turtle.region_rect = Rect2(0, 0, 75, roundf(shown))
	turtle.position = Vector2(556, water_y - roundf(shown))
	turtle.visible = shown >= 1.0
	# 두리번거리다가 고양이를 본다.
	var looking := t > 6.0 and t < 8.4
	turtle.flip_h = (int((t - 6.0) / 0.6) % 2 == 0) if looking else t >= 8.4
	n.splash.visible = t > 5.4 and t < 5.75
	n.splash.scale = Vector2.ONE * (1.0 + pulse(t, 5.4, 0.35) * 0.3)
	for i in n.ripple.size():
		var bar: Polygon2D = n.ripple[i]
		bar.visible = false
		bar.position = Vector2(594.0 - (11.0 - i * 4.0) + sin(t * 2.0 + i) * 2.0, water_y + i * 3.0).round()
	n.mark.visible = t > 8.5 and t < 9.6
	n.mark.position = Vector2(598, water_y - 96.0 - roundf(pulse(t, 8.5, 0.3) * 5.0))


# ---------- 8. 고양이 ----------

func _b_cat(root: Node2D) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/pier")
	n.clouds = [layer_sprite(n.world, "props/p_cloud", Vector2(520, 104)), layer_sprite(n.world, "props/p_cloud", Vector2(300, 92))]
	n.turtle = Sprite2D.new()
	n.turtle.texture = tex("chars/turtle_m_calm")
	n.turtle.centered = false
	n.turtle.region_enabled = true
	n.turtle.flip_h = true
	n.world.add_child(n.turtle)
	n.ripple = [_bar(n.world, 120, PAPER), _bar(n.world, 84, MINT), _bar(n.world, 50, PAPER)]
	n.splash = actor(n.world, "props/p_splash", Vector2(560, 330))
	n.line = Line2D.new()
	n.line.width = 1.0
	n.line.default_color = PAPER
	n.world.add_child(n.line)
	n.bobber = _dot(n.world, 5, ORANGE)
	n.glints = []
	for i in 7:
		n.glints.append(_bar(n.world, 6 + int(rnd(i, 95) * 10.0), PAPER))
	n.front = group(root)
	n.cat = actor(n.front, "chars/cat_m_bored", Vector2(215, 366))
	n.burst = make_burst(n.front, 10, 4)


func _u_cat(t: float) -> void:
	var cam := glide(t, 0.0, 16.2, 0.0, 30.0)
	# 낚싯감 얘기에 화면이 고양이 쪽으로 쿵 하고 당겨진다.
	var punch := pulse(t, 10.4, 0.35)
	n.world.position = Vector2(-roundf(cam) - 8.0, -22.0 + roundf(punch * 3.0))
	n.front.position = Vector2(-roundf(cam * 1.5), 0)
	for i in n.clouds.size():
		(n.clouds[i] as Sprite2D).position.x = roundf([520.0, 300.0][i] - t * (2.0 + i))
	# 물 위의 반짝임이 나타났다 사라지며 흘러간다.
	for i in n.glints.size():
		var glint: Polygon2D = n.glints[i]
		var cycle := fposmod(t * (0.35 + rnd(i, 96) * 0.3) + rnd(i, 97), 1.0)
		glint.visible = cycle < 0.55
		glint.position = Vector2(470.0 + rnd(i, 98) * 200.0 - cycle * 14.0, 312.0 + rnd(i, 99) * 60.0).round()
	# 고양이의 표정.
	var face := "bored"
	if t >= 4.8 and t < 7.0:
		face = "glance"
	elif t >= 10.4 and t < 12.8:
		face = "sparkle"
	elif t >= 12.8:
		face = "smirk"
	if face == "bored" and fposmod(t, 2.7) > 2.56:
		face = "blink"
	var cat: Sprite2D = n.cat
	cat.texture = tex("chars/cat_m_" + face)
	var pop := pulse(t, 10.4, 0.3) * 0.1 + pulse(t, 4.8, 0.2) * 0.03 + pulse(t, 12.8, 0.25) * 0.04
	var breath := sin(t * 1.8) * 0.008
	var talk := hop(t, 11.0, 2.0) if speaking(CAT) else 0.0
	cat.scale = Vector2(1.0 - pop * 0.5, 1.0 + pop + breath)
	cat.position = Vector2(215, 366.0 + talk).round()
	update_burst(n.burst, t - 10.4, cat.position + Vector2(-10, -120), 110.0, 1.1)
	# 낚싯줄과 찌. 찌는 별주부가 솟을 때 크게 출렁인다.
	var tip: Vector2 = cat.position + n.front.position - n.world.position + Vector2(92.0 * cat.scale.x, -142.0 * cat.scale.y)
	var slosh := pulse(t, 1.1, 0.8) * 5.0
	var float_at := Vector2(455.0, 336.0 + sin(t * 2.6) * 1.5 + sin(t * 20.0) * slosh).round()
	n.line.points = PackedVector2Array([tip, float_at])
	n.bobber.position = float_at + Vector2(-2, -3)
	# 별주부: 물에서 솟아 말을 건다.
	var turtle: Sprite2D = n.turtle
	var pose := "calm"
	if speaking(TURTLE):
		pose = "talk" if int(t * 7.0) % 2 == 0 else "calm"
	elif t >= 4.9 and t < 7.2:
		pose = "shock"
	elif t >= 10.6:
		pose = "happy"
	turtle.texture = tex("chars/turtle_m_" + pose)
	var plead := hop(t, 10.0, 4.0) if (speaking(TURTLE) and t > 7.0) else 0.0
	var joy := hop(t, 8.0, 5.0) if t >= 12.9 else 0.0
	var shown := clampf(glide(t, 1.1, 1.5, 0.0, 112.0) + pulse(t, 1.1, 0.7) * 10.0 + sin(t * 2.2) * 2.0 - plead - joy - pulse(t, 5.0, 0.3) * 8.0, 0.0, 140.0)
	var water_y := 344.0
	turtle.region_rect = Rect2(0, 0, 122, roundf(shown))
	turtle.position = Vector2(498, water_y - roundf(shown))
	turtle.visible = shown >= 1.0
	n.splash.visible = t > 1.1 and t < 1.5
	n.splash.scale = Vector2.ONE * (2.0 + pulse(t, 1.1, 0.4))
	for i in n.ripple.size():
		var bar: Polygon2D = n.ripple[i]
		bar.visible = t > 1.2
		var width: float = [120.0, 84.0, 50.0][i]
		bar.position = Vector2(560.0 - width / 2.0 + sin(t * 1.8 + i * 1.4) * 5.0, water_y + i * 4.0).round()


# ---------- 9. 거래 ----------

func _b_deal(root: Node2D) -> void:
	n.clear()
	n.sea = layer_sprite(root, "bg/sea", Vector2(-380, 0))
	n.streaks = []
	for i in 10:
		n.streaks.append(_bar(root, 60 + int(rnd(i, 91) * 90.0), PAPER if i % 2 == 0 else MINT, 2))
	n.flipper = layer_sprite(root, "chars/hand_turtle")
	n.paw = layer_sprite(root, "chars/hand_cat")
	n.burst = make_burst(root, 12, 5)


func _u_deal(t: float) -> void:
	n.sea.position.x = -380.0 - roundf(t * 5.0)
	# 두 손이 양쪽에서 들어와 맞잡고 흔든다.
	var meet := glide(t, 0.15, 0.8)
	var settle := pulse(t, 0.8, 0.25) * 6.0
	var decay := clampf(1.0 - (t - 0.95) / 2.0, 0.0, 1.0)
	var shake := (sin((t - 0.95) * 15.0) * 9.0 * decay) if t > 0.95 else 0.0
	n.paw.position = Vector2(lerpf(-450.0, -74.0, meet) - settle, 2.0 + shake).round()
	n.flipper.position = Vector2(lerpf(650.0, 266.0, meet) + settle, 2.0 + shake).round()
	update_burst(n.burst, t - 0.85, Vector2(322, 150), 120.0, 1.2)
	for i in n.streaks.size():
		var bar: Polygon2D = n.streaks[i]
		var from_left: bool = i % 2 == 0
		var along := fposmod(rnd(i, 92) + t * (1.6 + rnd(i, 93)), 1.0)
		bar.visible = t < 1.0
		bar.position = Vector2((along * 900.0 - 200.0) if from_left else (700.0 - along * 900.0), 30.0 + rnd(i, 94) * 290.0).round()


# ---------- 10. 출항 ----------

func _b_depart(root: Node2D) -> void:
	n.clear()
	n.world = group(root)
	layer_sprite(n.world, "bg/sea")
	n.clouds = [layer_sprite(n.world, "props/p_cloud", Vector2(330, 40)), layer_sprite(n.world, "props/p_cloud", Vector2(620, 66))]
	n.mid = group(root)
	n.wake = []
	for i in 5:
		n.wake.append(_bar(n.mid, 16 - i * 2, PAPER, 2))
	n.turtle = Sprite2D.new()
	n.turtle.texture = tex("chars/turtle_l_stand")
	n.turtle.centered = false
	n.turtle.region_enabled = true
	n.mid.add_child(n.turtle)
	n.boat = actor(n.mid, "chars/boat_cat")
	n.splash = actor(n.mid, "props/p_splash")
	n.wave = layer_sprite(root, "bg/wave_fg", Vector2(-60, 262))


func _u_depart(t: float) -> void:
	var cam := glide(t, -1.0, 10.6, 180.0, 476.0)
	n.world.position.x = -roundf(cam)
	for i in n.clouds.size():
		(n.clouds[i] as Sprite2D).position.x = roundf([330.0, 620.0][i] + cam * 0.6 - t * 2.0)
	n.wave.position = Vector2(-60.0 - roundf(t * 14.0) + roundf(sin(t * 1.3) * 4.0), 262.0 + roundf(sin(t * 1.6) * 2.0))
	# 노를 저을 때마다 배가 앞으로 밀리고 뱃머리가 들린다.
	var stroke := sin(t * 3.2)
	var boat: Sprite2D = n.boat
	var x := glide(t, -1.0, 10.6, 150.0, 400.0) + stroke * 4.0
	var y := 274.0 + sin(t * 1.6) * 2.0
	boat.position = Vector2(x, y).round()
	boat.rotation = -0.02 - stroke * 0.03
	for i in n.wake.size():
		var bar: Polygon2D = n.wake[i]
		var trail := fposmod(t * 1.2 + i * 0.2, 1.0)
		bar.position = Vector2(x - 86.0 - trail * 50.0, y - 6.0 + (i % 2) * 3.0).round()
		bar.visible = trail < 0.8
	# 별주부가 옆에서 헤엄쳐 따라간다.
	var turtle: Sprite2D = n.turtle
	var shown := 40.0 + roundf(sin(t * 3.2 + 1.0) * 3.0)
	turtle.region_rect = Rect2(0, 0, 75, shown)
	turtle.position = Vector2(x - 170.0 + sin(t * 1.1) * 6.0, y - 4.0 - shown).round()
	n.splash.visible = t > 1.2 and t < 1.6
	n.splash.position = Vector2(x + 70.0, y + 2.0).round()


# ---------- 작은 그림 ----------

## 가로 띠 (잔물결, 속도선, 물살).
func _bar(root: Node, width: int, colour: Color, height := 1) -> Polygon2D:
	var bar := Polygon2D.new()
	bar.polygon = PackedVector2Array([Vector2(0, 0), Vector2(width, 0), Vector2(width, height), Vector2(0, height)])
	bar.color = colour
	root.add_child(bar)
	return bar


func _dot(root: Node, size: int, colour: Color) -> Polygon2D:
	var dot := _bar(root, size, colour, size)
	var top := _bar(dot, size, PAPER, maxi(1, int(size / 3.0)))
	top.position = Vector2.ZERO
	return dot


## 느낌표.
func _mark_texture() -> Texture2D:
	var image := Image.create(7, 13, false, Image.FORMAT_RGBA8)
	image.fill(INK)
	for y in range(1, 12):
		for x in range(1, 6):
			image.set_pixel(x, y, PAPER)
	for y in range(2, 8):
		for x in range(2, 5):
			image.set_pixel(x, y, ORANGE)
	for y in range(9, 11):
		for x in range(2, 5):
			image.set_pixel(x, y, ORANGE)
	return ImageTexture.create_from_image(image)


## 솔잎 한 가닥.
func _leaf_texture() -> Texture2D:
	var image := Image.create(6, 4, false, Image.FORMAT_RGBA8)
	for i in 6:
		image.set_pixel(i, 3 - int(i / 2.0), TEAL_DARK)
	image.set_pixel(2, 3, Color("439083"))
	image.set_pixel(4, 2, Color("439083"))
	return ImageTexture.create_from_image(image)
