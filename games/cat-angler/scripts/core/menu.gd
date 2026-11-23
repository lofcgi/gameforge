class_name Menu
extends RefCounted
## 화면을 덮는 것: 타이틀 메뉴, 일시정지, 조작 안내, 알림, 어창, 도감. 열려 있는 동안 세계는 멈춘다.

const CODEX_COLS := 3
const TITLES := {"hold": "어창", "pause": "잠깐 멈춤", "help": "조작", "title": "", "notice": "", "codex": "도감"}

var kind := ""
var cursor := 0
var items: Array = []     # {text, right, ok, do, arg}
var say := ""
var text := ""            # 알림의 글
var pending := ""         # 어창이 가득 차 자리를 기다리는 방금 낚은 물고기
var denied := 0
var lock := 0             # 줄다리기 직후 감던 손이 그대로 "놓아주기"를 누르지 않게 잠깐 선택을 막는다
var opened := 0           # 연 틱(펼치는 연출에 쓴다)


func busy() -> bool:
	return kind != ""


func open(g: Game, what: String, arg := "") -> void:
	kind = what
	cursor = 0
	say = ""
	opened = g.tick
	match what:
		"hold":
			pending = arg
			if arg != "":
				lock = 45
				var fish := Data.fish(arg)
				say = "가득 찼다! 놓아줄 것을 고르자. X: 방금 낚은 %s(%d닢) 놓아주기" % [fish["name"], fish["price"]]
		"notice":
			text = arg
		"title":
			cursor = 0 if Save.exists() else 1
	_rebuild(g)
	g.emit("open", {"kind": what})


func step(g: Game) -> void:
	lock = maxi(0, lock - 1)
	match kind:
		"help", "notice":
			if g.pressed("action") or g.pressed("cancel") or g.pressed("pause"):
				_close(g)
			elif g.pressed_other([]):
				_deny(g)
			return
		"codex":
			_step_codex(g)
			return
	var used := ["up", "down", "action"]
	if kind != "title":
		used.append("cancel")
		used.append(kind)         # 어창은 H, 일시정지는 P 로도 닫힌다
	if g.pressed_other(used):
		_deny(g)
	var move := int(g.pressed("down")) - int(g.pressed("up"))
	if move != 0 and items.size() > 1:
		cursor = posmod(cursor + move, items.size())
		g.emit("cursor", {})
	elif move != 0:
		_deny(g)
	if g.pressed("action") and not items.is_empty():
		var item: Dictionary = items[cursor]
		if item["ok"] and lock == 0:
			_do(g, item)
			if kind != "" and kind != "help":
				_rebuild(g)
		else:
			denied += 1
			g.emit("deny", {})
		return
	if kind == "title":
		return
	if g.pressed("cancel") or (kind == "hold" and g.pressed("hold")) or (kind == "pause" and g.pressed("pause")):
		_close(g)


func _step_codex(g: Game) -> void:
	var count := Data.FISH.size()
	var move := int(g.pressed("right")) - int(g.pressed("left")) + CODEX_COLS * (int(g.pressed("down")) - int(g.pressed("up")))
	var to := clampi(cursor + move, 0, count - 1)
	if to != cursor:
		cursor = to
		g.emit("page", {})
	elif move != 0:
		_deny(g)
	if g.pressed("cancel") or g.pressed("codex") or g.pressed("action"):
		_close(g)
	elif g.pressed_other(["left", "right", "up", "down"]):
		_deny(g)


## 여기서는 하는 일이 없는 키: 틀이 살짝 떨린다.
func _deny(g: Game) -> void:
	denied += 1
	g.emit("deny", {})


func _close(g: Game) -> void:
	if pending != "":
		g.toast("%s 놓아주었다." % Data.fish(pending)["name"])
		g.emit("release", {})
		pending = ""
	var was := kind
	kind = ""
	g.emit("close", {"kind": was})
	if g.scene == "title":
		open(g, "title")


func _item(label: String, right := "", ok := true, action := "", arg = null) -> Dictionary:
	return {"text": label, "right": right, "ok": ok, "do": action, "arg": arg}


func _rebuild(g: Game) -> void:
	var inv := g.inv
	items = []
	match kind:
		"title":
			items.append(_item("이어하기", "", Save.exists(), "continue"))
			items.append(_item("새로 시작", "", true, "new"))
			items.append(_item("조작 안내", "", true, "help"))
		"pause":
			items.append(_item("계속하기", "", true, "resume"))
			items.append(_item("저장하기", "", Save.enabled(), "save"))
			items.append(_item("길잡이 끄기" if g.guide.on else "길잡이 켜기", "", true, "guide"))
			items.append(_item("조작 안내", "", true, "help"))
			items.append(_item("타이틀로", "저장하고 나간다", true, "title"))
		"hold":
			for i in inv.hold.size():
				var fish := Data.fish(inv.hold[i])
				items.append(_item("%s (%d칸)" % [fish["name"], fish["slots"]],
					"놓아주기" if inv.hold[i] == "legend" else "%d닢 · 놓아주기" % fish["price"], true, "release", i))
			if items.is_empty():
				items.append(_item("비어 있다", "", false))
		"codex":
			for fish in Data.FISH:
				items.append(_item(fish["name"] if inv.caught.has(fish["id"]) else "???", "", false, "", fish["id"]))
	cursor = clampi(cursor, 0, maxi(0, items.size() - 1))


func _do(g: Game, item: Dictionary) -> void:
	var inv := g.inv
	match item["do"]:
		"continue":
			kind = ""
			g.continue_game()
		"new":
			kind = ""
			g.new_game()
		"help":
			open(g, "help")
		"resume":
			_close(g)
		"save":
			Save.write(g)
			g.toast("저장했다.")
			g.emit("saved", {})
			_close(g)
		"guide":
			g.guide.on = not g.guide.on
			g.emit("cursor", {})
		"title":
			Save.write(g)
			kind = ""
			g.goto("title", "fade", {})
		"release":
			var id: String = inv.hold[item["arg"]]
			inv.hold.remove_at(item["arg"])
			g.emit("release", {})
			if pending != "" and inv.fits(pending):
				inv.hold.append(pending)
				g.toast("%s 놓아주고 %s 실었다." % [Data.fish(id)["name"], Data.fish(pending)["name"]])
				pending = ""
				kind = ""
				g.emit("close", {"kind": "hold"})
