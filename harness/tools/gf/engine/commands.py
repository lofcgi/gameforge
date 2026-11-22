"""`gf engine ...` 명령. 엔진별 차이는 어댑터가, 입력·기록 로직은 gf.play 가 맡는다."""

import json
import time
from datetime import datetime
from pathlib import Path

from gf.core.output import GfError, fail, ok
from gf.core.paths import gf_dir, project_dir, rel
from gf.engine import app_focus, image, os_input, perf
from gf.engine.adapter import DEFAULT_SIZE, Options, count_levels, open_session, parse_size
from gf.play import analyze, audio_probe, policies, script, session
from gf.play.runner import Run, first_divergence, play_live

SETTLE_TICKS = 30
PERF_WARMUP_S = 1.0
AUDIO_POLL_S = 0.1
OS_INPUT_LEAD_S = 0.08
AUDIO_TAIL_S = 1.0


def _project(args) -> Path:
    project = project_dir(args)
    gf_dir(project)
    return project


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _size(args) -> tuple[int, int]:
    return parse_size(args.size) if args.size else DEFAULT_SIZE


def _scale(args) -> float:
    if args.scale <= 0:
        raise GfError("--scale 은 0보다 커야 한다 (예: 2).")
    return args.scale


def _out_dir(project: Path, out: str) -> Path:
    directory = (project / out).resolve()
    if not directory.is_relative_to(project):
        raise GfError(f"결과는 게임 프로젝트 안에만 쓴다: {out}")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _load_script(project: Path, path: str | None) -> dict:
    return script.load((project / path).resolve()) if path else {"seed": None, "events": []}


def _seed(args, loaded: dict) -> int:
    if args.seed is not None:
        return args.seed
    return loaded["seed"] or 0


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return path


def _write_trace(path: Path, header: dict, run: Run) -> Path:
    entries = sorted(run.inputs + run.samples, key=lambda entry: entry["tick"])
    path.write_text("".join(session.dump_line(entry) for entry in [header, *entries]))
    return path


def _shot_rows(project: Path, run: Run) -> list[dict]:
    return [{"t": shot["t"], "tick": shot["tick"], "file": rel(project, shot["path"]), "state": shot["state"]}
            for shot in run.shots]


def _periodic_shots(directory: Path, end_tick: int, every_ticks: int) -> dict[int, Path]:
    ticks = range(every_ticks, end_tick, every_ticks)
    return {tick: directory / f"shot_{index:03d}.png" for index, tick in enumerate(ticks, start=1)}


def _input_check(run: Run, threshold: float = analyze.DEFAULT_THRESHOLD_S) -> dict:
    return analyze.check_inputs(run.inputs, run.samples, run.tick_rate, threshold)


def _liveness(project: Path, options: Options, run: Run, check: dict) -> dict:
    """합성 입력이 게임에 닿지 않았는데 성공으로 보고하는 일을 막는다.

    상태 변화 휴리스틱(check)에 더해, 같은 시드로 입력 없이 한 번 더 돌려 비교한다(반사실).
    입력이 닿았다면 첫 입력 뒤 어딘가에서 두 실행의 상태가 갈라져야 한다.
    """
    presses = [entry for entry in run.inputs if entry["down"]]
    if not presses:
        return {"verified": False, "reason": "보낸 입력이 없다"}
    analyze.require_liveness(check)
    first = presses[0]["tick"]
    with open_session(project, options) as baseline:
        diverged = first_divergence(baseline, run.samples)
    if diverged is None:
        raise GfError(
            f"입력 생존 확인 실패: 입력 {len(presses)}개를 보냈지만 입력 없이 돌린 실행과 상태가 끝까지 같다. "
            "입력이 게임의 처리기에 닿지 않는다."
        )
    if diverged <= first:
        return {"verified": False, "reason": "첫 입력 전부터 실행마다 상태가 달라(비결정적) 반사실 비교를 할 수 없다",
                "diverged_t": round(diverged / run.tick_rate, 3)}
    return {"verified": True, "first_input_t": round(first / run.tick_rate, 3),
            "diverged_t": round(diverged / run.tick_rate, 3)}


def run_game(args) -> int:
    project = _project(args)
    record = _session_path(project, args.id) if args.record else None
    loaded = _load_script(project, args.script)
    if loaded["events"] and args.seconds is None:
        raise GfError("--script 를 쓸 때는 --seconds 가 필요하다.")
    if args.os_input and not loaded["events"]:
        raise GfError("--os-input 은 --script 와 함께 쓴다.")
    if args.os_input:
        os_input.require_permission()
    options = Options(lockstep=False, size=_size(args), seed=_seed(args, loaded), record=record,
                      human=args.os_input or not loaded["events"], screen=args.screen)
    sent = None
    with open_session(project, options) as game:
        script.require_known_actions(loaded["events"], game.header["info"])
        if args.os_input:
            sent = _play_os_input(game, loaded["events"], args.seconds)
        elif loaded["events"]:
            play_live(game, loaded["events"], args.seconds)
        else:
            game.wait(args.seconds)
    logs = game.logs()
    fields = {"files": [], "logs": logs, **count_levels(logs)}
    if sent is not None:
        fields["os_input"] = sent
    if record:
        recorded = session.load(record)
        fields.update(files=[rel(project, record)], session=record.stem,
                      inputs=len(recorded.inputs), samples=len(recorded.samples))
    return ok(**fields)


def _play_os_input(game, events: list[dict], seconds: float) -> dict:
    """액션 스크립트를 브리지가 아니라 OS 키 이벤트로 넣는다. 게임이 맨 앞 앱이 아닌 순간의 키는 보내지 않고 센다."""
    info = game.header["info"]
    pid = game.os_pid()
    game.take_focus()
    sent = skipped = 0
    start = time.monotonic()
    for event in events:
        if event["t"] > seconds:
            break
        # 맨 앞 앱 확인(수십 ms)이 누르는 시각을 밀지 않게 조금 일찍 해 둔다.
        if not game.wait(max(0.0, event["t"] - OS_INPUT_LEAD_S - (time.monotonic() - start))):
            break
        frontmost = app_focus.frontmost_pid() == pid
        game.wait(max(0.0, event["t"] - (time.monotonic() - start)))
        if not frontmost:
            skipped += 1
            continue
        os_input.post_key(pid, os_input.key_for(event, info), event["down"])
        sent += 1
    game.wait(max(0.0, seconds - (time.monotonic() - start)))
    return {"sent": sent, "skipped_not_frontmost": skipped, "pid": pid,
            "level": "CGEventPostToPid: 게임 프로세스의 이벤트 큐에 넣은 Quartz 키 이벤트"}


def _session_path(project: Path, session_id: str | None) -> Path:
    directory = _out_dir(project, "captures/sessions")
    return directory / f"{session_id or _stamp()}.jsonl"


def record(args) -> int:
    args.record = True
    return run_game(args)


def capture(args) -> int:
    project = _project(args)
    out = _out_dir(project, args.out)
    loaded = _load_script(project, args.script)
    options = Options(size=_size(args), seed=_seed(args, loaded), scale=_scale(args), screen=args.screen)
    with open_session(project, options) as game:
        rate = game.header["tick_rate"]
        script.require_known_actions(loaded["events"], game.header["info"])
        events = script.to_ticks(loaded["events"], rate)
        times = _capture_times(args.at, events, rate)
        shots = {round(t * rate): out / f"shot_{index:02d}_t{t:.2f}.png" for index, t in enumerate(times, start=1)}
        run = Run(game, shots)
        run.play(events, max(shots))
    logs = game.logs()
    check = _input_check(run)
    image.require_rendered([shot["path"] for shot in run.shots])
    liveness = _liveness(project, options, run, check)
    report = _write_json(out / "capture.json", {
        "header": game.header, "shots": _shot_rows(project, run), "inputs": check, "liveness": liveness,
        "logs": logs,
    })
    files = [rel(project, shot["path"]) for shot in run.shots] + [rel(project, report)]
    return ok(files=files, shots=len(run.shots), inputs=_brief(check), liveness=liveness, **count_levels(logs))


def _capture_times(at: str | None, events: list[dict], rate: int) -> list[float]:
    if at:
        try:
            times = sorted({float(part) for part in at.split(",")})
        except ValueError as exc:
            raise GfError(f"--at 은 쉼표로 구분한 초 목록이다 (예: 0.5,2,4): {at}") from exc
        if times[0] < 0:
            raise GfError("--at 의 시각은 0 이상이어야 한다.")
        return times
    last = max((event["tick"] for event in events), default=0) / rate
    return [last + 1.0]


def _brief(check: dict) -> dict:
    return {**{key: check[key] for key in ("pressed", "responded", "unmapped", "unverified")},
            "unresponsive": [{k: item[k] for k in ("t", "input")} for item in check["unresponsive"]]}


def bot(args) -> int:
    project = _project(args)
    out = _out_dir(project, args.out or f"captures/bot/{Path(args.policy).stem}-{_stamp()}")
    scripted = _load_script(project, args.policy) if args.policy.endswith(".json") else None
    seed = _seed(args, scripted or {"seed": None})
    options = Options(size=_size(args), seed=seed, scale=_scale(args), screen=args.screen)
    with open_session(project, options) as game:
        rate = game.header["tick_rate"]
        end = round(args.seconds * rate)
        shots = _periodic_shots(out, end, round(args.shot_every * rate))
        run = Run(game, shots, stop=lambda state: state["goal"]["reached"])
        analyze.validate_state(run.state)
        if scripted:
            script.require_known_actions(scripted["events"], game.header["info"])
            run.play(script.to_ticks(scripted["events"], rate), end)
        else:
            run.play_policy(policies.load(args.policy, project, game.header["info"], seed), end)
        run.shot(out / "final.png")
    logs = game.logs()
    check = _input_check(run)
    image.require_rendered([shot["path"] for shot in run.shots])
    result = {
        "policy": args.policy, "seed": seed,
        "reached_goal": run.state["goal"]["reached"], "time_s": run.state["t"], "deaths": run.state["deaths"],
        "liveness": _liveness(project, options, run, check), "inputs": check,
        "final_state": run.state, "shots": _shot_rows(project, run), "logs": logs,
    }
    files = [rel(project, shot["path"]) for shot in run.shots]
    files.append(rel(project, _write_trace(out / "trace.jsonl", game.header, run)))
    files.append(rel(project, _write_json(out / "result.json", result)))
    summary = {key: result[key] for key in ("reached_goal", "time_s", "deaths", "liveness")}
    summary.update(inputs=_brief(check), **count_levels(logs))
    if args.require_goal and not result["reached_goal"]:
        return fail(f"봇이 {args.seconds}초 안에 목표에 닿지 못했다.", files=files, **summary)
    return ok(files=files, **summary)


def replay(args) -> int:
    project = _project(args)
    source = _find_session(project, args.session)
    recorded = session.load(source)
    out = _out_dir(project, args.out or f"captures/replays/{source.stem}")
    size = tuple(recorded.header.get("size") or DEFAULT_SIZE)
    end = recorded.last_tick + SETTLE_TICKS
    options = Options(size=size, seed=recorded.header["seed"], screen=args.screen)
    with open_session(project, options) as game:
        rate = game.header["tick_rate"]
        if rate != recorded.header["tick_rate"]:
            raise GfError(f"기록의 틱 속도({recorded.header['tick_rate']})와 게임의 틱 속도({rate})가 다르다.")
        run = Run(game, _periodic_shots(out, end, round(args.shot_every * rate)))
        run.play(recorded.inputs, end)
        run.shot(out / "final.png")
    logs = game.logs()
    check = _input_check(run, args.threshold)
    image.require_rendered([shot["path"] for shot in run.shots])
    liveness = _liveness(project, options, run, check)
    drift = analyze.position_drift(recorded.samples, run.samples)
    files = [rel(project, shot["path"]) for shot in run.shots]
    files.append(rel(project, _write_trace(out / "trace.jsonl", game.header, run)))
    files.append(rel(project, _write_json(out / "replay.json", {
        "session": rel(project, source), "inputs": check, "liveness": liveness, "drift": drift,
        "final_state": run.state, "shots": _shot_rows(project, run), "logs": logs,
    })))
    return ok(files=files, session=source.stem, inputs=_brief(check), liveness=liveness, drift=drift,
              final_state=run.state, **count_levels(logs))


def _find_session(project: Path, name: str) -> Path:
    candidates = [project / name, project / "captures/sessions" / name,
                  project / "captures/sessions" / f"{name}.jsonl"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise GfError(f"기록을 찾지 못했다: {name} (captures/sessions/ 의 id 나 파일 경로를 준다)")


def perf_command(args) -> int:
    project = _project(args)
    loaded = _load_script(project, args.script)
    options = Options(lockstep=False, size=_size(args), seed=_seed(args, loaded), uncapped=args.uncapped,
                      scale=_scale(args), screen=args.screen)
    with open_session(project, options) as game:
        script.require_known_actions(loaded["events"], game.header["info"])
        game.wait(PERF_WARMUP_S)
        game.perf_start()
        if not play_live(game, loaded["events"], args.seconds):
            raise GfError("측정 중에 게임이 종료했다.")
        measured = game.perf_stop()
    logs = game.logs()
    result = {
        "seconds": args.seconds, "uncapped": args.uncapped, "load_s": round(game.load_s, 3),
        **perf.frame_stats(measured["frame_ms"]),
        "counters": {key: round(value, 3) for key, value in measured["counters"].items()}, **count_levels(logs),
    }
    files = []
    if args.out:
        report = _out_dir(project, str(Path(args.out).parent)) / Path(args.out).name
        files.append(rel(project, _write_json(report, {**result, "logs": logs})))
    return ok(files=files, **result)


def audio(args) -> int:
    """실시간으로 돌리며 브리지가 잰 소리를 판정한다. 통과든 실패든 결과를 captures/audio/result.json 에 남긴다."""
    project = _project(args)
    out = _out_dir(project, args.out)
    default_script = "bot/clear.json" if (project / "bot/clear.json").is_file() else None
    loaded = _load_script(project, args.script or default_script)
    expect = [_parse_expect(value) for value in args.expect]
    options = Options(lockstep=False, size=_size(args), seed=_seed(args, loaded), audio=True, screen=args.screen)
    with open_session(project, options) as game:
        script.require_known_actions(loaded["events"], game.header["info"])
        report, marks = _measure_audio(game, loaded["events"], args.seconds, args.max_seconds)
    logs = game.logs()
    result = audio_probe.analyze(report, marks, game.header["engine"], game.header["tick_rate"], logs, expect)
    errors = [entry["text"] for entry in logs if entry["level"] == "error"]
    result["checks"]["no_errors"] = "ok" if not errors else f"오류 {len(errors)}건: {errors[0]}"
    failed = [name for name, verdict in result["checks"].items() if verdict != "ok"]
    error = "소리 측정 실패: " + " / ".join(result["checks"][name] for name in failed) if failed else None
    files = [rel(project, _write_json(out / "result.json", {
        "ok": not failed, "at": datetime.now().astimezone().isoformat(timespec="seconds"), "error": error,
        **result, "marks": marks, "timeline": report["timeline"], "events": report["events"], "logs": logs,
    }))]
    if error:
        return fail(error, files=files, **result, **count_levels(logs))
    return ok(files=files, **result, **count_levels(logs))


def _parse_expect(value: str) -> tuple[str, str]:
    name, _, sound = value.partition("=")
    if not name or not sound:
        raise GfError(f"--expect 는 <액션이나 사건>=<소리 파일 이름의 일부> 형식이다 (예: jump=jump.mp3): {value}")
    return name, sound


def _measure_audio(game, events: list[dict], seconds: float | None, max_seconds: float) -> tuple[dict, list[dict]]:
    """액션 스크립트를 실시간으로 넣으면서 소리 측정과 상태 변화를 모은다.

    seconds 가 없으면 스크립트가 끝나고, 시작된 반복 소리가 한 바퀴를 넘길 때까지(최대 max_seconds) 잰다.
    """
    pending = list(events)
    reports, marks = [], []
    state = game.state()
    script_end = (pending[-1]["t"] if pending else 0.0) + AUDIO_TAIL_S
    start = time.monotonic()
    while True:
        elapsed = time.monotonic() - start
        while pending and pending[0]["t"] <= elapsed:
            event = pending.pop(0)
            if event["down"]:
                name = event.get("action") or f"{event['device']}:{event['code']}"
                marks.append({"tick": game.state()["tick"], "kind": "input", "name": name})
            game.send_input(event)
        if not game.wait(AUDIO_POLL_S):
            raise GfError("측정 중에 게임이 종료했다.")
        after = game.state()
        marks += audio_probe.state_marks(state, after)
        state = after
        reports.append(game.audio_probe())
        measured = audio_probe.merge(reports)
        if seconds is not None:
            done = elapsed >= seconds
        else:
            covered = measured["timeline"] and measured["timeline"][-1]["ms"] >= audio_probe.needed_ms(measured["events"])
            done = (elapsed >= script_end and covered) or elapsed >= max_seconds
        if done:
            return measured, marks


def test(args) -> int:
    """스모크 테스트. 통과든 실패든 결과를 captures/test/result.json 에 남긴다 (check evidence 가 읽는다)."""
    project = _project(args)
    out = _out_dir(project, "captures/test")
    try:
        fields = _smoke(project, out, args)
    except GfError as exc:
        _write_test_result(out, False, str(exc), {})
        raise
    failed = [name for name, verdict in fields["checks"].items() if verdict != "ok"]
    error = f"스모크 테스트 실패: {', '.join(failed)}" if failed else None
    fields["files"].append(rel(project, _write_test_result(out, not failed, error, fields)))
    if error:
        return fail(error, **fields)
    return ok(**fields)


def _write_test_result(out: Path, passed: bool, error: str | None, fields: dict) -> Path:
    return _write_json(out / "result.json", {
        "ok": passed, "at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "checks": fields.get("checks"), "error": error, "load_s": fields.get("load_s"),
    })


def _smoke(project: Path, out: Path, args) -> dict:
    checks: dict[str, str] = {}
    with open_session(project, Options(size=_size(args), scale=_scale(args), screen=args.screen)) as game:
        checks["boot"] = "ok"
        run = Run(game)
        checks["contract"] = _verdict(lambda: _check_contract(game.header, run.state))
        run.advance_to(SETTLE_TICKS)
        run.shot(out / "first_frame.png")
        checks["first_frame"] = _verdict(lambda: image.require_rendered([out / "first_frame.png"]))
        probe = _probe_inputs(run, args.threshold) if checks["contract"] == "ok" else None
    logs = game.logs()
    if probe is not None:
        checks["input_liveness"] = "ok" if not probe["unresponsive"] else (
            "반응 없는 입력: " + ", ".join(item["input"] for item in probe["unresponsive"]))
    errors = [entry["text"] for entry in logs if entry["level"] == "error"]
    checks["no_errors"] = "ok" if not errors else f"오류 {len(errors)}건: {errors[0]}"
    return {"files": [rel(project, out / "first_frame.png")], "checks": checks,
            "load_s": round(game.load_s, 3), "logs": logs}


def _verdict(check) -> str:
    try:
        check()
    except GfError as exc:
        return str(exc)
    return "ok"


def _check_contract(header: dict, state: dict) -> None:
    analyze.validate_state(state)
    info = header["info"]
    if not info.get("actions") or not info.get("probe"):
        raise GfError("브리지 info 에 actions 와 probe 가 있어야 한다.")
    script.require_known_actions([{"action": name} for name in info["probe"]], info)


def _probe_inputs(run: Run, threshold: float) -> dict:
    """info.probe 의 액션을 하나씩 눌러 보고 상태가 반응하는지 본다."""
    window = round(threshold * run.tick_rate)
    for action in run.session.header["info"]["probe"]:
        run.send({"down": True, "action": action})
        run.advance_to(run.tick + window)
        run.send({"down": False, "action": action})
        run.advance_to(run.tick + SETTLE_TICKS)
    return _input_check(run, threshold)


def register(sub) -> None:
    group = sub.add_parser("engine", help="게임 실행, 스크린샷, 플레이 봇, 입력 기록·재생, 성능 측정")
    commands = group.add_subparsers(dest="cmd", required=True)

    def add(name: str, func, text: str):
        parser = commands.add_parser(name, help=text)
        parser.add_argument("--size", help="창/뷰포트 크기 WxH (기본 1280x720)")
        parser.add_argument("--scale", type=float, default=1.0,
                            help="web 의 화면 배율 devicePixelRatio (기본 1, 레티나는 2). 스크린샷은 --size 의 배율 배가 된다. "
                                 "Godot 은 --size 가 이미 물리 픽셀이라 쓰지 않는다")
        parser.add_argument("--screen", type=int, help="Godot 창을 띄울 화면 번호 (큰 창이 화면에 안 들어갈 때)")
        parser.set_defaults(func=func)
        return parser

    def add_live_options(parser) -> None:
        parser.add_argument("--seconds", type=float, help="이 시간 뒤 자동 종료 (없으면 창을 닫을 때까지)")
        parser.add_argument("--id", help="기록 id (기본: 현재 시각). captures/sessions/<id>.jsonl")
        parser.add_argument("--script", help="사람 대신 실시간으로 입력할 액션 스크립트 (기록 경로 점검용)")
        parser.add_argument("--os-input", action="store_true",
                            help="--script 의 키를 브리지가 아니라 macOS 키 이벤트로 게임 창에 보낸다 (사람의 키와 같은 경로. "
                                 "손쉬운 사용 권한 필요)")
        parser.add_argument("--seed", type=int)

    p = add("run", run_game, "사람이 플레이하도록 게임을 띄운다")
    p.add_argument("--record", action="store_true", help="입력과 상태를 captures/sessions/ 에 기록한다")
    add_live_options(p)

    p = add("record", record, "게임을 띄우고 사람의 입력을 기록한다 (run --record 와 같다)")
    add_live_options(p)

    p = add("capture", capture, "게임을 자동 실행해 실제 렌더링된 스크린샷과 상태를 저장한다")
    p.add_argument("--out", required=True, help="결과 디렉터리 (예: captures/title)")
    p.add_argument("--at", help="스크린샷을 찍을 게임 시각(초) 목록. 예: 0.5,2,4")
    p.add_argument("--script", help="실행 중 입력할 액션 스크립트(JSON)")
    p.add_argument("--seed", type=int)

    p = add("bot", bot, "플레이 봇이 실제 입력 경로로 게임을 플레이하고 결과를 보고한다")
    p.add_argument("--policy", required=True,
                   help=f"내장 정책({', '.join(policies.BUILTIN)}) 또는 파일(.json 액션 스크립트, .py)")
    p.add_argument("--seconds", type=float, default=30.0, help="게임 시간 제한 (기본 30)")
    p.add_argument("--shot-every", type=float, default=2.0, help="스크린샷 간격(초)")
    p.add_argument("--require-goal", action="store_true", help="목표에 닿지 못하면 실패로 끝낸다")
    p.add_argument("--out", help="결과 디렉터리 (기본 captures/bot/<정책>-<시각>)")
    p.add_argument("--seed", type=int)

    p = add("replay", replay, "기록한 입력을 결정적으로 재생하고 반응 없는 입력 후보를 보고한다")
    p.add_argument("session", help="기록 id 또는 jsonl 경로")
    p.add_argument("--threshold", type=float, default=analyze.DEFAULT_THRESHOLD_S,
                   help="이 시간(초) 안에 상태가 반응하지 않으면 후보로 보고한다")
    p.add_argument("--shot-every", type=float, default=1.0, help="스크린샷 간격(초)")
    p.add_argument("--out", help="결과 디렉터리 (기본 captures/replays/<id>)")

    p = add("perf", perf_command, "프레임 시간, 드로우 콜, 메모리, 로딩 시간을 잰다")
    p.add_argument("--seconds", type=float, default=5.0)
    p.add_argument("--uncapped", action="store_true", help="수직 동기화를 끄고 최대 프레임을 잰다")
    p.add_argument("--script", help="측정 중 실시간으로 입력할 액션 스크립트")
    p.add_argument("--seed", type=int)
    p.add_argument("--out", help="결과 JSON 을 저장할 경로 (예: captures/perf/base.json)")

    p = add("audio", audio, "실시간으로 돌리며 소리가 실제로 나는지 잰다 (마스터 신호의 피크·RMS, 재생된 소리, 반복). "
                             "결과를 captures/audio/result.json 에 남긴다")
    p.add_argument("--script", help="측정 중 실시간으로 입력할 액션 스크립트 (기본: bot/clear.json 이 있으면 그것)")
    p.add_argument("--seconds", type=float, help="잴 시간. 없으면 스크립트가 끝나고 반복 소리가 한 바퀴를 넘길 때까지")
    p.add_argument("--max-seconds", type=float, default=60.0, help="--seconds 가 없을 때의 상한 (기본 60)")
    p.add_argument("--expect", action="append", default=[], metavar="이름=소리",
                   help="그 액션이나 사건(goal, death) 직후에 이름에 이 글자가 든 소리가 시작돼야 한다. 여러 번 줄 수 있다")
    p.add_argument("--out", default="captures/audio", help="결과 디렉터리 (기본 captures/audio)")
    p.add_argument("--seed", type=int)

    p = add("test", test, "스모크 테스트: 부팅, 첫 화면, 콘솔 오류, 입력 생존. 결과를 captures/test/result.json 에 남긴다")
    p.add_argument("--threshold", type=float, default=analyze.DEFAULT_THRESHOLD_S)
