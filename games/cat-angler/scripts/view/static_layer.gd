class_name StaticLayer
extends Node2D
## 거의 바뀌지 않는 그림 한 겹. painter 로 한 번 그려 두고, refresh 에 준 값이 달라질 때만 다시 그린다.
## 매 프레임 다시 그리는 도형 수를 줄이려고 먼 배경, 항구, 섬을 이렇게 둔다.

var painter: Callable
var _signature = null


static func make(painter_: Callable) -> StaticLayer:
	var layer := StaticLayer.new()
	layer.painter = painter_
	layer.show_behind_parent = true
	return layer


func refresh(signature) -> void:
	if signature != _signature:
		_signature = signature
		queue_redraw()


func _draw() -> void:
	painter.call(self)
