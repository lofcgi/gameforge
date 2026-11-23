class_name Assets
## 그림·글꼴·소리를 읽는 한 곳. 경로는 design/asset-spec.md 의 것(assets/game 아래)만 쓴다.
## 파일이 없으면 Placeholder 가 도형으로 그린 임시 그림을 주고, 빠진 이름을 missing 에 한 번씩 적는다.
## 파일이 생기면 다음 실행부터 코드 수정 없이 쓰인다.

const ROOT := "res://assets/game/"
const SOUND_TYPES := [".wav", ".ogg", ".mp3"]

static var missing := {}      # 빠진 파일 이름(assets/game 기준) -> true. 넣은 순서가 유지된다

static var _tex := {}
static var _anims := {}
static var _streams := {}


## 가져오기(import)가 끝난 리소스이거나, 아직 가져오지 않았어도 파일이 놓여 있으면 참.
static func exists(rel: String) -> bool:
	return ResourceLoader.exists(ROOT + rel) or FileAccess.file_exists(ROOT + rel)


static func _note_missing(rel: String) -> void:
	missing[rel] = true


## 정지 그림. rel 예: "boats/boat1.png".
static func tex(rel: String) -> Texture2D:
	if _tex.has(rel):
		return _tex[rel]
	var texture: Texture2D = _load_texture(rel)
	if texture == null:
		_note_missing(rel)
		texture = ImageTexture.create_from_image(Placeholder.image(rel))
	_tex[rel] = texture
	return texture


static func _load_texture(rel: String) -> Texture2D:
	var path := ROOT + rel
	if ResourceLoader.exists(path):
		return load(path)
	if FileAccess.file_exists(path):
		# 에디터가 아직 가져오지 않은 PNG: 파일에서 바로 읽는다.
		var image := Image.load_from_file(ProjectSettings.globalize_path(path))
		if image != null:
			return ImageTexture.create_from_image(image)
	return null


## 애니메이션. base 예: "chars/cat_idle" → {"frames": [Texture2D], "fps": float, "loop": bool}.
## `gf post sheet` 의 .tres(SpriteFrames)를 먼저 찾고, 없으면 PNG + JSON 매니페스트를 읽는다.
static func anim(base: String) -> Dictionary:
	if _anims.has(base):
		return _anims[base]
	var result := _load_frames(base)
	if result.is_empty():
		_note_missing(base + ".tres")
		var made := Placeholder.frames(base)
		var list: Array = []
		for image in made["frames"]:
			list.append(ImageTexture.create_from_image(image))
		result = {"frames": list, "fps": made["fps"], "loop": true}
	_anims[base] = result
	return result


static func _load_frames(base: String) -> Dictionary:
	var path := ROOT + base + ".tres"
	if ResourceLoader.exists(path):
		var res = load(path)
		if res is SpriteFrames and not res.get_animation_names().is_empty():
			var name: StringName = res.get_animation_names()[0]
			var list: Array = []
			for i in res.get_frame_count(name):
				list.append(res.get_frame_texture(name, i))
			if not list.is_empty():
				return {"frames": list, "fps": res.get_animation_speed(name), "loop": res.get_animation_loop(name)}
	var sheet := _load_texture(base + ".png")
	var manifest := ROOT + base + ".json"
	if sheet == null or not FileAccess.file_exists(manifest):
		return {}
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(manifest))
	if not (parsed is Dictionary) or not parsed.has("animations") or parsed["animations"].is_empty():
		return {}
	var entry: Dictionary = parsed["animations"].values()[0]
	var frames: Array = []
	for rect in entry["frames"]:
		var atlas := AtlasTexture.new()
		atlas.atlas = sheet
		atlas.region = Rect2(rect["x"], rect["y"], rect["w"], rect["h"])
		frames.append(atlas)
	return {"frames": frames, "fps": float(entry.get("fps", 8.0)), "loop": bool(entry.get("loop", true))}


## 틱에 맞는 프레임. start 를 주면 그 틱에서 시작한 것으로 보고, 반복하지 않는 동작은 마지막 프레임에 머문다.
static func frame(base: String, tick: int, start := 0, once := false) -> Texture2D:
	var data := anim(base)
	var list: Array = data["frames"]
	var index := int((tick - start) * data["fps"] / 60.0)
	if once:
		index = clampi(index, 0, list.size() - 1)
	return list[posmod(index, list.size())]


static func frame_count(base: String) -> int:
	return anim(base)["frames"].size()


## 글꼴. 역할마다 파일과 크기가 정해져 있다(픽셀 글꼴은 제 크기의 정수배로만 또렷하다).
## assets/game/fonts/font.json 이 있으면 그 표를 쓰고, 없으면 아래 기본(갈무리)을 쓴다. 파일이 없으면 시스템 한글 글꼴로 대신한다.
const FONT_ROLES := {
	"body": ["Galmuri11.ttf", 12], "bold": ["Galmuri11-Bold.ttf", 12], "small": ["Galmuri9.ttf", 10], "large": ["Galmuri14.ttf", 15],
}

static var _fonts := {}


static func font(role := "body") -> Font:
	return _font_entry(role)[0]


static func font_size(role := "body") -> int:
	return _font_entry(role)[1]


static func _font_entry(role: String) -> Array:
	if _fonts.has(role):
		return _fonts[role]
	var table: Dictionary = FONT_ROLES
	if FileAccess.file_exists(ROOT + "fonts/font.json"):
		var parsed = JSON.parse_string(FileAccess.get_file_as_string(ROOT + "fonts/font.json"))
		if parsed is Dictionary:
			table = parsed
	var spec: Array = table.get(role, table.get("body", FONT_ROLES["body"]))
	var loaded: Font = null
	for candidate in [spec, table.get("body", spec)]:
		var path: String = ROOT + "fonts/" + candidate[0]
		if not FileAccess.file_exists(path):
			continue
		var file := FontFile.new()
		if file.load_dynamic_font(path) != OK:
			push_error("글꼴을 읽지 못했다: " + path)
			continue
		file.antialiasing = TextServer.FONT_ANTIALIASING_NONE
		file.hinting = TextServer.HINTING_NONE
		file.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
		loaded = file
		spec = candidate
		break
	if loaded == null:
		_note_missing("fonts/%s" % spec[0])
		var system := SystemFont.new()
		system.font_names = PackedStringArray(["Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans CJK KR", "NanumGothic", "sans-serif"])
		system.antialiasing = TextServer.FONT_ANTIALIASING_NONE
		system.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
		system.font_weight = 700 if role == "bold" else 500
		loaded = system
	_fonts[role] = [loaded, int(spec[1])]
	return _fonts[role]


## 지금 프레임의 번호(낚싯대 끝처럼 프레임마다 다른 자리를 찾을 때 쓴다).
static func frame_index(base: String, tick: int, start := 0, once := false) -> int:
	var data := anim(base)
	var count: int = data["frames"].size()
	var index := int((tick - start) * data["fps"] / 60.0)
	return clampi(index, 0, count - 1) if once else posmod(index, count)


## 실행을 마칠 때 붙잡고 있던 리소스를 놓는다.
static func release() -> void:
	_tex.clear()
	_anims.clear()
	_streams.clear()
	_fonts.clear()


## 소리. name 예: "coin". 없으면 null 이고 빠진 목록에 오른다.
static func stream(name: String) -> AudioStream:
	if _streams.has(name):
		return _streams[name]
	var found: AudioStream = null
	for ext in SOUND_TYPES:
		var path: String = ROOT + "audio/" + name + ext
		if ResourceLoader.exists(path):
			found = load(path)
			break
		if ext == ".wav" and FileAccess.file_exists(path):
			found = AudioStreamWAV.load_from_file(ProjectSettings.globalize_path(path))
			break
	if found == null:
		_note_missing("audio/%s.wav" % name)
	_streams[name] = found
	return found


static func missing_list() -> Array:
	return missing.keys()


## 규격에 있는 파일 가운데 아직 없는 것을 미리 적어 둔다(시작할 때 한 번). 그래야 아직 열어 보지 않은 화면의 것도 목록에 나온다.
static func probe() -> void:
	var stills: Array = ["boats/boat1.png", "boats/boat2.png", "boats/boat3.png"]
	var anims: Array = []
	for action in Placeholder.CAT_FRAMES:
		anims.append("chars/cat_" + action)
	stills.append("portraits/cat.png")
	for id in Data.SHOP_ORDER:
		anims.append("chars/keeper_%s_idle" % id)
		anims.append("chars/keeper_%s_talk" % id)
		stills.append("portraits/keeper_%s.png" % id)
		stills.append("places/%s.png" % Data.SHOPS[id]["scene"])
	for fish in Data.FISH:
		anims.append("fish/%s_swim" % fish["id"])
		stills.append("fish/%s_card.png" % fish["id"])
	anims.append("fish/legend_shadow_swim")
	for zone in ["shallow", "open", "deep"]:
		for layer in ["sky", "far", "mid", "under", "bed"]:
			stills.append("sea/%s_%s.png" % [layer, zone])
	for name in ["surface_pattern", "wave_crest", "reef", "wreck", "island_far", "ruin_1", "ruin_2", "ruin_3", "pavilion", "pier",
			"crate", "bottle", "hook"]:
		stills.append("sea/%s.png" % name)
	for name in ["school_small", "school_mid", "school_big", "bird", "splash", "bubble", "sparkle", "vortex"]:
		anims.append("sea/" + name)
	for id in Data.BAIT_ORDER:
		stills.append("sea/bait_%s.png" % id)
		stills.append("items/bait_%s.png" % id)
	for name in ["town", "town_fg", "forage", "island", "title"]:
		stills.append("places/%s.png" % name)
	for id in Data.MATS:
		stills.append("items/%s.png" % id)
		stills.append("items/%s_plant.png" % id)
	stills.append("items/coin.png")
	for tier in [1, 2, 3]:
		stills.append("items/rod%d.png" % tier)
		stills.append("items/rod%d_wall.png" % tier)
	for name in ["panel", "button", "button_focus", "bubble", "gauge_frame", "gauge_fill", "tension_frame", "tension_fill",
			"depth_ruler", "slot", "slot_focus", "codex_book", "icon_durability", "icon_hold", "icon_coin", "icon_anchor",
			"icon_bait", "arrow", "logo"]:
		stills.append("ui/%s.png" % name)
	for rel in stills:
		if not exists(rel):
			_note_missing(rel)
	for base in anims:
		if not exists(base + ".tres") and not (exists(base + ".png") and exists(base + ".json")):
			_note_missing(base + ".tres")
	for name in MUSIC + SOUNDS:
		var found := false
		for ext in SOUND_TYPES:
			found = found or exists("audio/" + name + ext)
		if not found:
			_note_missing("audio/%s.wav" % name)
	for role in FONT_ROLES:
		font(role)


const MUSIC := ["title", "town", "sea_shallow", "sea_open", "sea_deep", "fight", "legend_fight", "cutscene_intro", "cutscene_ending"]
const SOUNDS := ["step", "pick", "door", "coin", "buy", "craft", "anchor_down", "anchor_up", "cast", "nibble", "bite", "reel",
	"line_strain", "snap", "slip", "catch_small", "catch_big", "wave_hit", "splash", "ui_move", "ui_ok", "ui_cancel", "codex_new",
	"talk", "page", "repair", "pickup", "release"]
