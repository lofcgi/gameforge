"""macOS 의 Quartz 이벤트로 게임 프로세스에 진짜 키 이벤트를 넣는다 (`gf engine run --os-input`).

브리지 주입(Godot: Input.parse_input_event, web: CDP)과 달리 앱 바깥에서 들어간다: CGEventPostToPid 가 게임 프로세스의
이벤트 큐에 키 이벤트를 넣고, 앱 안에서는 NSEvent 로 도착해 사람이 누른 키와 같은 처리 경로를 탄다
(Godot: 창의 keyDown → Input → _input, Chrome: 브라우저 프로세스 → 렌더러 → DOM keydown).
거치지 않는 것은 키보드 하드웨어·드라이버와, 어느 앱이 키를 받을지 정하는 WindowServer 의 포커스 판단이다.
특정 프로세스에만 보내므로 다른 앱에 글자가 새지 않는다. 게임 창이 키 입력을 받는 상태(앱이 맨 앞)여야 하고,
터미널 앱에 손쉬운 사용 권한이 있어야 한다. 권한은 여기서 바꾸지 않는다.
"""

import ctypes
import ctypes.util
import sys

from gf.core.output import GfError

# 미국 ANSI 자판의 가상 키코드. 이름은 Godot 의 물리 키 이름과 web 의 KeyboardEvent.code 를 함께 받는다.
_LETTERS = {"A": 0, "S": 1, "D": 2, "F": 3, "H": 4, "G": 5, "Z": 6, "X": 7, "C": 8, "V": 9, "B": 11, "Q": 12,
            "W": 13, "E": 14, "R": 15, "Y": 16, "T": 17, "O": 31, "U": 32, "I": 34, "P": 35, "L": 37, "J": 38,
            "K": 40, "N": 45, "M": 46}
_DIGITS = {"1": 18, "2": 19, "3": 20, "4": 21, "6": 22, "5": 23, "9": 25, "7": 26, "8": 28, "0": 29}
_NAMED = {"Space": 49, "Enter": 36, "Escape": 53, "Tab": 48, "Shift": 56, "Ctrl": 59,
          "Left": 123, "Right": 124, "Down": 125, "Up": 126}
KEYCODES = {
    **_LETTERS, **_DIGITS, **_NAMED,
    **{f"Key{name}": code for name, code in _LETTERS.items()},
    **{f"Digit{name}": code for name, code in _DIGITS.items()},
    **{f"Arrow{name}": _NAMED[name] for name in ("Left", "Right", "Down", "Up")},
    "ShiftLeft": 56, "ControlLeft": 59,
}


def keycode(name: str) -> int:
    if name not in KEYCODES:
        raise GfError(f"OS 키 이벤트로 보낼 줄 모르는 키: {name}")
    return KEYCODES[name]


def key_for(event: dict, info: dict) -> str:
    """입력 이벤트(액션 또는 원시 키)가 누를 키 이름."""
    if "action" in event:
        keys = info["actions"][event["action"]].get("keys")
        if not keys:
            raise GfError(f"액션 {event['action']} 에 키가 없다.")
        return keys[0]
    if event.get("device") != "key":
        raise GfError("OS 입력은 키보드만 보낸다.")
    return event["code"]


def _quartz():
    if sys.platform != "darwin":
        raise GfError("--os-input 은 macOS 에서만 쓴다.")
    quartz = ctypes.cdll.LoadLibrary(ctypes.util.find_library("ApplicationServices"))
    quartz.CGPreflightPostEventAccess.restype = ctypes.c_bool
    quartz.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
    quartz.CGEventCreateKeyboardEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool]
    quartz.CGEventPostToPid.argtypes = [ctypes.c_int, ctypes.c_void_p]
    quartz.CFRelease.argtypes = [ctypes.c_void_p]
    return quartz


def require_permission() -> None:
    if not _quartz().CGPreflightPostEventAccess():
        raise GfError(
            "이 터미널 앱에는 키 이벤트를 보낼 권한이 없다. 시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용에서 "
            "지금 쓰는 터미널 앱을 켜야 한다(사용자가 직접 한다). 권한 없이 확인하려면 gf engine run --record 로 직접 누른다."
        )


def post_key(pid: int, name: str, down: bool) -> None:
    quartz = _quartz()
    event = quartz.CGEventCreateKeyboardEvent(None, keycode(name), down)
    if not event:
        raise GfError("키 이벤트를 만들지 못했다.")
    quartz.CGEventPostToPid(pid, event)
    quartz.CFRelease(event)
