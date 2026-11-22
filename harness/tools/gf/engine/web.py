"""웹 어댑터.

게임 디렉터리를 로컬 HTTP 로 서빙하고, 설치된 Google Chrome 을 Playwright 로 몬다.
자동 실행은 headless(이 맥에서는 ANGLE Metal 로 WebGL 이 GPU 렌더링된다), 사람 플레이는 창을 띄운다.
입력은 Playwright 의 키보드·마우스로 보내므로 게임의 keydown/keyup 처리기를 그대로 탄다.
"""

import functools
import json
import shutil
import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from gf.core.output import GfError
from gf.engine import app_focus
from gf.engine.adapter import Options, require_bridge
from gf.play import session

READY_TIMEOUT_MS = 30000
PUMP_INTERVAL_MS = 100
MOUSE_BUTTONS = ("left", "middle", "right")
NEXT_FRAME = "() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))"


class _Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def install_dependencies(project: Path) -> None:
    """package.json 에 의존성이 있는데 node_modules 가 없으면 bun install 을 한 번 돌린다."""
    manifest = project / "package.json"
    if not manifest.is_file() or not json.loads(manifest.read_text()).get("dependencies"):
        return
    if (project / "node_modules").is_dir():
        return
    bun = shutil.which("bun")
    if not bun:
        raise GfError("bun 을 찾지 못했다. 웹 템플릿의 의존성 설치에 필요하다.")
    result = subprocess.run(
        [bun, "install", "--frozen-lockfile"], cwd=project, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise GfError(f"bun install 실패:\n{result.stderr[-2000:]}")


class WebSession:
    def __init__(self, project: Path, options: Options):
        if options.uncapped:
            raise GfError("web 엔진은 --uncapped 를 지원하지 않는다. Chrome 의 프레임 제한을 자동 실행에서 끌 수 없다. "
                          "여유는 counters.work_ms_avg (프레임당 JS 작업 시간)로 본다.")
        if options.screen is not None:
            raise GfError("--screen 은 Godot 엔진에서만 쓴다. web 의 자동 실행은 창을 띄우지 않는다.")
        if not (project / "index.html").is_file():
            raise GfError(f"{project} 에 index.html 이 없다.")
        install_dependencies(project)
        self._record = options.record
        self._logs: list[dict] = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Handler, directory=str(project)))
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        self._playwright = sync_playwright().start()
        try:
            self._open_page(project, options)
        except BaseException:
            self._shutdown()
            raise

    def _open_page(self, project: Path, options: Options) -> None:
        width, height = options.size
        self._browser = self._playwright.chromium.launch(
            channel="chrome", headless=not options.human, args=[f"--window-size={width},{height}"],
        )
        if options.human:
            self._page = self._browser.new_page(no_viewport=True)
        else:
            self._page = self._browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=options.scale)
        self._watch_console()
        query = f"gf_seed={options.seed}" + ("&gf_manual=1" if options.lockstep else "")
        query += "&gf_record=1" if options.record else ""
        query += "&gf_audio=1" if options.audio else ""
        started = time.monotonic()
        self._page.goto(f"http://127.0.0.1:{self._server.server_address[1]}/index.html?{query}")
        try:
            self._page.wait_for_function("window.__gf && window.__gf.ready", timeout=READY_TIMEOUT_MS)
        except PlaywrightError as exc:
            raise GfError(
                f"window.__gf 브리지가 준비되지 않았다: {exc}\n콘솔: {json.dumps(self._logs, ensure_ascii=False)}"
            ) from exc
        self.load_s = time.monotonic() - started
        bridge = self._page.evaluate(
            "({version: __gf.version, bridge: __gf.bridge, tickRate: __gf.tickRate, info: __gf.info,"
            " size: [innerWidth, innerHeight]})")
        require_bridge(bridge.get("bridge"), project, "bridge.js", "web-2d")
        # 사람이 플레이하는 창은 브라우저 테두리만큼 안쪽이 작다. 재생이 같은 크기로 띄우도록 실제 크기를 적는다.
        self.header = {
            "type": "header", "version": bridge["version"], "engine": "web", "tick_rate": bridge["tickRate"],
            "seed": options.seed, "size": bridge["size"], "info": bridge["info"],
        }
        if self._record:
            self._record.write_text(session.dump_line(self.header))

    def _watch_console(self) -> None:
        def on_console(message) -> None:
            # 404 등은 아래 response 처리기가 URL 과 함께 남기므로 URL 없는 콘솔 줄은 건너뛴다.
            if message.type in ("error", "warning") and not message.text.startswith("Failed to load resource"):
                self._logs.append({"level": message.type, "text": message.text})

        def on_response(response) -> None:
            if response.status >= 400:
                self._logs.append({"level": "error", "text": f"HTTP {response.status}: {response.url}"})

        self._page.on("console", on_console)
        self._page.on("pageerror", lambda error: self._logs.append({"level": "error", "text": str(error)}))
        self._page.on("response", on_response)
        self._page.on("requestfailed", lambda request: self._logs.append(
            {"level": "error", "text": f"요청 실패: {request.url} ({request.failure})"}))

    def step(self, ticks: int) -> dict:
        return self._page.evaluate("n => window.__gf.step(n)", ticks)

    def state(self) -> dict:
        return self._page.evaluate("window.__gf.state()")

    def send_input(self, event: dict) -> None:
        if "action" in event:
            self._key(self.header["info"]["actions"][event["action"]]["keys"][0], event["down"])
        elif event["device"] == "key":
            self._key(event["code"], event["down"])
        elif event["device"] == "mouse":
            self._page.mouse.move(*event["pos"])
            button = MOUSE_BUTTONS[int(event["code"])]
            (self._page.mouse.down if event["down"] else self._page.mouse.up)(button=button)
        else:
            raise GfError(f"web 엔진이 재생할 수 없는 입력 장치: {event['device']}")

    def _key(self, code: str, down: bool) -> None:
        try:
            (self._page.keyboard.down if down else self._page.keyboard.up)(code)
        except PlaywrightError as exc:
            raise GfError(f"키 '{code}' 를 보내지 못했다: {exc}") from exc

    def screenshot(self, path: Path) -> None:
        self._page.evaluate(NEXT_FRAME)
        self._page.screenshot(path=str(path))

    def perf_start(self) -> None:
        self._page.evaluate("window.__gf.perfStart()")

    def perf_stop(self) -> dict:
        return self._page.evaluate("window.__gf.perfStop()")

    def os_pid(self) -> int:
        """키 이벤트를 받는 Chrome 브라우저 프로세스."""
        processes = self._browser.new_browser_cdp_session().send("SystemInfo.getProcessInfo")["processInfo"]
        return next(process["id"] for process in processes if process["type"] == "browser")

    def take_focus(self) -> None:
        """OS 키 이벤트가 페이지에 닿게 한다. 새로 띄운 창은 키 입력이 주소창 쪽에 있을 수 있다."""
        self._page.bring_to_front()
        app_focus.activate(self.os_pid())

    def audio_probe(self) -> dict:
        return self._page.evaluate("window.__gf.audio()")

    def wait(self, seconds: float | None) -> bool:
        """seconds 동안(None 이면 창이 닫힐 때까지) 기다리며 기록을 파일로 옮긴다. 게임이 떠 있으면 True."""
        deadline = None if seconds is None else time.monotonic() + seconds
        while deadline is None or time.monotonic() < deadline:
            remaining = PUMP_INTERVAL_MS if deadline is None else (deadline - time.monotonic()) * 1000
            try:
                self._page.wait_for_timeout(max(1, min(PUMP_INTERVAL_MS, remaining)))
                self._pump()
            except PlaywrightError:
                if self._page.is_closed() or not self._browser.is_connected():
                    return False
                raise
        return True

    def _pump(self) -> None:
        if not self._record:
            return
        lines = self._page.evaluate("window.__gf.drain()")
        with self._record.open("a") as handle:
            handle.writelines(session.dump_line(entry) for entry in lines)

    def logs(self) -> list[dict]:
        return list(self._logs)

    def close(self) -> None:
        try:
            if not self._page.is_closed() and self._browser.is_connected():
                self._pump()
        finally:
            self._shutdown()

    def _shutdown(self) -> None:
        try:
            if hasattr(self, "_browser") and self._browser.is_connected():
                self._browser.close()
        finally:
            self._playwright.stop()
            self._server.shutdown()
            self._server.server_close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.close()
        else:
            self._shutdown()
