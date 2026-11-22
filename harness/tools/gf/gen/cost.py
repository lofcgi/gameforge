"""단가 단위를 실제 사용량으로 환산한다. 정직하게 환산할 수 없는 단위는 None 과 이유를 돌려준다."""

import re

from gf.gen.mapping import CANDIDATES

# 단위 이름 → 사용량 키와 나눌 값.
UNITS = {
    "image": ("images", 1),
    "second": ("seconds", 1),
    "minute": ("seconds", 60),
    "character": ("characters", 1),
    "generation": ("generations", 1),
    "request": ("generations", 1),
}


def _number(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _seconds(fields: dict, arguments: dict) -> float | None:
    """보내는 길이, 없으면 스키마 기본값. 'auto' 처럼 숫자가 아니면 알 수 없다."""
    for name in CANDIDATES["duration"]:
        if name in fields:
            value = _number(arguments.get(name, fields[name].get("default")))
            if value is None:
                return None
            return value / 1000 if name.endswith("_ms") else value
    return None


def usage(fields: dict, arguments: dict) -> dict:
    text = next((arguments[name] for name in CANDIDATES["prompt"] if isinstance(arguments.get(name), str)), "")
    return {
        "images": arguments.get("num_images", fields.get("num_images", {}).get("default", 1)),
        "seconds": _seconds(fields, arguments),
        "characters": len(text),
        "generations": 1,
    }


def estimate(price: dict, used: dict) -> tuple[float | None, str | None]:
    """(추정 비용 USD, 주의할 점). 환산할 수 없으면 비용은 None 이다."""
    unit = str(price.get("unit", "")).strip().lower()
    match = re.fullmatch(r"(?:(\d+)\s+)?([a-z ]+?)s?", unit)
    key = UNITS.get(match.group(2)) if match else None
    if key is None:
        return None, f"단가 단위 '{price.get('unit')}' 는 입력만으로 사용량을 알 수 없어 비용을 추정하지 않았다."
    amount = used.get(key[0])
    if amount is None:
        return None, f"길이를 지정하지 않아 '{price.get('unit')}' 단가로 비용을 추정할 수 없다."
    per = int(match.group(1) or 1) * key[1]
    note = None
    if key[0] in ("images", "seconds"):
        note = "해상도·옵션에 따른 배수는 단가 API 에 없어 기본 단가로만 계산했다."
    return round(price["unit_price"] * amount / per, 4), note
