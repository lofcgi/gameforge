class_name Graybox
## 아트 없이 상자만으로 레벨을 세우는 도우미. box 는 [중심, 크기].


static func solid(box: Array, color: Color) -> StaticBody3D:
	var body := StaticBody3D.new()
	_fill(body, box, color)
	return body


static func zone(box: Array, color: Color) -> Area3D:
	var area := Area3D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	_fill(area, box, color)
	return area


static func _fill(node: Node3D, box: Array, color: Color) -> void:
	node.position = box[0]
	var shape := CollisionShape3D.new()
	shape.shape = BoxShape3D.new()
	shape.shape.size = box[1]
	node.add_child(shape)
	var mesh := MeshInstance3D.new()
	mesh.mesh = BoxMesh.new()
	mesh.mesh.size = box[1]
	mesh.material_override = material(color)
	node.add_child(mesh)


static func material(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.9
	return mat
