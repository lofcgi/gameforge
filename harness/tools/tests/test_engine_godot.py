from gf.engine import godot
from gf.engine.adapter import Options

OUTPUT = """Godot Engine v4.7.2.stable.official - https://godotengine.org
Metal 4.0 - Forward+ - Using Device #0: Apple - Apple M4 Pro (Apple9)

\x1b[1;31mSCRIPT ERROR:\x1b[0m Invalid access to property or key 'missing' on a base object of type 'Dictionary'.
          at: _process (res://scripts/main.gd:75)
WARNING: Node './Foo' was modified from inside an instance.
   at: instantiate (scene/resources/packed_scene.cpp:310)
ERROR: Failed to load script "res://scripts/main.gd" with error "Parse error".
some ordinary print
USER WARNING: careful
"""


def test_parse_log_finds_errors_even_though_godot_exits_zero():
    entries = godot.parse_log(OUTPUT)
    assert [entry["level"] for entry in entries] == ["error", "warning", "error", "warning"]
    assert entries[0]["text"].startswith("SCRIPT ERROR: Invalid access")
    assert "at: _process (res://scripts/main.gd:75)" in entries[0]["text"]
    assert "packed_scene.cpp" in entries[1]["text"]


def test_parse_log_ignores_ordinary_output():
    assert godot.parse_log("hello\nGodot Engine v4\n   at: nowhere\n") == []


def test_tick_rate_reads_project_setting(tmp_path):
    (tmp_path / "project.godot").write_text("[physics]\n\ncommon/physics_ticks_per_second=120\n")
    assert godot.tick_rate(tmp_path) == 120
    (tmp_path / "project.godot").write_text("[application]\n")
    assert godot.tick_rate(tmp_path) == 60


def test_lockstep_command_decouples_from_wall_clock(tmp_path, monkeypatch):
    (tmp_path / "project.godot").write_text("")
    monkeypatch.setattr(godot, "godot_binary", lambda: "godot")
    session = object.__new__(godot.GodotSession)
    command = session._command(tmp_path, Options(lockstep=True, size=(640, 360), seed=7), 5000)
    engine_args, user_args = command[: command.index("--")], command[command.index("--") + 1:]
    assert "--headless" not in command
    assert ["--fixed-fps", "60"] == engine_args[engine_args.index("--fixed-fps"):][:2]
    assert ["--resolution", "640x360"] == engine_args[engine_args.index("--resolution"):][:2]
    assert user_args == ["--gf-port=5000", "--gf-seed=7", "--gf-lockstep", "--gf-auto"]
    assert ["--position", godot.WINDOW_POSITION] == engine_args[engine_args.index("--position"):][:2]


def test_human_window_keeps_focus_and_options_reach_godot(tmp_path, monkeypatch):
    (tmp_path / "project.godot").write_text("")
    monkeypatch.setattr(godot, "godot_binary", lambda: "godot")
    session = object.__new__(godot.GodotSession)
    human = session._command(tmp_path, Options(lockstep=False, human=True), 5000)
    assert "--gf-auto" not in human
    probe = session._command(tmp_path, Options(lockstep=False, audio=True, screen=1), 5000)
    assert "--gf-audio" in probe and "--gf-auto" in probe
    assert ["--screen", "1"] == probe[probe.index("--screen"):][:2] and "--position" not in probe


def test_live_record_command(tmp_path, monkeypatch):
    (tmp_path / "project.godot").write_text("")
    monkeypatch.setattr(godot, "godot_binary", lambda: "godot")
    session = object.__new__(godot.GodotSession)
    record = tmp_path / "s.jsonl"
    command = session._command(tmp_path, Options(lockstep=False, record=record), 5000)
    assert "--fixed-fps" not in command and "--gf-lockstep" not in command
    assert f"--gf-record={record}" in command


def test_exit_teardown_leak_lines_are_warnings_not_errors():
    text = (
        "WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).\n"
        "   at: cleanup (core/object/object.cpp:2536)\n"
        "ERROR: 1 resources still in use at exit (run with --verbose for details).\n"
        "   at: clear (core/io/resource.cpp:822)\n"
        "ERROR: something real\n"
    )
    assert [entry["level"] for entry in godot.parse_log(text)] == ["warning", "warning", "error"]
