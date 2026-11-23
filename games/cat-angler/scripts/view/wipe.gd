class_name Wipe
extends ColorRect
## 화면 전환 연출: 격자 무늬로 어두워지는 페이드와, 고양이에게로 오므라드는 조리개. 코어의 trans 진행을 그대로 그린다.

const SHADER := """
shader_type canvas_item;
uniform int kind = 0;
uniform float cover = 0.0;
uniform vec2 center = vec2(320.0, 180.0);
const vec3 INK = vec3(0.09, 0.07, 0.106);
void fragment() {
	vec2 p = floor(UV * vec2(640.0, 360.0));
	float alpha = 0.0;
	if (kind == 1) {
		float radius = (1.0 - cover) * 760.0;
		alpha = (cover > 0.0 && distance(p, center) >= radius) ? 1.0 : 0.0;
	} else {
		vec2 cell = floor(p / 2.0);
		float threshold = (mod(cell.x, 2.0) * 2.0 + mod(cell.y, 2.0) * 3.0 - mod(cell.x, 2.0) * mod(cell.y, 2.0) * 4.0 + 0.5) / 4.0;
		alpha = cover * 1.25 > threshold ? 1.0 : 0.0;
	}
	COLOR = vec4(INK, alpha);
}
"""

var _material := ShaderMaterial.new()
var _mark := Node2D.new()     # 화면이 다 가려진 동안 가운데에 뜨는 물결 문양


func _ready() -> void:
	var shader := Shader.new()
	shader.code = SHADER
	_material.shader = shader
	material = _material
	color = Color.WHITE
	visible = false
	for i in 3:
		var tile := Sprite2D.new()
		tile.texture = Assets.tex("sea/surface_pattern.png")
		tile.position = Vector2((i - 1) * tile.texture.get_width(), 0)
		_mark.add_child(tile)
	_mark.position = Ui.SCREEN * 0.5
	add_child(_mark)


func advance(g: Game, focus: Vector2) -> void:
	visible = g.transitioning()
	if not visible:
		return
	var t: float = g.trans["t"] / float(Game.TRANS_HALF)
	var cover := t if t <= 1.0 else 2.0 - t
	# 조리개는 닫힐 때 빨라지고 열릴 때 느려진다.
	_material.set_shader_parameter("kind", 1 if g.trans["kind"] == "iris" else 0)
	_material.set_shader_parameter("cover", clampf(cover * cover if g.trans["kind"] == "iris" else cover, 0.0, 1.0))
	_material.set_shader_parameter("center", focus.round())
	_mark.visible = cover > 0.55
	_mark.position.y = Ui.SCREEN.y * 0.5 + roundf(sin(g.tick * 0.4) * 2.0)
