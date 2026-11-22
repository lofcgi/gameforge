"""Blender 를 배경 모드로 띄워 scripts/ 의 스크립트를 실행한다."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from gf.core.output import GfError

SCRIPTS = Path(__file__).with_name("scripts")
MAC_APP = Path("/Applications/Blender.app/Contents/MacOS/Blender")


def find_blender() -> str | None:
    found = shutil.which("blender")
    if found:
        return found
    return str(MAC_APP) if MAC_APP.is_file() else None


def require_blender() -> str:
    blender = find_blender()
    if not blender:
        raise GfError(
            "Blender 를 찾지 못했다. `brew install --cask blender` 로 설치하고 `blender --version` 이 되는지 확인한다."
        )
    return blender


def run_script(script: Path, arguments: list[str], cwd: Path | None = None, echo: bool = False) -> dict:
    """스크립트를 실행하고, 스크립트가 GF_RESULT 파일에 쓴 JSON 을 돌려준다 (쓰지 않았으면 빈 dict)."""
    blender = require_blender()
    with tempfile.TemporaryDirectory() as scratch:
        result_path = Path(scratch) / "result.json"
        command = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(script), "--", *arguments]
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False, cwd=cwd, env={**os.environ, "GF_RESULT": str(result_path)}
        )
        output = (completed.stdout + completed.stderr).strip()
        if echo:
            print(output, file=sys.stderr)
        if completed.returncode != 0:
            raise GfError(f"Blender 스크립트 {script.name} 실패 (종료 코드 {completed.returncode}): {output[-1200:]}")
        return json.loads(result_path.read_text()) if result_path.is_file() else {}
