"""플레이 봇 정책. 정책은 상태를 받아 '지금 누르고 있을 액션 집합'을 돌려주는 함수다."""

import importlib.util
import random
from collections.abc import Callable
from pathlib import Path

from gf.core.output import GfError

BUILTIN = ("goal", "random", "idle")
STUCK_SECONDS = 0.4
STUCK_JUMP_PERIOD = 0.4
JUMP_LEAD_SECONDS = 0.2
RANDOM_HOLD_SECONDS = 0.3

Policy = Callable[[dict], set[str]]


def load(spec: str, project: Path, info: dict, seed: int) -> Policy:
    if spec == "idle":
        return lambda state: set()
    if spec == "random":
        return random_policy(info, seed)
    if spec == "goal":
        return GoalPolicy(info)
    path = (project / spec).resolve()
    if path.suffix == ".py" and path.is_file():
        return _load_python(path, info)
    raise GfError(f"모르는 정책 '{spec}'. 내장: {', '.join(BUILTIN)}. 파일은 .json(액션 스크립트)이나 .py 를 쓴다.")


def _load_python(path: Path, info: dict) -> Policy:
    """.py 정책은 decide(state: dict, info: dict) -> list[str] 를 정의한다."""
    spec = importlib.util.spec_from_file_location("gf_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "decide", None)):
        raise GfError(f"{path}: decide(state, info) 함수가 없다.")
    return lambda state: set(module.decide(state, info))


def random_policy(info: dict, seed: int) -> Policy:
    rng = random.Random(seed)
    actions = sorted(info["actions"])
    held: set[str] = set()
    until = [0.0]

    def decide(state: dict) -> set[str]:
        nonlocal held
        if state["t"] >= until[0]:
            held = {action for action in actions if rng.random() < 0.4}
            until[0] = state["t"] + RANDOM_HOLD_SECONDS
        return held

    return decide


def move_actions(info: dict) -> dict[str, list[float]]:
    return {name: spec["move"] for name, spec in info["actions"].items() if "move" in spec}


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def toward(moves: dict[str, list[float]], delta: list[float]) -> set[str]:
    """delta 방향으로 가는 이동 액션들. 가장 큰 성분의 35% 이상인 축만 누른다."""
    components = {name: _dot(move, delta) for name, move in moves.items()}
    best = max(components.values(), default=0.0)
    if best <= 0.0:
        return set()
    return {name for name, value in components.items() if value > 0.35 * best}


class GoalPolicy:
    """목표 쪽으로 곧장 간다. 막히면 점프하고, 죽은 자리를 기억해 다음에는 그 앞에서 점프한다.

    길 찾기는 하지 않는다. 그레이박스가 '끝까지 갈 수 있는가'를 빠르게 확인하는 용도다.
    """

    def __init__(self, info: dict):
        self.moves = move_actions(info)
        self.has_jump = "jump" in info["actions"]
        if not self.moves:
            raise GfError("goal 정책에는 info.actions 에 move 벡터가 있는 액션이 필요하다.")
        self.axes = [i for i in range(len(next(iter(self.moves.values()))))
                     if any(move[i] for move in self.moves.values())]
        self.death_points: list[list[float]] = []
        self.last_floor_pos: list[float] | None = None
        self.deaths = 0
        self.anchor: tuple[float, list[float]] | None = None

    def _planar(self, a: list[float], b: list[float]) -> float:
        return sum((a[i] - b[i]) ** 2 for i in self.axes) ** 0.5

    def __call__(self, state: dict) -> set[str]:
        player, pos = state["player"], state["player"]["pos"]
        if state["deaths"] > self.deaths:
            self.deaths = state["deaths"]
            if self.last_floor_pos is not None:
                self.death_points.append(self.last_floor_pos)
        elif player.get("on_floor", True):
            self.last_floor_pos = pos
        if state["goal"]["reached"]:
            return set()
        held = toward(self.moves, [g - p for g, p in zip(state["goal"]["pos"], pos)])
        if self.has_jump and (self._near_death_point(player) or self._stuck(state["t"], pos)):
            held.add("jump")
        return held

    def _near_death_point(self, player: dict) -> bool:
        speed = sum(player["vel"][i] ** 2 for i in self.axes) ** 0.5
        lead = speed * JUMP_LEAD_SECONDS
        return any(self._planar(player["pos"], point) < lead for point in self.death_points)

    def _stuck(self, t: float, pos: list[float]) -> bool:
        if self.anchor is None or self._planar(pos, self.anchor[1]) > 1e-3:
            self.anchor = (t, pos)
            return False
        # 점프는 누르는 순간에만 먹으므로, 계속 막혀 있으면 눌렀다 떼기를 되풀이한다.
        stuck_for = t - self.anchor[0] - STUCK_SECONDS
        return stuck_for >= 0 and stuck_for % STUCK_JUMP_PERIOD < STUCK_JUMP_PERIOD / 2
