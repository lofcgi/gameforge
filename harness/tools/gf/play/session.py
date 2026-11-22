"""입력 기록 파일(captures/sessions/<id>.jsonl) 형식.

첫 줄은 header, 이후는 input 과 state 가 틱 순서로 섞여 있다.
  {"type": "header", "version": 1, "engine": "godot", "tick_rate": 60, "seed": 0, "size": [w, h], "info": {...}}
  {"type": "input", "tick": 31, "t": 0.5167, "down": true, "device": "key", "code": "Right", "actions": ["right"]}
  {"type": "state", "tick": 36, "t": 0.6, "state": {...}}
"""

import json
from dataclasses import dataclass
from pathlib import Path

from gf.core.output import GfError

VERSION = 1
HEADER_KEYS = ("version", "engine", "tick_rate", "seed", "info")
INPUT_KEYS = ("tick", "down", "device", "code")


@dataclass
class Session:
    header: dict
    inputs: list[dict]
    samples: list[dict]

    @property
    def last_tick(self) -> int:
        return max((entry["tick"] for entry in self.inputs + self.samples), default=0)


def dump_line(entry: dict) -> str:
    return json.dumps(entry, ensure_ascii=False) + "\n"


def load(path: Path) -> Session:
    if not path.is_file():
        raise GfError(f"기록 파일이 없다: {path}")
    return parse(path.read_text().splitlines(), str(path))


def parse(lines: list[str], source: str = "session") -> Session:
    entries = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            entries.append((number, json.loads(line)))
        except json.JSONDecodeError as exc:
            raise GfError(f"{source}:{number}: JSON 오류: {exc}") from exc
    if not entries or entries[0][1].get("type") != "header":
        raise GfError(f"{source}: 첫 줄이 header 가 아니다.")
    header = entries[0][1]
    _require(header, HEADER_KEYS, f"{source}:1")
    if header["version"] != VERSION:
        raise GfError(f"{source}: 기록 형식 버전 {header['version']} 은 지원하지 않는다 (지원: {VERSION}).")
    inputs, samples = [], []
    for number, entry in entries[1:]:
        where = f"{source}:{number}"
        if entry.get("type") == "input":
            _require(entry, INPUT_KEYS, where)
            inputs.append(entry)
        elif entry.get("type") == "state":
            _require(entry, ("tick", "state"), where)
            samples.append(entry)
        else:
            raise GfError(f"{where}: 모르는 type '{entry.get('type')}'.")
    return Session(header, inputs, samples)


def _require(entry: dict, keys: tuple[str, ...], where: str) -> None:
    missing = [key for key in keys if key not in entry]
    if missing:
        raise GfError(f"{where}: 필드가 없다: {', '.join(missing)}")
