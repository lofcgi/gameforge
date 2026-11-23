class_name ShopScreen
extends Screen
## 가게 실내 화면의 바탕: 배경, 주인과 고양이, 초상화가 있는 대사 창. 가게마다의 거래 화면은 이 위에 stage() 로 그린다.

const DIALOG := Rect2(112, 274, 520, 62)
const PORTRAIT := Rect2(8, 240, 100, 100)

var _was_anim := ""


func data() -> Dictionary:
	return Layout.of("places/" + game.scene)


func point(key: String) -> Vector2:
	return Layout.point("places/" + game.scene, key)


func focus() -> Vector2:
	return point("cat") + Vector2(0, -28)


func advance() -> void:
	var anim: Dictionary = game.shop.anim
	var stamp: String = "%s%d" % [anim["kind"], anim["t"]] if not anim.is_empty() else ""
	if stamp != "" and stamp != _was_anim:
		on_anim(anim)
	_was_anim = stamp
	queue_redraw()


## 거래 연출의 틱마다 불린다(동전 날리기, 입자).
func on_anim(_anim: Dictionary) -> void:
	pass


## 가게마다의 거래 화면.
func stage() -> void:
	pass


func _draw() -> void:
	var shop := game.shop
	draw_texture(Assets.tex("places/%s.png" % game.scene), fx.offset)
	var speaking := not shop.typed()
	Ui.sprite(self, Assets.frame("chars/keeper_%s_%s" % [shop.id, "talk" if speaking else "idle"], game.tick), point("keeper"), Vector2(0.5, 1.0), true)
	var mood := "idle"
	if not shop.anim.is_empty() and shop.anim["t"] < 40:
		mood = "cheer"
	draw_cat(point("cat"), mood)
	if not shop.talking():
		stage()
	draw_effects(Vector2.ZERO)
	_dialog()


func _dialog() -> void:
	var shop := game.shop
	Ui.box(self, "panel", PORTRAIT)
	draw_texture(Assets.tex("portraits/keeper_%s.png" % shop.id), PORTRAIT.position + Vector2(2, 2))
	Ui.box(self, "bubble", DIALOG)
	# 말풍선 꼬리: 초상화 쪽을 가리킨다. 창의 왼쪽 테두리를 꼬리 안쪽 높이만큼 바탕색으로 덮어 이어 붙인다.
	var tail := Assets.tex("ui/bubble_tail.png")
	var tail_at := DIALOG.position + Vector2(-tail.get_width() + 1, 26)
	draw_texture(tail, tail_at)
	draw_rect(Rect2(DIALOG.position.x, tail_at.y + 1, 4, tail.get_height() - 3), Pal.WHITE)
	var name: String = shop.data()["keeper"]
	Ui.box(self, "button", Rect2(DIALOG.position + Vector2(10, -10), Vector2(Ui.width(name) + 16, 20)), 8)
	Ui.text(self, DIALOG.position + Vector2(18, -7), name, Pal.BARK)
	Ui.paragraph(self, Rect2(DIALOG.position + Vector2(18, 14), DIALOG.size - Vector2(44, 20)), shop.line, Pal.BARK, int(shop.shown))
	if shop.talking() and shop.typed() and game.tick % 40 < 26:
		Ui.sprite(self, Assets.tex("ui/arrow.png"), DIALOG.end - Vector2(18, 8))


## 고를 수 있는 칸의 틀. focused 면 밝은 틀, 살 수 없으면 흐리게.
func slot(rect: Rect2, focused: bool, ok := true) -> void:
	var nudge := Vector2(2, 0) if focused and fx.on("deny") and game.tick % 4 < 2 else Vector2.ZERO
	Ui.box(self, "slot_focus" if focused else "slot", Rect2(rect.position + nudge, rect.size), 6, Color.WHITE if ok or focused else Color(1, 1, 1, 0.6))


func tag(center_x: float, y: float, text: String, focused := false, color := Pal.BARK) -> void:
	var w := Ui.width(text) + 14.0
	Ui.box(self, "button_focus" if focused else "button", Rect2(roundf(center_x - w * 0.5), y, w, 18), 8)
	Ui.text(self, Vector2(roundf(center_x - w * 0.5) + 7, y + 2), text, color)
