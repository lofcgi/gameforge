"""세션(엔진 어댑터가 연 게임)을 틱 단위로 몰면서 입력·상태·스크린샷을 남긴다."""

import time
from collections.abc import Callable
from pathlib import Path

SAMPLE_TICKS = 3


class Run:
    """lockstep 세션 위의 한 번의 실행. trace 는 기록 파일과 같은 형식의 항목 목록이다."""

    def __init__(self, session, shots: dict[int, Path] | None = None,
                 stop: Callable[[dict], bool] | None = None):
        self.session = session
        self.tick_rate = session.header["tick_rate"]
        self.state = session.state()
        self.inputs: list[dict] = []
        self.samples: list[dict] = [self._sample()]
        self.shots: list[dict] = []
        self.stopped = False
        self._pending_shots = dict(shots or {})
        self._stop = stop

    @property
    def tick(self) -> int:
        return self.state["tick"]

    def _sample(self) -> dict:
        return {"type": "state", "tick": self.state["tick"], "t": self.state["t"], "state": self.state}

    def send(self, event: dict) -> None:
        self.session.send_input(event)
        entry = {"type": "input", "tick": self.tick, "t": self.state["t"], "down": event["down"]}
        if "action" in event:
            entry["actions"] = [event["action"]]
        else:
            entry.update({k: event[k] for k in ("device", "code", "pos", "actions") if k in event})
        self.inputs.append(entry)

    def advance_to(self, target: int) -> None:
        """target 틱까지 진행한다. 표본 간격과 스크린샷 예약 틱마다 멈춰 기록한다."""
        self._take_due_shots()
        while self.tick < target and not self.stopped:
            next_sample = (self.tick // SAMPLE_TICKS + 1) * SAMPLE_TICKS
            due = [tick for tick in self._pending_shots if tick > self.tick]
            stop_at = min([target, next_sample, *due])
            self.state = self.session.step(stop_at - self.tick)
            self.samples.append(self._sample())
            self._take_due_shots()
            if self._stop is not None and self._stop(self.state):
                self.stopped = True

    def _take_due_shots(self) -> None:
        for tick in sorted(t for t in self._pending_shots if t <= self.tick):
            self.shot(self._pending_shots.pop(tick))

    def shot(self, path: Path) -> None:
        self.session.screenshot(path)
        self.shots.append({"tick": self.tick, "t": self.state["t"], "path": path, "state": self.state})

    def play(self, events: list[dict], end_tick: int) -> None:
        """tick 이 붙은 이벤트를 순서대로 보내고 end_tick 까지 진행한다."""
        for event in events:
            self.advance_to(event["tick"])
            if self.stopped:
                return
            self.send(event)
        self.advance_to(end_tick)

    def play_policy(self, decide: Callable[[dict], set[str]], end_tick: int) -> None:
        """표본 간격마다 정책에게 누르고 있을 액션 집합을 묻고, 바뀐 만큼만 누르거나 뗀다."""
        held: set[str] = set()
        while self.tick < end_tick and not self.stopped:
            wanted = set(decide(self.state))
            for action in sorted(held - wanted):
                self.send({"down": False, "action": action})
            for action in sorted(wanted - held):
                self.send({"down": True, "action": action})
            held = wanted
            self.advance_to(min(end_tick, self.tick + SAMPLE_TICKS))


def comparable(state: dict) -> dict:
    return {key: value for key, value in state.items() if key != "fps"}


def first_divergence(baseline, samples: list[dict]) -> int | None:
    """입력 없이 도는 baseline 세션을 같은 틱까지 진행하며 비교해, 상태가 처음 달라지는 틱을 돌려준다."""
    state = baseline.state()
    for sample in samples:
        if sample["tick"] > state["tick"]:
            state = baseline.step(sample["tick"] - state["tick"])
        if comparable(state) != comparable(sample["state"]):
            return sample["tick"]
    return None


def play_live(session, events: list[dict], seconds: float) -> bool:
    """실시간으로 도는 세션에 이벤트(t 초 기준)를 벽시계에 맞춰 seconds 동안 보낸다. 게임이 먼저 닫히면 False."""
    start = time.monotonic()
    for event in events:
        if event["t"] > seconds:
            break
        if not session.wait(max(0.0, event["t"] - (time.monotonic() - start))):
            return False
        session.send_input(event)
    return session.wait(max(0.0, seconds - (time.monotonic() - start)))
