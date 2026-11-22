class_name Level
## 레벨 데이터. 좌표는 기준 해상도(320x180) 픽셀이고 y 는 아래로 증가한다.
## 그레이박스 단계에서는 이 상수만 고쳐 레벨을 바꾼다.

const NAME := "graybox-1"
const WIDTH := 640
const KILL_Y := 220.0
const SPAWN := Vector2(24, 140)

const SOLIDS: Array[Rect2] = [
	Rect2(0, 156, 200, 24),
	Rect2(232, 156, 168, 24),
	Rect2(400, 132, 80, 48),
	Rect2(480, 156, 160, 24),
	Rect2(-8, 0, 8, 180),
	Rect2(640, 0, 8, 180),
]

const HAZARDS: Array[Rect2] = [
	Rect2(312, 148, 8, 8),
]

const GOAL := Rect2(600, 124, 12, 32)
