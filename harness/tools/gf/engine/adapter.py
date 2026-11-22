"""엔진 어댑터 공통 인터페이스.

어댑터는 게임을 띄워 `Session` 을 돌려준다. 세션은 게임 안의 브리지(templates/README.md)와 대화한다.
godot 과 web 이 같은 메서드를 구현하므로 명령과 플레이 봇은 엔진을 몰라도 된다.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from gf.core import state
from gf.core.output import GfError
from gf.core.paths import TEMPLATES

DEFAULT_SIZE = (1280, 720)
BRIDGE_VERSION = 2
"""템플릿의 브리지(gf_bridge.gd 의 BRIDGE, bridge.js 의 BRIDGE)와 같은 값."""


@dataclass
class Options:
    lockstep: bool = True
    """True 면 step() 으로만 시간이 흐른다(결정적). False 면 실시간으로 돈다."""
    size: tuple[int, int] = DEFAULT_SIZE
    seed: int = 0
    record: Path | None = None
    """사람(또는 실시간 스크립트)의 입력을 남길 jsonl 경로."""
    human: bool = False
    """사람이 직접 플레이할 창을 띄운다."""
    uncapped: bool = False
    """수직 동기화를 끄고 낼 수 있는 최대 프레임을 잰다."""
    audio: bool = False
    """브리지의 소리 측정을 켠다 (`audio_probe()` 로 읽는다)."""
    scale: float = 1.0
    """화면 배율. web 의 devicePixelRatio. Godot 은 크기가 처음부터 물리 픽셀이라 쓰지 않는다."""
    screen: int | None = None
    """Godot 창을 띄울 화면 번호. 없으면 Godot 이 고른다."""


class Session(Protocol):
    header: dict
    """기록 파일의 header 와 같은 내용. header["info"] 가 게임이 선언한 액션이다."""
    load_s: float
    """실행부터 브리지가 준비될 때까지 걸린 시간."""

    def step(self, ticks: int) -> dict: ...
    def state(self) -> dict: ...
    def send_input(self, event: dict) -> None: ...
    def screenshot(self, path: Path) -> None: ...
    def perf_start(self) -> None: ...
    def perf_stop(self) -> dict: ...
    def audio_probe(self) -> dict: ...
    def os_pid(self) -> int: ...
    def take_focus(self) -> None: ...
    def wait(self, seconds: float | None) -> bool: ...
    def logs(self) -> list[dict]: ...
    def close(self) -> None: ...


def open_session(project: Path, options: Options) -> Session:
    engine = state.load(project)["engine"]
    if engine == "godot":
        from gf.engine.godot import GodotSession

        return GodotSession(project, options)
    if engine == "web":
        from gf.engine.web import WebSession

        return WebSession(project, options)
    raise GfError(f"지원하지 않는 엔진: {engine}")


def require_bridge(found: int | None, project: Path, name: str, template: str) -> None:
    """게임에 든 브리지가 이 하네스와 맞는 버전인지 본다. 옛 템플릿으로 만든 게임은 브리지 파일을 바꿔 줘야 한다."""
    if found != BRIDGE_VERSION:
        source = TEMPLATES / template / "gf" / name
        raise GfError(
            f"게임의 gf/{name} 가 이 하네스와 맞지 않는다 (브리지 버전 {found or 1}, 필요 {BRIDGE_VERSION}). "
            f"하네스의 것으로 바꾼다: cp '{source}' '{project / 'gf' / name}'"
        )


def parse_size(text: str) -> tuple[int, int]:
    parts = text.lower().split("x")
    if len(parts) != 2 or not all(part.isdigit() and int(part) > 0 for part in parts):
        raise GfError(f"--size 는 WxH 형식이다 (예: 1280x720): {text}")
    return int(parts[0]), int(parts[1])


def count_levels(logs: list[dict]) -> dict:
    return {
        "errors": sum(1 for entry in logs if entry["level"] == "error"),
        "warnings": sum(1 for entry in logs if entry["level"] == "warning"),
    }
