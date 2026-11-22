"""상태 표본으로 '입력에 게임이 반응했는가'를 판정한다.

반응의 정의: 누른 뒤 threshold 안에, 위치·시간을 뺀 상태(플래그, 카운터)가 바뀌거나
속도의 변화율이 누르기 전과 달라진다. 위치는 관성으로도 변하고 속도는 중력으로도 변하므로
그 자체로는 반응으로 치지 않는다. 착지처럼 입력과 무관한 변화가 같은 구간에 겹치면
반응한 것으로 잘못 볼 수 있으니, 결과는 '후보'로 다룬다.
"""

from gf.core.output import GfError

DEFAULT_THRESHOLD_S = 0.25
ACCEL_TOLERANCE = 1e-3
IGNORED_KEYS = ("tick", "t", "fps")
REQUIRED_STATE = ("tick", "t", "level", "player", "goal", "deaths")


def validate_state(state: dict) -> None:
    """브리지 계약의 필수 필드를 확인한다."""
    missing = [key for key in REQUIRED_STATE if key not in state]
    player, goal = state.get("player", {}), state.get("goal", {})
    missing += [f"player.{key}" for key in ("pos", "vel") if key not in player]
    missing += [f"goal.{key}" for key in ("pos", "reached") if key not in goal]
    if missing:
        raise GfError(f"브리지 상태에 필수 필드가 없다: {', '.join(missing)}")


def _velocity(state: dict) -> list[float]:
    return list(state["player"]["vel"])


def _flags(state: dict) -> dict:
    """위치·속도·시간을 뺀 나머지 상태."""
    rest = {key: value for key, value in state.items() if key not in IGNORED_KEYS}
    rest["player"] = {k: v for k, v in state["player"].items() if k not in ("pos", "vel")}
    return rest


def _rate(earlier: dict, later: dict) -> list[float]:
    ticks = later["tick"] - earlier["tick"]
    return [(b - a) / ticks for a, b in zip(_velocity(earlier["state"]), _velocity(later["state"]))]


def _differs(a: list[float], b: list[float]) -> bool:
    return any(abs(x - y) > ACCEL_TOLERANCE * max(1.0, abs(x), abs(y)) for x, y in zip(a, b))


def responded(before: list[dict], after: list[dict]) -> bool:
    """before: 누르기 전 표본(마지막이 기준), after: 누른 뒤 threshold 안의 표본."""
    base = before[-1]
    prior_rate = _rate(before[-2], base) if len(before) > 1 else [0.0] * len(_velocity(base["state"]))
    for sample in after:
        if _flags(sample["state"]) != _flags(base["state"]):
            return True
        if _differs(_rate(base, sample), prior_rate):
            return True
    return False


def label(entry: dict) -> str:
    if entry.get("actions"):
        return "+".join(entry["actions"])
    return f"{entry['device']}:{entry['code']}"


def check_inputs(inputs: list[dict], samples: list[dict], tick_rate: int,
                 threshold_s: float = DEFAULT_THRESHOLD_S) -> dict:
    """누름 입력마다 반응 여부를 판정한다.

    게임 액션에 매핑되지 않은 키는 판정하지 않고 unmapped 로만 센다.
    앞뒤 표본이 없어 판정할 수 없는 입력은 unverified 로 센다.
    """
    window = round(threshold_s * tick_rate)
    result = {"pressed": 0, "responded": 0, "unmapped": 0, "unverified": 0, "unresponsive": []}
    for entry in inputs:
        if not entry["down"]:
            continue
        if entry.get("device") == "key" and not entry.get("actions"):
            result["unmapped"] += 1
            continue
        tick = entry["tick"]
        before = [s for s in samples if s["tick"] <= tick]
        after = [s for s in samples if tick < s["tick"] <= tick + window]
        if not before or not after:
            result["unverified"] += 1
            continue
        result["pressed"] += 1
        if responded(before, after):
            result["responded"] += 1
        else:
            result["unresponsive"].append(
                {"tick": tick, "t": round(tick / tick_rate, 3), "input": label(entry),
                 "threshold_s": threshold_s, "state": before[-1]["state"]}
            )
    return result


def require_liveness(check: dict) -> None:
    """합성 입력이 게임의 입력 처리기에 닿지 않는 거짓 양성을 막는다."""
    if check["pressed"] > 0 and check["responded"] == 0:
        raise GfError(
            f"입력 생존 확인 실패: 입력 {check['pressed']}개를 보냈지만 게임 상태가 한 번도 반응하지 않았다. "
            "입력이 게임의 처리기에 닿지 않는다."
        )


def position_drift(recorded: list[dict], replayed: list[dict]) -> dict | None:
    """같은 틱의 기록 표본과 재생 표본 사이 플레이어 위치 차이."""
    by_tick = {sample["tick"]: sample["state"] for sample in replayed}
    distances = []
    for sample in recorded:
        other = by_tick.get(sample["tick"])
        if other is None:
            continue
        a, b = sample["state"]["player"]["pos"], other["player"]["pos"]
        distances.append(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5)
    if not distances:
        return None
    return {"compared": len(distances), "max": round(max(distances), 4), "final": round(distances[-1], 4)}
