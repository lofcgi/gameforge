class_name Save
## 진행 저장: 돈, 장비, 미끼, 재료, 어창, 도감, 있던 곳. user://<slot>.json 한 파일이다.
## 마을에 들어설 때마다 저절로 저장하고, 일시정지 메뉴에서 직접 저장할 수 있다.
## 자동 실행(봇·캡처·재생)에서는 저장을 끈다: 남은 저장 파일이 실행마다 결과를 바꾸면 재생이 어긋난다.

const VERSION := 1

static var slot := "save"     # 빈 문자열이면 저장하지 않는다


static func enabled() -> bool:
	return slot != ""


static func path() -> String:
	return "user://%s.json" % slot


static func exists() -> bool:
	return enabled() and FileAccess.file_exists(path())


static func write(g: Game) -> void:
	if not enabled():
		return
	var inv := g.inv
	var where := g.scene
	if where.begins_with("in_") or not (where in ["town", "forage", "island", "sea"]):
		where = "town"
	var data := {
		"version": VERSION, "scene": where, "walk_x": g.walk.x, "boat_x": g.sailing.x,
		"coins": inv.coins, "mats": inv.mats, "baits": inv.baits, "bait": inv.bait, "hold": inv.hold,
		"rod": inv.rod, "boat": inv.boat, "durability": inv.durability, "caught": inv.caught,
		"delivered": g.delivered, "deaths": g.deaths, "picked": g.picked, "stock": g.walk.stock,
		"visits": g.shop.visits, "guide": {"on": g.guide.on, "step": g.guide.step, "gathered": g.guide.gathered,
			"crafted": g.guide.crafted, "sold": g.guide.sold},
		"catches": g.fishing.catches,
	}
	var file := FileAccess.open(path(), FileAccess.WRITE)
	if file == null:
		push_error("저장하지 못했다: %s (%d)" % [path(), FileAccess.get_open_error()])
		return
	file.store_string(JSON.stringify(data, " "))


static func read() -> Dictionary:
	if not exists():
		return {}
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path()))
	if not (parsed is Dictionary) or int(parsed.get("version", 0)) != VERSION:
		push_error("저장 파일을 읽지 못했다: " + path())
		return {}
	return parsed


## 읽은 저장을 게임에 넣는다. 돌아갈 화면 이름을 돌려준다.
static func apply(g: Game, data: Dictionary) -> String:
	var inv := g.inv
	inv.coins = int(data["coins"])
	for id in inv.mats:
		inv.mats[id] = int(data["mats"].get(id, 0))
	for id in inv.baits:
		inv.baits[id] = int(data["baits"].get(id, 0))
	inv.bait = data["bait"]
	inv.hold = Array(data["hold"])
	inv.rod = int(data["rod"])
	inv.boat = int(data["boat"])
	inv.durability = float(data["durability"])
	inv.caught = {}
	for id in data["caught"]:
		inv.caught[id] = int(data["caught"][id])
	g.delivered = bool(data["delivered"])
	g.deaths = int(data["deaths"])
	g.picked = int(data["picked"])
	g.fishing.catches = int(data.get("catches", 0))
	for mat in g.walk.stock:
		var saved: Array = data["stock"].get(mat, [])
		for i in mini(saved.size(), g.walk.stock[mat].size()):
			g.walk.stock[mat][i] = bool(saved[i])
	g.shop.visits = {}
	for id in data["visits"]:
		g.shop.visits[id] = int(data["visits"][id])
	var guide: Dictionary = data["guide"]
	g.guide.on = bool(guide["on"])
	g.guide.step = int(guide["step"])
	g.guide.gathered = int(guide["gathered"])
	g.guide.crafted = bool(guide["crafted"])
	g.guide.sold = bool(guide["sold"])
	g.walk.x = float(data["walk_x"])
	g.sailing.x = clampf(float(data["boat_x"]), Sailing.left_limit(), Sailing.right_limit())
	return data["scene"]
