import json
import sys
from typing import Any


class GfError(Exception):
    """사용자에게 그대로 보여 줄 실패."""


def ok(**fields: Any) -> int:
    print(json.dumps({"ok": True, **fields}, ensure_ascii=False))
    return 0


def fail(message: str, **fields: Any) -> int:
    print(json.dumps({"ok": False, "error": message, **fields}, ensure_ascii=False))
    print(message, file=sys.stderr)
    return 1
