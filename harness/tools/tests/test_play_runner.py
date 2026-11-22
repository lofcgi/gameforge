import pytest

from gf.core.output import GfError
from gf.play import analyze, policies
from gf.play.runner import SAMPLE_TICKS, Run, first_divergence

INFO = {"actions": {"left": {"move": [-1, 0]}, "right": {"move": [1, 0]}, "jump": {}}}


class FakeSession:
    """오른쪽 키를 누르고 있으면 틱마다 x 가 1 늘고, x 가 goal 에 닿으면 끝나는 게임."""

    def __init__(self, goal=1000.0, deaf=False):
        self.header = {"tick_rate": 60, "info": INFO}
        self.tick, self.x, self.goal, self.deaf = 0, 0.0, goal, deaf
        self.held: set[str] = set()
        self.screenshots: list[tuple[int, str]] = []

    def state(self) -> dict:
        moving = "right" in self.held
        return {"tick": self.tick, "t": self.tick / 60, "fps": 60 + self.tick % 7, "level": "fake",
                "player": {"pos": [self.x, 0.0], "vel": [60.0 if moving else 0.0, 0.0], "on_floor": True},
                "goal": {"pos": [self.goal, 0.0], "reached": self.x >= self.goal}, "deaths": 0}

    def step(self, ticks: int) -> dict:
        for _ in range(ticks):
            self.tick += 1
            self.x += 1.0 if "right" in self.held else 0.0
        return self.state()

    def send_input(self, event: dict) -> None:
        if self.deaf:
            return
        (self.held.add if event["down"] else self.held.discard)(event["action"])

    def screenshot(self, path) -> None:
        self.screenshots.append((self.tick, str(path)))


def test_play_samples_on_interval_and_shoots_on_exact_ticks(tmp_path):
    game = FakeSession()
    run = Run(game, shots={10: tmp_path / "a.png", 20: tmp_path / "b.png"})
    run.play([{"tick": 4, "down": True, "action": "right"}, {"tick": 14, "down": False, "action": "right"}], 20)
    assert [tick for tick, _ in game.screenshots] == [10, 20]
    assert [shot["state"]["player"]["pos"][0] for shot in run.shots] == [6.0, 10.0]
    ticks = [sample["tick"] for sample in run.samples]
    assert ticks == sorted(set(ticks)) and set(range(0, 21, SAMPLE_TICKS)) <= set(ticks)
    assert [(entry["tick"], entry["down"], entry["actions"]) for entry in run.inputs] == [
        (4, True, ["right"]), (14, False, ["right"])]


def test_trace_feeds_the_unresponsive_check():
    run = Run(FakeSession())
    run.play([{"tick": 6, "down": True, "action": "right"}, {"tick": 30, "down": True, "action": "jump"}], 60)
    result = analyze.check_inputs(run.inputs, run.samples, run.tick_rate)
    assert result["responded"] == 1
    assert [item["input"] for item in result["unresponsive"]] == ["jump"]


def test_raw_events_keep_device_fields_in_trace():
    run = Run(FakeSession(deaf=True))
    run.play([{"tick": 3, "down": True, "device": "key", "code": "Right", "actions": ["right"], "type": "input"}], 6)
    assert run.inputs[0] == {"type": "input", "tick": 3, "t": 0.05, "down": True,
                             "device": "key", "code": "Right", "actions": ["right"]}


def test_policy_run_presses_only_changes_and_stops_at_goal():
    game = FakeSession(goal=30.0)
    run = Run(game, stop=lambda state: state["goal"]["reached"])
    run.play_policy(policies.load("goal", None, INFO, 0), 600)
    assert run.stopped and run.state["goal"]["reached"]
    assert run.tick < 60
    assert [(entry["down"], entry["actions"]) for entry in run.inputs] == [(True, ["right"])]


def test_first_divergence_detects_inputs_that_never_arrive():
    def played(deaf: bool) -> Run:
        run = Run(FakeSession(deaf=deaf))
        run.play([{"tick": 12, "down": True, "action": "right"}], 60)
        return run

    assert first_divergence(FakeSession(), played(deaf=False).samples) == 15
    assert first_divergence(FakeSession(), played(deaf=True).samples) is None


def test_toward_picks_dominant_axes():
    moves = {"left": [-1, 0, 0], "right": [1, 0, 0], "forward": [0, 0, -1], "back": [0, 0, 1]}
    assert policies.toward(moves, [0.5, 0, -10]) == {"forward"}
    assert policies.toward(moves, [-6, 3, 8]) == {"left", "back"}
    assert policies.toward(moves, [0, 5, 0]) == set()


def _state(t, x, vx=90.0, on_floor=True, deaths=0):
    return {"t": t, "deaths": deaths, "goal": {"pos": [600.0, 0.0], "reached": False},
            "player": {"pos": [x, 0.0], "vel": [vx, 0.0], "on_floor": on_floor}}


def test_goal_policy_jumps_before_the_place_it_died():
    policy = policies.GoalPolicy(INFO)
    assert policy(_state(0.0, 100.0)) == {"right"}
    assert policy(_state(1.0, 200.0)) == {"right"}
    assert policy(_state(1.2, 215.0, on_floor=False)) == {"right"}
    assert policy(_state(1.5, 24.0, vx=0.0, deaths=1)) == {"right"}
    assert policy(_state(3.0, 150.0)) == {"right"}
    assert policy(_state(3.5, 190.0)) == {"right", "jump"}


def test_goal_policy_pulses_jump_when_stuck():
    policy = policies.GoalPolicy(INFO)
    pressed = [("jump" in policy(_state(tick * 0.05, 50.0, vx=0.0))) for tick in range(40)]
    assert not any(pressed[:8])
    assert any(pressed) and not all(pressed[8:])


def test_random_policy_is_seeded():
    def sequence(seed):
        decide = policies.load("random", None, INFO, seed)
        return [sorted(decide({"t": tick * 0.1})) for tick in range(30)]

    assert sequence(1) == sequence(1)
    assert sequence(1) != sequence(2)


def test_python_policy_file_and_unknown_policy(tmp_path):
    (tmp_path / "mine.py").write_text("def decide(state, info):\n    return ['right'] if state['t'] < 1 else []\n")
    decide = policies.load("mine.py", tmp_path, INFO, 0)
    assert decide({"t": 0.5}) == {"right"} and decide({"t": 2}) == set()
    (tmp_path / "empty.py").write_text("x = 1\n")
    with pytest.raises(GfError, match="decide"):
        policies.load("empty.py", tmp_path, INFO, 0)
    with pytest.raises(GfError, match="모르는 정책"):
        policies.load("speedrun", tmp_path, INFO, 0)
