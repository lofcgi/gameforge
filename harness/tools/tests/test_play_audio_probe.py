from gf.play import audio_probe

RATE = 60


def bins(seconds: float, level=lambda ms: -20.0, quiet=lambda ms: 0.0, step: int = 100) -> list[dict]:
    return [{"ms": ms, "tick": round(ms * RATE / 1000), "peak_db": level(ms), "rms_db": level(ms) - 10, "quiet_ms": quiet(ms)}
            for ms in range(0, round(seconds * 1000), step)]


def start(ms: int, sound: str, length: float, loop: bool = False, **extra) -> dict:
    tick = round(ms * RATE / 1000)
    return {"kind": "start", "ms": ms, "tick": tick, "t": tick / RATE, "sound": sound, "length_s": length, "loop": loop, **extra}


def mark(t: float, name: str, kind: str = "input") -> dict:
    return {"tick": round(t * RATE), "kind": kind, "name": name}


def test_silent_run_fails_audible():
    report = {"timeline": bins(2.0, level=lambda ms: -200.0), "events": []}
    result = audio_probe.analyze(report, [], "godot", RATE, [])
    assert result["checks"]["audible"] != "ok" and result["peak_db"] == -200.0


def test_sounds_are_matched_to_inputs_and_state_events():
    events = [start(1010, "res://assets/game/audio/jump.mp3", 0.4), start(3020, "/assets/game/audio/goal.mp3", 1.2)]
    report = {"timeline": bins(5.0, level=lambda ms: -8.0 if 1000 <= ms < 1400 else -20.0), "events": events}
    marks = [mark(1.0, "jump"), mark(2.0, "jump"), {**mark(3.1, "goal", "state"), "since_tick": 180}]
    result = audio_probe.analyze(report, marks, "godot", RATE, [], [("jump", "jump.mp3"), ("goal", "goal")])
    rows = result["responses"]
    assert rows[0]["sounds"] == ["assets/game/audio/jump.mp3"] and rows[1]["sounds"] == []
    assert rows[0]["peak_db_after"] == -8.0 and rows[0]["peak_db_before"] == -20.0
    assert rows[2]["sounds"] == ["assets/game/audio/goal.mp3"]
    assert result["sounds"]["assets/game/audio/jump.mp3"]["starts"] == 1
    assert result["checks"]["expected_sounds"] == "ok"
    missing = audio_probe.analyze(report, marks, "godot", RATE, [], [("jump", "land")])
    assert "기대한 소리" in missing["checks"]["expected_sounds"]


def test_web_must_be_silent_before_the_first_input():
    quiet_then_loud = bins(3.0, level=lambda ms: -200.0 if ms < 1000 else -18.0)
    context = {"state": "running", "sample_rate": 48000, "created": {"ms": 1005, "tick": 61, "after_gesture": True}}
    report = {"timeline": quiet_then_loud, "events": [start(1010, "/a/theme.wav", 8.0, True)], "contexts": [context]}
    ok = audio_probe.analyze(report, [mark(1.0, "right")], "web", RATE, [])
    assert ok["checks"]["silent_before_input"] == "ok" and ok["checks"]["no_autoplay_warnings"] == "ok"
    early = {**report, "contexts": [{**context, "created": {"ms": 10, "tick": 0, "after_gesture": False}}]}
    logs = [{"level": "warning", "text": "The AudioContext was not allowed to start."}]
    bad = audio_probe.analyze(early, [mark(1.0, "right")], "web", RATE, logs)
    assert bad["checks"]["silent_before_input"] != "ok" and bad["checks"]["no_autoplay_warnings"] != "ok"


def test_loop_is_checked_past_its_length():
    loop = start(200, "res://theme.wav", 4.0, True)
    wrapped = {"kind": "loop", "ms": 4200, "tick": 252, "t": 4.2, "sound": "res://theme.wav", "length_s": 4.0, "loop": True}
    playing = {"timeline": bins(6.0, quiet=lambda ms: 9.5 if ms == 4200 else 0.0), "events": [loop, wrapped]}
    row = audio_probe.analyze(playing, [], "godot", RATE, [])["loops"][0]
    assert row["continues"] is True and row["wraps"] == 1 and row["quiet_ms_at_wrap"] == 9.5

    stopped = {"timeline": bins(6.0, level=lambda ms: -20.0 if ms < 4200 else -200.0), "events": [loop]}
    result = audio_probe.analyze(stopped, [], "godot", RATE, [])
    assert result["loops"][0]["continues"] is False and "끊겼다" in result["checks"]["loop_continues"]

    short = {"timeline": bins(3.0), "events": [loop]}
    result = audio_probe.analyze(short, [], "godot", RATE, [])
    assert result["loops"][0]["continues"] is None and "재지 못했다" in result["checks"]["loop_continues"]


def test_gaps_while_a_loop_plays_are_listed():
    report = {"timeline": bins(3.0, quiet=lambda ms: 35.0 if ms == 2000 else 0.0), "events": [start(0, "/theme.wav", 8.0, True)]}
    assert audio_probe.analyze(report, [], "web", RATE, [])["gaps"] == [{"ms": 2000, "t": 2.0, "quiet_ms": 35.0}]


def test_merge_needed_time_and_state_marks():
    first = {"mix_rate": 48000, "timeline": bins(1.0), "events": [start(100, "/theme.wav", 8.0, True)]}
    second = {"mix_rate": 48000, "timeline": bins(0.5), "events": []}
    merged = audio_probe.merge([first, second])
    assert len(merged["timeline"]) == 15 and len(merged["events"]) == 1 and merged["mix_rate"] == 48000
    assert audio_probe.needed_ms(merged["events"]) == 100 + 8000 + audio_probe.LOOP_MARGIN_S * 1000
    assert audio_probe.needed_ms([start(0, "/jump.mp3", 0.4)]) == 0.0

    before = {"tick": 60, "goal": {"reached": False}, "deaths": 0}
    after = {"tick": 66, "goal": {"reached": True}, "deaths": 1}
    assert [m["name"] for m in audio_probe.state_marks(before, after)] == ["goal", "death"]
    assert audio_probe.state_marks(after, after) == []
    assert audio_probe.sound_name(None) == "(이름 없는 버퍼)"
