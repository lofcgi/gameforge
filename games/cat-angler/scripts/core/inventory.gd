class_name Inventory
extends RefCounted
## 가진 것: 돈, 재료, 미끼, 어창, 장비 단계, 도감.

var coins := 0
var mats := {"herb": 0, "bug": 0, "berry": 0, "flower": 0}
var baits := {"herb": 0, "bug": 0, "berry": 0, "legend": 0}
var bait := "herb"
var hold: Array = []
var rod := 0
var boat := 0
var durability := 0.0
var caught := {}


func _init() -> void:
	for id in Data.START_BAITS:
		baits[id] = Data.START_BAITS[id]
	durability = boat_data()["dur"]


func rod_data() -> Dictionary:
	return Data.RODS[rod]


func boat_data() -> Dictionary:
	return Data.BOATS[boat]


func hold_used() -> int:
	var used := 0
	for id in hold:
		used += Data.fish(id)["slots"]
	return used


func hold_cap() -> int:
	return boat_data()["hold"]


func fits(id: String) -> bool:
	return hold_used() + Data.fish(id)["slots"] <= hold_cap()


func hold_value() -> int:
	var total := 0
	for id in hold:
		total += Data.fish(id)["price"]
	return total


func sell_all() -> int:
	var earned := hold_value()
	hold = hold.filter(func(id): return id == "legend")
	coins += earned
	return earned


func sell_one(id: String) -> int:
	if id == "legend" or not hold.has(id):
		return 0
	hold.erase(id)
	coins += Data.fish(id)["price"]
	return Data.fish(id)["price"]


func can_craft(id: String) -> bool:
	var cost: Dictionary = Data.BAITS[id]["cost"]
	for mat in cost:
		if mats[mat] < cost[mat]:
			return false
	return true


func craft(id: String) -> bool:
	if not can_craft(id):
		return false
	var cost: Dictionary = Data.BAITS[id]["cost"]
	for mat in cost:
		mats[mat] -= cost[mat]
	baits[id] += 1
	return true


## 가진 미끼 중 다음 것으로 바꾼다. 바꿀 것이 없으면 false.
func cycle_bait() -> bool:
	var at := Data.BAIT_ORDER.find(bait)
	for step in range(1, Data.BAIT_ORDER.size()):
		var next: String = Data.BAIT_ORDER[(at + step) % Data.BAIT_ORDER.size()]
		if baits[next] > 0:
			bait = next
			return true
	return false


func repair_cost() -> int:
	return ceili((boat_data()["dur"] - durability) / Data.REPAIR_PER_COIN)
