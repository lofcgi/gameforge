"""macOS 에서 앞에 있는 앱을 알아내고 다시 앞으로 보낸다.

Godot 은 창을 띄우며 스스로 활성 앱이 된다. 자동 실행에서는 그 포커스를 원래 앱에 돌려준다: 사용자가 하던 일을
빼앗지 않고, 비활성인 Godot 은 더 잃을 포커스가 없어 넣어 둔 입력이 풀리지 않는다(gf_bridge.gd 의 "앱 포커스").
손쉬운 사용·자동화 권한이 필요 없는 길만 쓴다(lsappinfo 와 NSRunningApplication).
"""

import ctypes
import ctypes.util
import re
import subprocess
import sys

ACTIVATE_IGNORING_OTHER_APPS = 2


def supported() -> bool:
    return sys.platform == "darwin"


def parse_pid(info: str) -> int | None:
    match = re.search(r'"pid"\s*=\s*(\d+)', info)
    return int(match.group(1)) if match else None


def frontmost_pid() -> int | None:
    """지금 활성인 앱의 pid. 없으면 None."""
    front = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True, check=False).stdout.strip()
    if not front.startswith("ASN:"):
        return None
    info = subprocess.run(["lsappinfo", "info", "-only", "pid", front], capture_output=True, text=True, check=False)
    return parse_pid(info.stdout)


def activate(pid: int) -> bool:
    """pid 의 앱을 활성화한다. 그런 앱이 없으면 False."""
    objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
    ctypes.cdll.LoadLibrary("/System/Library/Frameworks/AppKit.framework/AppKit")
    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.restype = ctypes.c_void_p

    def send(restype, *argtypes):
        return ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *argtypes))

    app = send(ctypes.c_void_p, ctypes.c_int)(
        objc.objc_getClass(b"NSRunningApplication"),
        objc.sel_registerName(b"runningApplicationWithProcessIdentifier:"), pid,
    )
    if not app:
        return False
    return bool(send(ctypes.c_bool, ctypes.c_ulong)(
        app, objc.sel_registerName(b"activateWithOptions:"), ACTIVATE_IGNORING_OTHER_APPS))
