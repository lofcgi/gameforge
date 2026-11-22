"""gameforge PreToolUse 가드. 표준 라이브러리만 쓴다.

gameforge 프로젝트(.gf 폴더가 있는 곳) 안에서만 동작하고, 그 밖에서는 아무 출력 없이 통과시킨다.
이 스크립트 자체가 고장 나면 세션을 막지 않도록 조용히 통과시킨다 (종료 코드 0, 출력 없음).
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
EVIDENCE_TIMEOUT_S = 45
ENV_SAFE_SUFFIXES = (".example", ".sample", ".template", ".dist")
ENV_SAFE_COMMANDS = {"ls", "test", "[", "stat", "touch", "chmod"}
BRIDGE_FILES = {("gf", "gf_bridge.gd"), ("gf", "bridge.js")}

ENV_TOKEN = re.compile(r"""(?:^|[\s"'=<>(/])(\.env(?:\.[\w.-]+)?)(?=$|[\s"';|&)<>])""")
APPROVE = re.compile(r"\bgf\b[^|;&\n]*\bstate\s+approve\b")
DELETES = re.compile(r"\b(rm|rmdir|unlink|mv|truncate|shred)\b|\bgit\s+(clean|checkout|restore)\b|>\s*\S*\.gf/")
PROTECTED_BASH = re.compile(r"\.gf/(judge|state\.json|ledger\.jsonl)")


def find_project(start: Path) -> Path | None:
    """start 에서 위로 올라가며 .gf 폴더가 있는 게임 프로젝트를 찾는다."""
    try:
        start = start.resolve()
    except OSError:
        return None
    for folder in (start, *start.parents):
        if (folder / ".gf").is_dir():
            return folder
    return None


def near_project(folder: Path) -> bool:
    """folder 자신, 조상, 바로 아래 폴더 중에 게임 프로젝트가 있는가 (.env 는 보통 게임 폴더 위에 있다)."""
    if find_project(folder):
        return True
    try:
        with os.scandir(folder) as entries:
            for index, entry in enumerate(entries):
                if index > 300:
                    break
                if entry.is_dir(follow_symlinks=False) and os.path.isdir(os.path.join(entry.path, ".gf")):
                    return True
    except OSError:
        pass
    return False


def is_env_file(name: str) -> bool:
    return (name == ".env" or name.startswith(".env.")) and not name.endswith(ENV_SAFE_SUFFIXES)


def reads_env(command: str) -> bool:
    """.env 를 언급하는 명령 조각이 있고, 그 조각이 내용을 건드리지 않는 명령(ls, test 등)이 아닌가."""
    for segment in re.split(r"&&|\|\||[;|\n]", command):
        names = [name for name in ENV_TOKEN.findall(segment) if is_env_file(name)]
        if not names:
            continue
        words = segment.split()
        if not words or words[0] not in ENV_SAFE_COMMANDS:
            return True
    return False


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def split_words(command: str) -> list[str]:
    try:
        return shlex.split(command, comments=False, posix=True)
    except ValueError:
        return command.split()


def approve_target(command: str, cwd: Path) -> Path | None:
    """`gf ... state approve` 를 실행하는 명령이면 그 대상 게임 프로젝트를, 아니면 None 을 돌려준다.

    따옴표 안의 글(grep "gf state approve" 같은 것)은 한 단어라서 걸리지 않는다.
    """
    words = split_words(command)
    target, seen_gf, approving = cwd, False, False
    for index, word in enumerate(words):
        if word in ("&&", "||", ";", "|"):
            if approving:
                break
            target, seen_gf = cwd, False
        elif word == "gf" or word.endswith("/gf"):
            seen_gf = True
        elif seen_gf and word == "--project" and index + 1 < len(words):
            target = Path(os.path.expandvars(os.path.expanduser(words[index + 1])))
        elif seen_gf and word.startswith("--project="):
            target = Path(os.path.expandvars(os.path.expanduser(word.split("=", 1)[1])))
        elif seen_gf and word == "state" and words[index + 1:index + 2] == ["approve"]:
            approving = True
    if not approving:
        return None
    if not target.is_absolute():
        target = cwd / target
    return find_project(target)


def check_evidence(project: Path) -> str | None:
    """근거가 부족하면 그 이유를 돌려준다. 검사를 돌릴 수 없으면 None (막지 않는다)."""
    try:
        done = subprocess.run(
            ["uv", "run", "-q", "--project", str(HARNESS / "tools"), "gf", "--project", str(project),
             "check", "evidence"],
            capture_output=True, text=True, timeout=EVIDENCE_TIMEOUT_S, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = [line for line in done.stdout.splitlines() if line.strip()]
    try:
        payload = json.loads(lines[-1])
    except (IndexError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("ok") is not False:
        return None
    return str(payload.get("error") or "근거 검사 실패")


def guard_bash(command: str, cwd: Path) -> None:
    in_project = find_project(cwd) is not None

    if (in_project or near_project(cwd)) and reads_env(command):
        deny(
            "[gameforge] .env 의 내용을 읽거나 출력할 수 있는 명령은 막혀 있다. "
            "FAL_KEY 는 gf 명령이 .env 에서 직접 읽으므로 볼 필요가 없다. "
            "키가 있는지만 확인하려면 gf doctor 의 fal_key 값을 본다."
        )

    if PROTECTED_BASH.search(command) and DELETES.search(command) and (in_project or "--project" in command):
        deny(
            "[gameforge] .gf/judge, .gf/state.json, .gf/ledger.jsonl 은 심사 기록·승인 기록·비용 기록이다. "
            "지우거나 덮어쓰지 않는다. 단계는 gf state set/approve 로, 심사 결과는 gf judge record 로 바꾼다."
        )

    if APPROVE.search(command):
        project = approve_target(command, cwd)
        if project is None:
            return
        problem = check_evidence(project)
        if problem:
            deny(
                f"[gameforge] 승인 전에 근거가 필요하다. {problem} "
                "근거를 만든 뒤 결과 파일의 절대 경로를 사용자에게 보여 주고, "
                "사용자가 승인한다고 말하면 다시 gf state approve 를 실행한다."
            )


def guard_read(tool_input: dict, cwd: Path, agent_type: str) -> None:
    raw = tool_input.get("file_path") or tool_input.get("path") or ""
    if not raw:
        return
    path = Path(raw) if os.path.isabs(raw) else cwd / raw

    if is_env_file(path.name) and (near_project(path.parent) or find_project(cwd)):
        deny(
            f"[gameforge] {path.name} 은 읽지 않는다 (API 키가 들어 있다). "
            "gf 명령이 .env 를 직접 읽는다. 키가 있는지는 gf doctor 의 fal_key 로 확인한다."
        )

    if agent_type.split(":")[-1] == "blind-judge":
        project = find_project(path.parent)
        allowed = project is not None and path.resolve().is_relative_to(project / "captures" / "judge")
        if not allowed:
            deny(
                "[gameforge] 블라인드 심사자는 심사 폴더(captures/judge/<id>/)의 X.png, Y.png, target.png, "
                "rubric.md 만 읽는다. 다른 파일은 어느 쪽이 수정 후인지 알려 줄 수 있어 읽지 않는다."
            )


def guard_write(tool_input: dict, cwd: Path) -> None:
    raw = tool_input.get("file_path") or ""
    if not raw:
        return
    path = (Path(raw) if os.path.isabs(raw) else cwd / raw).resolve()
    project = find_project(path.parent)
    if project is None:
        return
    parts = path.relative_to(project).parts

    if is_env_file(path.name):
        deny("[gameforge] .env 는 사용자가 직접 고친다. 에이전트가 쓰거나 고치지 않는다.")
    if parts[:2] == (".gf", "judge") or parts in ((".gf", "state.json"), (".gf", "ledger.jsonl")):
        deny(
            "[gameforge] 승인·심사·비용 기록은 손으로 고치지 않는다. "
            "단계는 gf state set/approve, 심사 결과는 gf judge record 로만 바꾼다."
        )
    if parts in BRIDGE_FILES:
        deny(
            "[gameforge] 브리지 파일은 게임 쪽에서 고치지 않는다. 테스트·봇·캡처가 이 파일을 통해 게임을 본다. "
            "검사를 통과시키려면 브리지가 아니라 게임 코드를 고친다. 브리지 자체의 버그면 사용자에게 보고한다."
        )
    if parts == ("captures", "test", "result.json"):
        deny(
            "[gameforge] 스모크 테스트 기록은 gf engine test 가 쓴다. 손으로 쓰지 않는다."
        )


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(event, dict):
        return
    tool = event.get("tool_name") or ""
    tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return
    cwd = Path(event.get("cwd") or os.getcwd())
    agent_type = str(event.get("agent_type") or "")

    if tool == "Bash":
        guard_bash(str(tool_input.get("command") or ""), cwd)
    elif tool in ("Read", "Grep"):
        guard_read(tool_input, cwd, agent_type)
    elif tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        guard_write(tool_input, cwd)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - 가드가 고장 나도 세션을 막지 않는다
        sys.exit(0)
