"""액션 스크립트(JSON)를 시간순 입력 이벤트로 바꾼다.

형식: {"seed": 1, "actions": [...]} 또는 항목 배열. 항목은 다음 중 하나다.
  {"t": 0.5, "press": "right"}             액션을 누른다
  {"t": 1.2, "release": "right"}           액션을 뗀다
  {"t": 1.0, "tap": "jump", "hold": 0.1}   눌렀다가 hold 초 뒤에 뗀다 (기본 0.1)
  {"t": 2.0, "key": "KeyA", "down": true}  엔진 고유 키 코드를 직접 보낸다
"""

import json
from pathlib import Path

from gf.core.output import GfError

DEFAULT_TAP_HOLD = 0.1
VERBS = ("press", "release", "tap", "key")


def load(path: Path) -> dict:
    if not path.is_file():
        raise GfError(f"액션 스크립트가 없다: {path}")
    try:
        return parse(json.loads(path.read_text()))
    except json.JSONDecodeError as exc:
        raise GfError(f"액션 스크립트 JSON 오류 ({path}): {exc}") from exc


def parse(data) -> dict:
    """{"seed": int | None, "events": [{"t", "down", "action" | ("device", "code")}]} 를 돌려준다."""
    if isinstance(data, list):
        data = {"actions": data}
    if not isinstance(data, dict) or not isinstance(data.get("actions"), list):
        raise GfError('액션 스크립트는 배열이거나 {"actions": [...]} 여야 한다.')
    events = []
    for index, item in enumerate(data["actions"]):
        events.extend(_parse_item(index, item))
    events.sort(key=lambda event: event["t"])
    return {"seed": data.get("seed"), "events": events}


def _parse_item(index: int, item) -> list[dict]:
    where = f"actions[{index}]"
    if not isinstance(item, dict):
        raise GfError(f"{where}: 객체여야 한다.")
    t = item.get("t")
    if isinstance(t, bool) or not isinstance(t, (int, float)) or t < 0:
        raise GfError(f"{where}: t 는 0 이상의 숫자여야 한다.")
    verbs = [verb for verb in VERBS if verb in item]
    if len(verbs) != 1:
        raise GfError(f"{where}: {', '.join(VERBS)} 중 정확히 하나가 있어야 한다.")
    verb = verbs[0]
    name = item[verb]
    if not isinstance(name, str) or not name:
        raise GfError(f"{where}: {verb} 값은 비어 있지 않은 문자열이어야 한다.")
    if verb == "key":
        if not isinstance(item.get("down"), bool):
            raise GfError(f"{where}: key 항목에는 down(true/false)이 필요하다.")
        return [{"t": float(t), "down": item["down"], "device": "key", "code": name}]
    if verb == "tap":
        hold = item.get("hold", DEFAULT_TAP_HOLD)
        if isinstance(hold, bool) or not isinstance(hold, (int, float)) or hold <= 0:
            raise GfError(f"{where}: hold 는 0보다 큰 숫자여야 한다.")
        return [
            {"t": float(t), "down": True, "action": name},
            {"t": float(t) + hold, "down": False, "action": name},
        ]
    return [{"t": float(t), "down": verb == "press", "action": name}]


def to_ticks(events: list[dict], tick_rate: int) -> list[dict]:
    return [{**event, "tick": round(event["t"] * tick_rate)} for event in events]


def require_known_actions(events: list[dict], info: dict) -> None:
    known = info.get("actions", {})
    unknown = sorted({e["action"] for e in events if "action" in e and e["action"] not in known})
    if unknown:
        raise GfError(f"게임이 선언하지 않은 액션: {', '.join(unknown)}. 가능한 액션: {', '.join(known)}")
