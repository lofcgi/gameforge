class_name Level
## 레벨 데이터. 단위는 미터, y 가 위, forward 입력은 -z 로 간다. 각 상자는 [중심, 크기].
## 그레이박스 단계에서는 이 상수만 고쳐 레벨을 바꾼다.

const NAME := "graybox-1"
const KILL_Y := -8.0
const SPAWN := Vector3(0, 1.0, 0)

const SOLIDS := [
	[Vector3(0, -0.5, -4), Vector3(8, 1, 14)],
	[Vector3(0, -0.5, -21), Vector3(8, 1, 16)],
	[Vector3(0, 0.375, -18), Vector3(8, 0.75, 2)],
]

const HAZARDS := [
	[Vector3(0, -2.5, -12), Vector3(8, 1, 2)],
	[Vector3(-1.5, 0.2, -24), Vector3(3, 0.4, 1)],
]

const GOAL := [Vector3(0, 1, -27), Vector3(1.5, 2, 1.5)]
