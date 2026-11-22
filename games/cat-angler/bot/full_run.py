"""처음부터 끝까지 깨는 봇 정책: 채집 → 미끼 → 출항 → 낚시 → 귀항 → 팔기 → 업그레이드 → 섬 → 전설의 심해어 → 용궁.

gf engine bot --policy bot/full_run.py --seconds 3600 --require-goal
균형 표는 브리지 info["data"] 에서 읽는다. 상태만 보고 판단하므로 CA_START 로 중간부터 시작해도 된다.
"""

import os

RETURN_DURABILITY = 0.4
WAIT_CALLS = 500          # 한 어종을 기다리는 한계 (정책은 3틱마다 불린다: 500번 = 25초)
SPOTS_M = {"shallow": 520.0, "open": 1010.0, "deep": 2010.0}
BUY_ORDER = [("rod", 2), ("boat", 2), ("rod", 3), ("boat", 3)]

# 시험용: CA_BOT_ONLY=amberjack+moray 처럼 주면 그 어종만 노린다. CA_BOT_REEL=always 면 버틸 때도 감는다(줄 끊김 확인용).
ONLY = set(filter(None, os.environ.get("CA_BOT_ONLY", "").split("+")))
REEL_ALWAYS = os.environ.get("CA_BOT_REEL", "") == "always"

LOG = os.environ.get("CA_BOT_LOG", "")
last_key = None

calls = 0
task = None               # 지금 노리는 어종 id
waited = 0
cold = set()              # 이번 자리에서 입질이 없던 어종
last_mode = ""
log = []


def tap(action, every=2):
    return [action] if calls % every == 0 else []


def note(state):
    """CA_BOT_LOG 에 파일 경로를 주면 진행 상황을 한 줄씩 남긴다(긴 실행을 지켜볼 때 쓴다)."""
    global last_key
    key = (state["mode"], state["rod"], state["boat"]["tier"], state["coins"], state["caught"], state["deaths"],
           len(state["hold"]), state["snaps"], state["slips"])
    if LOG and key != last_key:
        last_key = key
        with open(LOG, "a") as out:
            out.write("%7.1f %s rod%d boat%d coins=%d caught=%d hold=%d/%d snaps=%d slips=%d wrecks=%d m=%d baits=%s\n" % (
                state["t"], state["mode"], state["rod"], state["boat"]["tier"], state["coins"], state["caught"],
                state["hold_used"], state["hold_cap"], state["snaps"], state["slips"], state["deaths"],
                state["boat"]["m"], state["baits"]))


def decide(state, info):
    global calls, last_mode
    calls += 1
    data = info["data"]
    note(state)
    if state["mode"] != last_mode:
        last_mode = state["mode"]
        if last_mode == "land":
            cold.clear()
    if state["card"] >= 0:
        return tap("cancel")
    if state["panel"]:
        return panel(state, data)
    if state["mode"] == "land":
        return land(state, data)
    if state["mode"] == "sail":
        return sail(state, data)
    return fish(state, data)


# ---- 계획 ----

def next_buy(state, data):
    for kind, tier in BUY_ORDER:
        if state[kind if kind == "rod" else "boat_tier"] < tier:
            table = data["rods"] if kind == "rod" else data["boats"]
            return kind, table[tier - 1]["price"]
    return None, 0


def view(state):
    """상태에 boat_tier 를 펴 넣는다."""
    state["boat_tier"] = state["boat"]["tier"]
    return state


def spot_m(sp, data):
    if sp["place"]:
        return data["places"][sp["place"]]["x"]
    return SPOTS_M[sp["zone"]]


def candidates(state, data):
    """지금 장비로 노릴 수 있고 미끼와 어창 자리가 있는 어종."""
    boat = data["boats"][state["boat"]["tier"] - 1]
    reach = state["reach"]
    free = state["hold_cap"] - state["hold_used"]
    found = []
    for sp in data["fish"]:
        if ONLY and sp["id"] not in ONLY:
            continue
        zone = next(z for z in data["zones"] if z["id"] == sp["zone"])
        if zone["grade"] > boat["grade"] or sp["dmin"] >= reach or sp["slots"] > free or sp["id"] in cold:
            continue
        if not any(state["baits"][bait] > 0 for bait in sp["baits"]):
            continue
        found.append(sp)
    return found


def pick_task(state, data):
    known = state["caught_ids"]
    best, best_score = None, -1e9
    for sp in candidates(state, data):
        score = sp["price"] / sp["slots"] - 0.02 * abs(spot_m(sp, data) - state["boat"]["m"])
        # 못 낚아 본 어종을 먼저 채우고(도감 13종), 그다음 전설의 심해어를 노린다.
        if sp["id"] == "legend":
            score += 500
        elif sp["id"] not in known:
            score += 1000
        if score > best_score:
            best, best_score = sp, score
    return best


def want_island(state, data):
    return (state["boat"]["tier"] >= 2 and state["mats"]["flower"] == 0 and state["baits"]["legend"] == 0
            and "legend" not in state["hold"] and not state["goal"]["reached"] and state["stock"]["flower"] > 0)


def must_return(state, data):
    boat = data["boats"][state["boat"]["tier"] - 1]
    if "legend" in state["hold"]:
        return True
    if state["boat"]["durability"] < boat["dur"] * RETURN_DURABILITY:
        return True
    return pick_task(state, data) is None and not want_island(state, data)


# ---- 육지 ----

def bench_target(state, data):
    """작업대에서 만들 미끼의 줄 번호. 전설용 재료 한 벌은 남겨 둔다."""
    mats, baits = state["mats"], state["baits"]
    order = data["baits"]
    if baits["legend"] == 0 and all(mats[m] > 0 for m in ("herb", "bug", "berry", "flower")):
        return order.index("legend")
    reserve = 1 if baits["legend"] == 0 else 0
    for index, bait in enumerate(order[:3]):
        if mats[bait] > reserve:
            return index
    return None


def shop_wish(state, data):
    """(가게, 줄 번호) 또는 None."""
    boat = data["boats"][state["boat"]["tier"] - 1]
    kind, price = next_buy(view(state), data)
    if kind == "rod" and state["coins"] >= price:
        return "tackle", 0
    if kind == "boat" and state["coins"] >= price:
        return "shipyard", 1
    missing = boat["dur"] - state["boat"]["durability"]
    if missing > 0 and state["coins"] >= -(-missing // 2):
        return "shipyard", 0
    return None


def land_goal(state, data):
    if state["area"] == "island":
        return "flower" if state["stock"]["flower"] > 0 else "dock"
    if any(fish != "legend" for fish in state["hold"]):
        return "market"
    for mat in ("herb", "bug", "berry"):
        if state["stock"][mat] > 0:
            return mat
    if bench_target(state, data) is not None:
        return "bench"
    wish = shop_wish(state, data)
    if wish:
        return wish[0]
    return "pier"


def land(state, data):
    goal = land_goal(state, data)
    if state["near"] == goal:
        return tap("action")
    if state["area"] == "island":
        stations = {s["id"]: data["island_px"] + s["x"] for s in data["island_stations"]}
    else:
        stations = {s["id"]: s["x"] for s in data["stations"]}
    return ["right"] if stations[goal] > state["player"]["pos"][0] else ["left"]


def panel(state, data):
    name = state["panel"]
    target = None
    if name == "market":
        target = 0 if state["items_ok"][0] else None
    elif name == "bench":
        target = bench_target(state, data)
    elif name in ("shipyard", "tackle"):
        wish = shop_wish(state, data)
        target = wish[1] if wish and wish[0] == name else None
    if target is None or target >= len(state["items_ok"]) or not state["items_ok"][target]:
        return tap("cancel")
    if state["cursor"] != target:
        return tap("down")
    return tap("action")


# ---- 바다 ----

def steer(state, target_px, tolerance=12.0):
    """목표 x 로 배를 몬다. 도착해 멈췄으면 None."""
    x, v = state["boat"]["x"], state["player"]["vel"][0]
    dx = target_px - x
    if abs(dx) <= tolerance:
        return None if abs(v) < 8 else []
    toward = v * dx > 0
    if toward and abs(dx) < abs(v) * 0.7:
        return []
    return ["right"] if dx > 0 else ["left"]


def sail(state, data):
    global task, waited
    if must_return(state, data):
        if state["boat"]["at_pier"]:
            return tap("action")
        return ["left"]
    if want_island(state, data):
        move = steer(state, data["island_dock_px"], 8.0)
        return tap("action") if move is None else move
    sp = pick_task(state, data)
    task = sp["id"]
    waited = 0
    move = steer(state, spot_m(sp, data) * data["x_px"] + 20.0 * len(cold))
    return tap("action") if move is None else move


def fish(state, data):
    global task, waited
    by_id = {sp["id"]: sp for sp in data["fish"]}
    if state["hooked"]:
        return fight(state, data, by_id[state["hooked"]])
    if must_return(state, data):
        return tap("cancel")
    sp = by_id.get(task)
    here = [c["id"] for c in candidates(state, data) if abs(spot_m(c, data) - state["boat"]["m"]) < 30]
    if sp is None or sp["id"] not in here or sp["id"] in state["caught_ids"] and waited == 0:
        best = pick_task(state, data)
        if best is None or best["id"] not in here or must_return(state, data):
            return tap("cancel")
        sp, task, waited = best, best["id"], 0
    if state["interest"] in ("", "sniff"):
        waited += 1
    if waited > WAIT_CALLS:
        cold.add(sp["id"])
        waited = 0
        task = None
        return []
    if state["bait"] not in sp["baits"]:
        return tap("bait")
    low = sp["dmin"]
    high = min(sp["dmax"], state["reach"], state["bed"] - 1.0)
    target = (low + high) / 2.0
    if state["depth"] < target - 1.5:
        return ["down"]
    if state["depth"] > target + 1.5:
        return ["up"]
    return tap("action", 30)


def fight(state, data, sp):
    rod = data["rods"][state["rod"] - 1]
    ratio = sp["str"] / rod["str"]
    held = []
    if state["off"] > 8:
        held.append("right")
    elif state["off"] < -8:
        held.append("left")
    easy = ratio < 0.8 or REEL_ALWAYS
    if (state["tension"] < 0.9 or REEL_ALWAYS) and (easy or state["phase"] in ("tired", "spent")):
        held.append("action")
    return held
