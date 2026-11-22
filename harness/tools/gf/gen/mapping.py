"""의미 입력(프롬프트, 이미지, 길이…)을 모델 스키마에 실제로 있는 필드 이름에 맞춘다.

모델마다 필드 이름이 다르고 설정으로 모델을 바꿀 수 있으므로, 호출 시점의 스키마에 있는
이름만 쓴다. 맞는 필드가 없으면 그 모델의 실제 필드를 보여 주고 실패한다.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gf.core.output import GfError

# 의미 입력 → 후보 필드 이름. 기본 모델들의 실제 스키마에서 확인한 이름이다.
CANDIDATES = {
    "prompt": ["prompt", "text"],
    "image": ["image_url", "image_urls"],
    "end_image": ["end_image_url"],
    "model": ["model_url"],
    "duration": ["duration", "duration_seconds", "music_length_ms"],
}


@dataclass(frozen=True)
class Upload:
    """호출 직전에 fal 에 올릴 로컬 파일."""

    path: Path


def describe_fields(fields: dict) -> str:
    return ", ".join(f"{name}{'*' if spec.get('required') else ''}" for name, spec in fields.items())


def _kinds(spec: dict) -> set[str]:
    return {spec.get("type"), *spec.get("anyOf", [])} - {None, "null"}


def _scalar(name: str, kinds: set[str], value: Any) -> Any:
    if isinstance(value, (Upload, bool)) or not isinstance(value, (int, float)):
        return value
    if "integer" in kinds or ("string" in kinds and "number" not in kinds):
        if value != int(value):
            raise GfError(f"{name} 은(는) 정수만 받는다: {value}")
        return str(int(value)) if "integer" not in kinds else int(value)
    return float(value) if "number" in kinds else value


def coerce(name: str, spec: dict, value: Any) -> Any:
    """값을 필드의 타입에 맞추고 enum·범위를 확인한다."""
    kinds = _kinds(spec)
    if "array" in kinds:
        return value if isinstance(value, list) else [value]
    if isinstance(value, list):
        if len(value) != 1:
            raise GfError(f"{name} 은(는) 값을 하나만 받는데 {len(value)}개가 들어왔다.")
        value = value[0]
    value = _scalar(name, kinds, value)
    if "enum" in spec and value not in spec["enum"]:
        raise GfError(f"{name} 에 넣을 수 없는 값 {value!r}. 가능한 값: {', '.join(map(str, spec['enum']))}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        low, high = spec.get("minimum"), spec.get("maximum")
        if (low is not None and value < low) or (high is not None and value > high):
            raise GfError(f"{name} 값 {value} 이(가) 범위 {low}~{high} 를 벗어난다.")
    return value


def field_for(endpoint: str, fields: dict, semantic: str) -> str:
    for name in CANDIDATES[semantic]:
        if name in fields:
            return name
    raise GfError(
        f"{endpoint} 에는 '{semantic}' 입력을 넣을 필드가 없다 (찾아본 이름: {', '.join(CANDIDATES[semantic])}). "
        f"이 모델의 필드: {describe_fields(fields)}. 맞는 필드가 있으면 --arg 필드=값 으로 직접 넣는다."
    )


def _bind(endpoint: str, fields: dict, semantic: str, value: Any) -> tuple[str, Any]:
    name = field_for(endpoint, fields, semantic)
    if semantic == "duration" and name.endswith("_ms"):
        value = round(value * 1000)
    return name, coerce(name, fields[name], value)


def parse_extra(pair: str, resolve) -> tuple[str, Any]:
    """--arg 필드=값. 값은 JSON 으로 읽히면 JSON, @경로 면 업로드할 파일, 아니면 문자열이다."""
    if "=" not in pair:
        raise GfError(f"--arg 는 필드=값 형태다: {pair}")
    name, text = pair.split("=", 1)
    if text.startswith("@"):
        return name, Upload(resolve(text[1:]))
    try:
        return name, json.loads(text)
    except json.JSONDecodeError:
        return name, text


def build(endpoint: str, fields: dict, semantic: dict, direct: dict, extra: dict) -> dict:
    """호출 인자를 만든다.

    semantic: 의미 입력 이름 → 값 (CANDIDATES 로 필드를 찾는다)
    direct: 스키마 필드 이름 → 값 (명령의 전용 옵션. 모델에 그 필드가 없으면 실패한다)
    extra: --arg 로 받은 필드 이름 → 값 (타입 변환 없이 그대로 넣는다)
    None 인 값은 넣지 않아 모델의 기본값이 쓰인다.
    """
    arguments: dict = {}
    for name, value in semantic.items():
        if value is not None and value != []:
            field, coerced = _bind(endpoint, fields, name, value)
            arguments[field] = coerced
    for name, value in {**{k: v for k, v in direct.items() if v is not None}, **extra}.items():
        if name not in fields:
            raise GfError(f"{endpoint} 에는 '{name}' 필드가 없다. 이 모델의 필드: {describe_fields(fields)}")
        arguments[name] = value if name in extra else coerce(name, fields[name], value)
    missing = [name for name, spec in fields.items() if spec.get("required") and name not in arguments]
    if missing:
        raise GfError(f"{endpoint} 의 필수 필드가 비었다: {', '.join(missing)}. 이 모델의 필드: {describe_fields(fields)}")
    return arguments
