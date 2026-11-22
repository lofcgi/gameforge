"""실행 중인 게임에서 잰 소리(브리지의 소리 측정)를 판정한다.

브리지는 스피커가 아니라 엔진 안의 최종 신호(Godot: 마스터 버스, web: destination 직전)를 잰다. 그래서 여기서
말할 수 있는 것은 "게임이 소리를 내보냈다"까지다. 듣기에 좋은지는 사람이 판정한다.

입력 형식 (두 엔진 공통):
  timeline: [{"ms", "tick", "peak_db", "rms_db", "quiet_ms"}]   ms 는 측정 시작부터의 벽시계
  events:   [{"kind": "start" | "loop" | "element", "ms", "tick", "sound", "length_s", "loop"}]
  marks:    [{"tick", "kind": "input" | "state", "name"}]        하네스가 넣은 입력과 상태 변화(goal, death)
"""

import math

SILENT_DB = -60.0
FLOOR_DB = -200.0
RESPONSE_S = 0.25
"""입력·사건 뒤 이 시간 안에 시작된 소리를 그 입력의 소리로 본다."""
LOOP_MARGIN_S = 1.5
"""반복 지점을 지나 이만큼 더 재야 '계속 재생된다'고 말한다."""
GAP_MS = 20.0
"""반복 재생 중에 디지털 무음이 이보다 길게 이어지면 끊김으로 보고한다."""
WRAP_WINDOW_MS = 250.0
AUTOPLAY_WORDS = ("AudioContext", "autoplay", "user gesture", "NotAllowedError", "play() failed")


def sound_name(raw: str | None) -> str:
    if not raw:
        return "(이름 없는 버퍼)"
    return raw.removeprefix("res://").lstrip("/")


def merge(reports: list[dict]) -> dict:
    """여러 번 나눠 꺼낸 측정을 하나로 잇는다. 그 밖의 항목은 마지막 것을 쓴다."""
    merged = dict(reports[-1]) if reports else {}
    merged["timeline"] = [entry for report in reports for entry in report["timeline"]]
    merged["events"] = [entry for report in reports for entry in report["events"]]
    return merged


def needed_ms(events: list[dict]) -> float:
    """지금까지 시작된 반복 소리가 한 바퀴 돌고 LOOP_MARGIN_S 가 더 지나는 시각."""
    ends = [event["ms"] + (event["length_s"] + LOOP_MARGIN_S) * 1000
            for event in events if event["kind"] == "start" and event.get("loop") and event.get("length_s")]
    return max(ends, default=0.0)


def _energy(db: float) -> float:
    return 0.0 if db <= FLOOR_DB else 10 ** (db / 10)


def _db(energy: float) -> float:
    return round(10 * math.log10(energy), 1) if energy > 0 else FLOOR_DB


def _peak(entries: list[dict]) -> float:
    return round(max((entry["peak_db"] for entry in entries), default=FLOOR_DB), 1)


def _rms(entries: list[dict]) -> float:
    return _db(sum(_energy(entry["rms_db"]) for entry in entries) / len(entries)) if entries else FLOOR_DB


def state_marks(before: dict, after: dict) -> list[dict]:
    """상태 두 개 사이에 일어난 사건: 목표 도달과 사망."""
    marks = []
    if after["goal"]["reached"] and not before["goal"]["reached"]:
        marks.append({"tick": after["tick"], "since_tick": before["tick"], "kind": "state", "name": "goal"})
    if after["deaths"] > before["deaths"]:
        marks.append({"tick": after["tick"], "since_tick": before["tick"], "kind": "state", "name": "death"})
    return marks


def _responses(marks: list[dict], starts: list[dict], timeline: list[dict], tick_rate: int) -> list[dict]:
    window = round(RESPONSE_S * tick_rate)
    rows = []
    for mark in marks:
        first = mark.get("since_tick", mark["tick"])
        last = mark["tick"] + window
        before = [entry for entry in timeline if first - window <= entry["tick"] < first]
        after = [entry for entry in timeline if first <= entry["tick"] <= last + window]
        rows.append({
            "t": round(mark["tick"] / tick_rate, 3), "kind": mark["kind"], "name": mark["name"],
            "sounds": [sound_name(event["sound"]) for event in starts if first <= event["tick"] <= last],
            "peak_db_before": _peak(before), "peak_db_after": _peak(after),
        })
    return rows


def _loops(events: list[dict], timeline: list[dict]) -> list[dict]:
    end_ms = timeline[-1]["ms"] if timeline else 0
    rows = []
    for event in events:
        if event["kind"] != "start" or not event.get("loop") or not event.get("length_s"):
            continue
        length_ms = event["length_s"] * 1000
        reported = [other["ms"] for other in events
                    if other["kind"] == "loop" and other["sound"] == event["sound"] and other["ms"] > event["ms"]]
        # Godot 은 반복 지점을 넘은 틱을 알려 준다. web 은 버퍼 길이로 계산한다(반복은 표본 단위로 정확하다).
        wraps = reported or [event["ms"] + length_ms * n
                             for n in range(1, int((end_ms - event["ms"]) // length_ms) + 1)]
        observed_s = (end_ms - event["ms"]) / 1000
        row = {
            "sound": sound_name(event["sound"]), "length_s": round(event["length_s"], 3),
            "started_t": round(event["t"], 3), "observed_s": round(observed_s, 2), "wraps": len(wraps),
            "continues": None, "peak_db_after_wrap": None, "quiet_ms_at_wrap": None,
        }
        for key in ("lead_silence_ms", "tail_silence_ms", "seam_jump_db"):
            if key in event:
                row[f"buffer_{key}"] = round(event[key], 2)
        if wraps and end_ms - wraps[0] >= LOOP_MARGIN_S * 1000 - 1:
            after = [entry for entry in timeline if wraps[0] <= entry["ms"] <= wraps[0] + LOOP_MARGIN_S * 1000]
            near = [entry for wrap in wraps for entry in timeline if abs(entry["ms"] - wrap) <= WRAP_WINDOW_MS]
            row["peak_db_after_wrap"] = _peak(after)
            row["continues"] = row["peak_db_after_wrap"] > SILENT_DB
            row["quiet_ms_at_wrap"] = round(max((entry["quiet_ms"] for entry in near), default=0.0), 1)
        rows.append(row)
    return rows


def _gaps(events: list[dict], timeline: list[dict]) -> list[dict]:
    """반복 소리가 재생 중인데 신호가 끊긴 구간."""
    starts = [event["ms"] for event in events if event["kind"] == "start" and event.get("loop")]
    if not starts:
        return []
    playing_from = min(starts) + 2 * WRAP_WINDOW_MS
    return [{"ms": entry["ms"], "t": round(entry["ms"] / 1000, 2), "quiet_ms": round(entry["quiet_ms"], 1)}
            for entry in timeline if entry["ms"] >= playing_from and entry["quiet_ms"] >= GAP_MS]


def _before_first_input(report: dict, marks: list[dict]) -> dict:
    inputs = [mark["tick"] for mark in marks if mark["kind"] == "input"]
    first = min(inputs, default=None)
    timeline = [entry for entry in report["timeline"] if first is None or entry["tick"] < first]
    contexts = [context for context in report.get("contexts", [])
                if first is None or context["created"]["tick"] < first]
    return {
        "seconds": round(timeline[-1]["ms"] / 1000, 2) if timeline else 0.0,
        "peak_db": _peak(timeline),
        "sounds": [sound_name(event["sound"]) for event in report["events"]
                   if event["kind"] != "loop" and (first is None or event["tick"] < first)],
        "audio_contexts": len(contexts),
    }


def _expected(expect: list[tuple[str, str]], responses: list[dict]) -> str:
    missing = []
    for name, sound in expect:
        rows = [row for row in responses if row["name"] == name]
        if not any(sound in played for row in rows for played in row["sounds"]):
            seen = "입력·사건이 없었다" if not rows else "그때 시작된 소리: " + str([row["sounds"] for row in rows])
            missing.append(f"{name} → {sound} ({seen})")
    return "ok" if not missing else "기대한 소리가 나지 않았다: " + "; ".join(missing)


def analyze(report: dict, marks: list[dict], engine: str, tick_rate: int, logs: list[dict],
            expect: list[tuple[str, str]] | None = None) -> dict:
    timeline, events = report["timeline"], report["events"]
    starts = [event for event in events if event["kind"] in ("start", "element")]
    sounds: dict[str, dict] = {}
    for event in starts:
        row = sounds.setdefault(sound_name(event["sound"]), {
            "starts": 0, "loop": bool(event.get("loop")),
            "length_s": round(event["length_s"], 3) if event.get("length_s") else None,
        })
        row["starts"] += 1
    result = {
        "measured": "엔진 안의 최종 신호 (Godot: 마스터 버스, web: destination 직전). 스피커 소리가 아니다",
        "seconds": round(timeline[-1]["ms"] / 1000, 2) if timeline else 0.0,
        "peak_db": _peak(timeline), "rms_db": _rms(timeline),
        "before_first_input": _before_first_input(report, marks),
        "sounds": sounds,
        "responses": _responses(marks, starts, timeline, tick_rate),
        "loops": _loops(events, timeline),
        "gaps": _gaps(events, timeline),
    }
    checks = {}
    checks["audible"] = "ok" if result["peak_db"] > SILENT_DB else (
        f"실행 내내 신호가 없다 (최대 {result['peak_db']} dB). 재생이 호출되지 않거나 볼륨이 0 이다")
    if engine == "web":
        early = result["before_first_input"]
        quiet = early["peak_db"] <= SILENT_DB and not early["sounds"] and not early["audio_contexts"]
        checks["silent_before_input"] = "ok" if quiet else (
            f"첫 입력 전에 소리를 내려 했다 (AudioContext {early['audio_contexts']}개, 소리 {early['sounds']}). "
            "브라우저가 막고 콘솔 경고를 낸다")
        blocked = [entry["text"] for entry in logs if any(word in entry["text"] for word in AUTOPLAY_WORDS)]
        checks["no_autoplay_warnings"] = "ok" if not blocked else f"자동 재생 경고 {len(blocked)}건: {blocked[0]}"
    stopped = [loop["sound"] for loop in result["loops"] if loop["continues"] is False]
    unknown = [loop["sound"] for loop in result["loops"] if loop["continues"] is None]
    if stopped:
        checks["loop_continues"] = "반복 지점을 지난 뒤 소리가 끊겼다: " + ", ".join(stopped)
    elif unknown:
        checks["loop_continues"] = ("반복 지점까지 재지 못했다: " + ", ".join(unknown)
                                    + ". --seconds 를 곡 길이보다 길게 준다")
    else:
        checks["loop_continues"] = "ok"
    if expect:
        checks["expected_sounds"] = _expected(expect, result["responses"])
    result["checks"] = checks
    return result
