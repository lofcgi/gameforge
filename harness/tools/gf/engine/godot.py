"""Godot 어댑터.

`--headless` 는 더미 렌더러라 픽셀이 나오지 않는다. 그래서 항상 창을 띄우고, 프로젝트의 GfBridge
오토로드가 뷰포트 텍스처를 PNG 로 저장한다. lockstep 에서는 `--fixed-fps` 로 벽시계와 분리하고
브리지가 step 명령을 받은 만큼만 물리 틱을 진행한다.
"""

import json
import re
import shutil
import socket
import subprocess
import time
from pathlib import Path

from gf.core.output import GfError
from gf.engine import app_focus
from gf.engine.adapter import Options, require_bridge

CONNECT_TIMEOUT_S = 60
REPLY_TIMEOUT_S = 60
YIELD_FOCUS_MS = 1000
IMPORT_TIMEOUT_S = 600
WINDOW_POSITION = "40,40"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOG_LEVELS = (
    ("SCRIPT ERROR:", "error"),
    ("USER SCRIPT ERROR:", "error"),
    ("USER ERROR:", "error"),
    ("ERROR:", "error"),
    ("USER WARNING:", "warning"),
    ("WARNING:", "warning"),
)
# 종료 정리 중에 나오는 줄. 재생 중인 오디오 스트림을 오디오 스레드가 아직 쥐고 있으면 실행마다 나왔다 안 나왔다
# 한다(실측: AudioStreamMP3 재생 중 종료). 게임 중의 오류가 아니므로 경고로만 남긴다.
EXIT_NOISE = ("resources still in use at exit", "instances were leaked at exit")


def parse_log(text: str) -> list[dict]:
    """Godot 은 스크립트 오류가 나도 종료 코드 0 을 내므로 출력에서 오류·경고 줄을 골라낸다."""
    entries: list[dict] = []
    for raw in text.splitlines():
        line = ANSI.sub("", raw).strip()
        level = next((lv for prefix, lv in LOG_LEVELS if line.startswith(prefix)), None)
        if level == "error" and any(noise in line for noise in EXIT_NOISE):
            level = "warning"
        if level:
            entries.append({"level": level, "text": line})
        elif line.startswith("at:") and entries:
            entries[-1]["text"] += " " + line
    return entries


def godot_binary() -> str:
    binary = shutil.which("godot")
    if not binary:
        raise GfError("godot 실행 파일을 찾지 못했다. Godot 4 를 설치하고 PATH 에 둔다.")
    return binary


def tick_rate(project: Path) -> int:
    match = re.search(r"physics_ticks_per_second=(\d+)", (project / "project.godot").read_text())
    return int(match.group(1)) if match else 60


def import_project(project: Path) -> None:
    """.godot 캐시(전역 클래스, 가져온 리소스)를 갱신한다. 새 에셋은 이 단계를 거쳐야 load 된다."""
    if not (project / "project.godot").is_file():
        raise GfError(f"{project} 에 project.godot 이 없다.")
    result = subprocess.run(
        [godot_binary(), "--headless", "--path", str(project), "--import"],
        capture_output=True, text=True, timeout=IMPORT_TIMEOUT_S, check=False,
    )
    errors = [e["text"] for e in parse_log(result.stdout + result.stderr) if e["level"] == "error"]
    if result.returncode != 0 or errors:
        detail = "\n".join(errors[:10]) or result.stderr[-2000:]
        raise GfError(f"Godot 가져오기(import) 실패 (종료 코드 {result.returncode}):\n{detail}")


class GodotSession:
    def __init__(self, project: Path, options: Options):
        import_project(project)
        self._log_path = project / ".gf" / "godot.log"
        self._server = socket.create_server(("127.0.0.1", 0))
        auto = not options.human
        front = app_focus.frontmost_pid() if auto and app_focus.supported() else None
        started = time.monotonic()
        self._log = self._log_path.open("w")
        self._process = subprocess.Popen(
            self._command(project, options, self._server.getsockname()[1]),
            stdout=self._log, stderr=subprocess.STDOUT,
        )
        try:
            self._socket = self._accept()
            self._reader = self._socket.makefile("r", encoding="utf-8")
            hello = self._read()
            require_bridge(hello.get("bridge"), project, "gf_bridge.gd", "godot-2d")
            self.header = hello["header"]
            self.load_s = time.monotonic() - started
            if auto and tuple(self.header["size"]) != tuple(options.size):
                got = "x".join(str(value) for value in self.header["size"])
                raise GfError(
                    f"Godot 창이 요청한 {options.size[0]}x{options.size[1]} 이 아니라 {got} 로 떴다. 창이 놓인 화면보다 "
                    "큰 크기다. --screen 으로 더 큰 화면을 고르거나 --size 를 줄인다 (Godot 의 크기는 물리 픽셀이다)."
                )
            if auto:
                self.focus = self._yield_focus(front)
        except BaseException:
            self._kill()
            raise

    def _yield_focus(self, front: int | None) -> dict:
        """Godot 이 가져간 포커스를 원래 앞에 있던 앱에 돌려준다. 이유는 gf_bridge.gd 의 "앱 포커스" 에 있다."""
        if front is None or front == self._process.pid or not app_focus.activate(front):
            return {"yielded": False, "reason": "포커스를 돌려줄 앱을 찾지 못했다"}
        active = self._request(cmd="yield_focus", wait_ms=YIELD_FOCUS_MS)["app_active"]
        return {"yielded": not active}

    def _command(self, project: Path, options: Options, port: int) -> list[str]:
        width, height = options.size
        command = [godot_binary(), "--path", str(project), "--resolution", f"{width}x{height}"]
        command += ["--position", WINDOW_POSITION] if options.screen is None else ["--screen", str(options.screen)]
        if options.lockstep:
            command += ["--fixed-fps", str(tick_rate(project)), "--disable-vsync"]
        elif options.uncapped:
            command += ["--disable-vsync"]
        command += ["--", f"--gf-port={port}", f"--gf-seed={options.seed}"]
        if options.lockstep:
            command.append("--gf-lockstep")
        if not options.human:
            command.append("--gf-auto")
        if options.audio:
            command.append("--gf-audio")
        if options.record:
            command.append(f"--gf-record={options.record}")
        return command

    def _accept(self) -> socket.socket:
        self._server.settimeout(0.2)
        deadline = time.monotonic() + CONNECT_TIMEOUT_S
        while time.monotonic() < deadline:
            if self._process.poll() is not None:
                raise GfError(f"Godot 이 브리지 접속 전에 종료했다 (코드 {self._process.returncode}).\n{self._log_tail()}")
            try:
                connection, _ = self._server.accept()
            except TimeoutError:
                continue
            connection.settimeout(REPLY_TIMEOUT_S)
            return connection
        raise GfError(
            f"{CONNECT_TIMEOUT_S}초 안에 GfBridge 가 접속하지 않았다. project.godot 의 오토로드에 GfBridge 가 있는지 확인한다.\n"
            + self._log_tail()
        )

    def _log_tail(self) -> str:
        return "\n".join(ANSI.sub("", self._log_path.read_text()).splitlines()[-15:])

    def _read(self) -> dict:
        try:
            line = self._reader.readline()
        except TimeoutError as exc:
            raise GfError(f"Godot 이 {REPLY_TIMEOUT_S}초 동안 응답하지 않았다.\n{self._log_tail()}") from exc
        if not line:
            raise GfError(f"Godot 과의 연결이 끊겼다.\n{self._log_tail()}")
        reply = json.loads(line)
        if reply.get("ok") is False:
            raise GfError(f"GfBridge 오류: {reply['error']}")
        return reply

    def _request(self, **message) -> dict:
        try:
            self._socket.sendall((json.dumps(message) + "\n").encode())
        except OSError as exc:
            raise GfError(f"Godot 에 명령을 보내지 못했다: {exc}\n{self._log_tail()}") from exc
        return self._read()

    def step(self, ticks: int) -> dict:
        return self._request(cmd="step", n=ticks)["state"]

    def state(self) -> dict:
        return self._request(cmd="state")["state"]

    def send_input(self, event: dict) -> None:
        if "action" in event:
            self._request(cmd="action", name=event["action"], down=event["down"])
        else:
            fields = {key: event[key] for key in ("device", "code", "down", "pos") if key in event}
            self._request(cmd="input", **fields)

    def screenshot(self, path: Path) -> None:
        self._request(cmd="screenshot", path=str(path))

    def perf_start(self) -> None:
        self._request(cmd="perf_start")

    def perf_stop(self) -> dict:
        reply = self._request(cmd="perf_stop")
        return {"frame_ms": reply["frame_ms"], "counters": reply["counters"]}

    def os_pid(self) -> int:
        return self._process.pid

    def take_focus(self) -> None:
        app_focus.activate(self._process.pid)

    def audio_probe(self) -> dict:
        return self._request(cmd="audio")["audio"]

    def wait(self, seconds: float | None) -> bool:
        """seconds 동안(None 이면 창이 닫힐 때까지) 기다린다. 게임이 아직 떠 있으면 True."""
        try:
            self._process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            return True
        return False

    def logs(self) -> list[dict]:
        return parse_log(self._log_path.read_text())

    def close(self) -> None:
        if self._process.poll() is None:
            try:
                self._socket.sendall(b'{"cmd": "quit"}\n')
                self._process.wait(timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                self._kill()
                raise GfError(f"Godot 이 정상 종료하지 않아 강제로 끝냈다.\n{self._log_tail()}") from None
        self._release()

    def _kill(self) -> None:
        self._process.kill()
        self._process.wait()
        self._release()

    def _release(self) -> None:
        if hasattr(self, "_socket"):
            self._socket.close()
        self._server.close()
        self._log.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.close()
        elif self._process.poll() is None:
            self._kill()
        else:
            self._release()
