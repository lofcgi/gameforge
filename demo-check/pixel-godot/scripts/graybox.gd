class_name Graybox
## 아트 없이 도형만으로 레벨을 세우는 도우미.


static func rect(area: Rect2, color: Color) -> ColorRect:
	var node := ColorRect.new()
	node.position = area.position
	node.size = area.size
	node.color = color
	return node


static func solid(area: Rect2, color: Color) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = area.get_center()
	body.add_child(_shape(area.size))
	body.add_child(rect(Rect2(-area.size / 2, area.size), color))
	return body


static func zone(area: Rect2, color: Color) -> Area2D:
	var node := Area2D.new()
	node.position = area.get_center()
	node.collision_layer = 0
	node.collision_mask = 2
	node.add_child(_shape(area.size))
	node.add_child(rect(Rect2(-area.size / 2, area.size), color))
	return node


static func _shape(size: Vector2) -> CollisionShape2D:
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	return shape
