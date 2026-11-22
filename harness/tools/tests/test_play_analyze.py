import pytest

from gf.core.output import GfError
from gf.play import analyze

RATE = 60
GRAVITY_PER_TICK = 700 / RATE


def state(pos=(0.0, 0.0), vel=(0.0, 0.0), on_floor=True, deaths=0, reached=False):
    return {"level": "l", "player": {"pos": list(pos), "vel": list(vel), "on_floor": on_floor},
            "goal": {"pos": [100, 0], "reached": reached}, "deaths": deaths, "fps": 60}


def sample(tick, **fields):
    return {"type": "state", "tick": tick, "t": tick / RATE, "state": {**state(**fields), "tick": tick, "t": tick / RATE}}


def press(tick, action="right", **extra):
    return {"type": "input", "tick": tick, "t": tick / RATE, "down": True, "device": "key", "code": "X",
            "actions": [action] if action else [], **extra}


def release(tick, action="right"):
    return {**press(tick, action), "down": False}


def test_velocity_change_counts_as_response():
    samples = [sample(0), sample(3), sample(6, vel=(90, 0), pos=(4, 0)), sample(9, vel=(90, 0), pos=(8, 0))]
    result = analyze.check_inputs([press(3)], samples, RATE)
    assert (result["pressed"], result["responded"], result["unresponsive"]) == (1, 1, [])


def test_no_change_is_reported_with_time_and_input_name():
    samples = [sample(tick) for tick in range(0, 31, 3)]
    result = analyze.check_inputs([press(6, "jump"), release(8, "jump")], samples, RATE)
    assert result["pressed"] == 1 and result["responded"] == 0
    assert result["unresponsive"][0]["input"] == "jump"
    assert result["unresponsive"][0]["t"] == 0.1


def test_coasting_and_gravity_are_not_a_response():
    """공중에서 눌렀는데 무시된 점프: 위치도 속도도 변하지만 누르기 전과 같은 추세다."""
    samples = [sample(t, pos=(t * 1.5, t), vel=(90, t * GRAVITY_PER_TICK), on_floor=False) for t in range(0, 31, 3)]
    result = analyze.check_inputs([press(9, "jump")], samples, RATE)
    assert [item["input"] for item in result["unresponsive"]] == ["jump"]


def test_jump_during_fall_is_a_response():
    falling = [sample(t, vel=(0, t * GRAVITY_PER_TICK), on_floor=False) for t in (0, 3, 6)]
    jumped = [sample(9, vel=(0, -230 + 3 * GRAVITY_PER_TICK), on_floor=False)]
    assert analyze.check_inputs([press(6, "jump")], falling + jumped, RATE)["responded"] == 1


def test_flag_or_counter_change_counts_as_response():
    samples = [sample(0), sample(3), sample(6, deaths=1)]
    assert analyze.check_inputs([press(3)], samples, RATE)["responded"] == 1
    samples = [sample(0), sample(3), {**sample(6), "state": {**sample(6)["state"], "score": 10}}]
    assert analyze.check_inputs([press(3)], samples, RATE)["responded"] == 1


def test_response_after_threshold_is_too_late():
    samples = [sample(tick) for tick in range(0, 30, 3)] + [sample(30, vel=(90, 0))]
    late = analyze.check_inputs([press(3)], samples, RATE, threshold_s=0.25)
    in_time = analyze.check_inputs([press(3)], samples, RATE, threshold_s=0.5)
    assert late["responded"] == 0 and in_time["responded"] == 1


def test_fps_and_time_alone_are_not_a_response():
    later = sample(6)
    later["state"]["fps"] = 30
    assert analyze.check_inputs([press(3)], [sample(0), sample(3), later], RATE)["responded"] == 0


def test_unmapped_keys_and_unverifiable_inputs_are_counted_separately():
    samples = [sample(0), sample(3), sample(6)]
    result = analyze.check_inputs([press(3, action=None), press(100)], samples, RATE)
    assert (result["pressed"], result["unmapped"], result["unverified"]) == (0, 1, 1)


def test_mouse_button_without_action_is_still_checked():
    samples = [sample(0), sample(3), sample(6)]
    click = {"type": "input", "tick": 3, "down": True, "device": "mouse", "code": 0, "pos": [5, 5], "actions": []}
    result = analyze.check_inputs([click], samples, RATE)
    assert result["unresponsive"][0]["input"] == "mouse:0"


def test_liveness_fails_only_when_nothing_responded():
    analyze.require_liveness({"pressed": 0, "responded": 0})
    analyze.require_liveness({"pressed": 5, "responded": 1})
    with pytest.raises(GfError, match="입력 생존"):
        analyze.require_liveness({"pressed": 5, "responded": 0})


def test_position_drift_compares_matching_ticks():
    recorded = [sample(6, pos=(10, 0)), sample(12, pos=(20, 0)), sample(99, pos=(0, 0))]
    replayed = [sample(6, pos=(10, 0)), sample(9, pos=(15, 0)), sample(12, pos=(23, 4))]
    assert analyze.position_drift(recorded, replayed) == {"compared": 2, "max": 5.0, "final": 5.0}
    assert analyze.position_drift(recorded, []) is None


def test_validate_state_lists_missing_contract_fields():
    analyze.validate_state(sample(0)["state"])
    broken = sample(0)["state"]
    del broken["deaths"], broken["player"]["vel"], broken["goal"]["reached"]
    with pytest.raises(GfError, match=r"deaths.*player\.vel.*goal\.reached"):
        analyze.validate_state(broken)
