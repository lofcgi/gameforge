import json
from pathlib import Path

from gf.core.output import GfError, ok
from gf.core.paths import gf_dir, project_dir, rel, resolve
from gf.judge import pairs


def _project(args) -> Path:
    project = project_dir(args)
    gf_dir(project)
    return project


def pair(args) -> int:
    project = _project(args)
    result = pairs.create(
        project,
        args.id,
        resolve(project, args.a),
        resolve(project, args.b),
        target=resolve(project, args.target) if args.target else None,
        mode=args.mode,
        series=args.series,
    )
    return ok(
        cost_usd=0.0,
        id=args.id,
        mode=args.mode,
        series=args.series,
        judge_reads=result["folder"],
        judge_must_not_read=rel(project, pairs.secret_dir(project)),
        **result,
    )


def _parse_scores(text: str | None) -> dict | None:
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError as exc:
        raise GfError("--scores 가 JSON 이 아니다") from exc


def record(args) -> int:
    project = _project(args)
    result = pairs.record(
        project,
        args.id,
        args.winner,
        scores=_parse_scores(args.scores),
        notes=args.notes,
        series=args.series,
        stop_after=args.stop_after,
    )
    entry, summary = result["entry"], result["summary"]
    fields = {
        "files": [rel(project, pairs.history_path(project))],
        "cost_usd": 0.0,
        "id": args.id,
        "series": entry["series"],
        "mode": entry["mode"],
        "winner": entry["winner"],
        "winner_file": entry["winner_file"],
        "counts": {key: summary[key] for key in ("rounds", "wins", "ties", "losses")},
        "stop": summary["stop"],
        "rules": pairs.RULES,
    }
    if entry["mode"] == "change":
        fields["keep_change"] = entry["winner"] in ("b", "tie")
    return ok(**fields)


def history(args) -> int:
    project = _project(args)
    rounds = pairs.load_history(project)
    names = [args.series] if args.series else list(dict.fromkeys(item["series"] for item in rounds))
    series = {}
    for name in names:
        own = [item for item in rounds if item["series"] == name]
        if not own:
            raise GfError(f"시리즈 '{name}' 의 기록이 없다.")
        series[name] = {
            **pairs.summarise(own, args.stop_after),
            "results": [
                {key: item[key] for key in ("at", "id", "winner", "winner_file", "notes")}
                for item in own
            ],
        }
    return ok(files=[], cost_usd=0.0, series=series)


def register(sub) -> None:
    p = sub.add_parser("judge", help="블라인드 심사용 쌍 만들기와 결과 기록")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("pair", help="두 이미지를 X/Y 로 섞어 심사 폴더를 만든다")
    q.add_argument("--a", required=True, help="change: 수정 전 화면 / target: 목표 그림")
    q.add_argument("--b", required=True, help="change: 수정 후 화면 / target: 게임 화면")
    q.add_argument("--target", help="change 방식에서 함께 보여 줄 목표 그림")
    q.add_argument("--id", required=True, help="심사 쌍 이름 (영문·숫자·._-)")
    q.add_argument(
        "--mode", choices=list(pairs.MODES), default="change", help="; ".join(pairs.MODES.values())
    )
    q.add_argument("--series", default="default", help="승패를 함께 셀 묶음 이름")
    q.set_defaults(func=pair)

    q = s.add_parser("record", help="심사 결과를 실제 이미지로 풀어 기록한다")
    q.add_argument("--id", required=True)
    q.add_argument("--winner", required=True, choices=[*pairs.LABELS, "tie"])
    q.add_argument("--scores", help='심사자가 낸 점수 JSON: {"X": {...}, "Y": {...}}')
    q.add_argument("--notes", default="")
    q.add_argument("--series", help="pair 때 정한 묶음 이름을 바꿔 기록한다")
    q.add_argument(
        "--stop-after", type=int, default=pairs.DEFAULT_STOP, help="멈춤 기준 횟수 (기본 2)"
    )
    q.set_defaults(func=record)

    q = s.add_parser("history", help="시리즈별 승패 요약")
    q.add_argument("--series")
    q.add_argument("--stop-after", type=int, default=pairs.DEFAULT_STOP)
    q.set_defaults(func=history)
