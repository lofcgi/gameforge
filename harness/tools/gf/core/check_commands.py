"""훅과 단계 승인 직전에 부르는 검사. 네트워크를 쓰지 않고, 실패하면 무엇을 하면 되는지 말한다."""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from gf.core import state
from gf.core.output import GfError, fail, ok
from gf.core.paths import gf_dir, project_dir, rel

IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "svg", "bmp", "gif"}
MODEL_EXT = {"glb", "gltf", "obj", "fbx"}
AUDIO_EXT = {"ogg", "wav", "mp3", "flac", "opus", "m4a"}
FONT_EXT = {"ttf", "otf", "woff", "woff2"}
ASSET_EXT = IMAGE_EXT | MODEL_EXT | AUDIO_EXT | FONT_EXT

CODE_SUFFIXES = {
    ".gd", ".tscn", ".tres", ".gdshader", ".godot",
    ".js", ".mjs", ".ts", ".html", ".css", ".glsl", ".wgsl",
}
# 게임을 이루지 않는 폴더. 여기의 변경은 "코드가 바뀌었다"로 세지 않는다.
PRUNED_DIRS = {
    ".gf", ".godot", ".git", "node_modules", "captures", "references", "design",
    "bot", "build", "dist", "export",
}
GENERATED_SUFFIXES = {".import", ".uid"}
ENGINE_STAGES = {"graybox", "assets", "polish", "publish"}
ASSET_STAGES = {"assets", "polish", "publish"}
AUDIO_STAGES = {"polish", "publish"}

TEST_RESULT = "captures/test/result.json"
SILENT_DB = -60.0
LATE_SFX_MS = 30.0
"""효과음 앞의 무음이 이보다 길면 누른 뒤 늦게 들린다."""
LOOP_NAME = re.compile(r"theme|music|bgm|loop|ambien", re.IGNORECASE)
PIXEL_MAX_COLOURS = 64

_REFERENCE = re.compile(
    r"""["'(]((?:res://|\./|/)?[\w@.\-/ ]+?\.(?:""" + "|".join(sorted(ASSET_EXT)) + r"""))["')?#]""",
    re.IGNORECASE,
)
_COMMENT = re.compile(r"^\s*(#|//|\*|/\*|<!--|;)")


def _project(args) -> Path:
    project = project_dir(args)
    gf_dir(project)
    return project


def _walk(project: Path):
    """게임을 이루는 파일들. assets/raw 와 하네스·엔진 캐시는 건너뛴다."""
    for root, dirs, files in os.walk(project):
        here = Path(root)
        dirs[:] = [
            name for name in dirs
            if name not in PRUNED_DIRS and not (here == project / "assets" and name == "raw")
        ]
        for name in files:
            yield here / name


def game_inputs(project: Path) -> list[Path]:
    """화면과 동작을 바꾸는 파일: 게임 코드와 assets/game 의 내용물."""
    game_assets = project / "assets" / "game"
    found = []
    for path in _walk(project):
        if path.suffix in GENERATED_SUFFIXES or path.name.startswith("."):
            continue
        if path.suffix in CODE_SUFFIXES or path.is_relative_to(game_assets):
            found.append(path)
    return found


def last_change(project: Path) -> tuple[float, Path | None]:
    newest, source = 0.0, None
    for path in game_inputs(project):
        mtime = path.stat().st_mtime
        if mtime > newest:
            newest, source = mtime, path
    return newest, source


def _optional_names(text: str) -> set[str]:
    """exists(...) 로 있는지 확인하고 쓰는 식별자와 문자열. 없어도 게임이 도는 참조다."""
    return set(re.findall(r"exists\w*\(\s*[\"']?([\w./:@-]+)", text))


def references(project: Path) -> list[dict]:
    """게임 코드가 문자열로 가리키는 에셋 경로와, 그것이 실제로 있는지."""
    found: dict[tuple[str, str], dict] = {}
    for path in _walk(project):
        if path.suffix not in CODE_SUFFIXES or path.is_relative_to(project / "gf"):
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        optional = _optional_names(text)
        for line in text.splitlines():
            if _COMMENT.match(line):
                continue
            for match in _REFERENCE.finditer(line):
                raw = match.group(1).strip()
                if "://" in raw and not raw.startswith("res://"):
                    continue
                target = _resolve(project, path, raw)
                name = re.match(r"\s*(?:const|var|let|export const|@export var)?\s*(\w+)", line)
                is_optional = raw in optional or bool(name and name.group(1) in optional)
                key = (rel(project, path), raw)
                found[key] = {
                    "from": key[0],
                    "ref": raw,
                    "file": rel(project, target),
                    "kind": _kind(target),
                    "exists": target.is_file(),
                    "bytes": target.stat().st_size if target.is_file() else 0,
                    "optional": is_optional,
                }
    return sorted(found.values(), key=lambda item: (item["from"], item["ref"]))


def _resolve(project: Path, source: Path, raw: str) -> Path:
    """참조가 가리키는 파일. 프로젝트 루트 기준, 참조한 파일 옆, assets/game 아래의 순서로 찾고, 없으면 루트 기준 경로다."""
    cleaned = raw.removeprefix("res://").removeprefix("./").lstrip("/")
    at_root = project / cleaned
    if at_root.is_file():
        return at_root
    beside = source.parent / cleaned
    if beside.is_file():
        return beside
    return _in_game_assets(project, cleaned) or at_root


def _in_game_assets(project: Path, cleaned: str) -> Path | None:
    """assets/game 아래에서 이 경로로 끝나는 파일. 게임이 에셋 폴더를 뺀 경로("boats/boat1.png", "body.ttf")를 적고
    읽을 때 폴더를 붙이는 경우다. 폴더까지 적힌 경로는 폴더도 맞아야 한다."""
    parts = Path(cleaned).parts
    for path in sorted((project / "assets" / "game").rglob(parts[-1])):
        if path.is_file() and path.parts[-len(parts):] == parts:
            return path
    return None


def _kind(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    for kind, group in (("image", IMAGE_EXT), ("model", MODEL_EXT), ("audio", AUDIO_EXT)):
        if ext in group:
            return kind
    return "font"


def _broken(refs: list[dict]) -> list[str]:
    problems = []
    for item in refs:
        if not item["exists"]:
            if not item["optional"]:
                problems.append(f"{item['from']} 가 가리키는 {item['file']} 이 없다")
        elif item["bytes"] == 0:
            problems.append(f"{item['from']} 가 가리키는 {item['file']} 이 빈 파일이다")
    return problems


def pixel_problems(project: Path) -> list[str]:
    """픽셀 스타일 프로젝트의 assets/game 에 후처리 안 된 그림이 섞였는지 본다."""
    from gf.post import inspect_image
    from gf.post.io import load_rgba

    problems = []
    folder = project / "assets" / "game"
    for path in sorted(folder.rglob("*.png")) if folder.is_dir() else []:
        if path.stat().st_size == 0:
            continue
        report = inspect_image.report(load_rgba(path), PIXEL_MAX_COLOURS)
        if not report["pixel_art"]:
            problems.append(f"{rel(project, path)}: {'; '.join(report['reasons'])}")
    return problems


def assets_report(project: Path) -> dict:
    refs = [item for item in references(project) if item["kind"] != "audio"]
    problems = _broken(refs)
    hints = []
    if problems:
        hints.append("없는 파일은 만들어 assets/game/ 에 넣거나, 쓰지 않는 참조를 코드에서 지운다.")
    if state.load(project).get("style") == "pixel":
        raw = pixel_problems(project)
        if raw:
            problems += raw
            hints.append(
                "픽셀 프로젝트의 assets/game 에는 1x 픽셀 아트만 둔다: "
                "gf post chroma --hard → gf post pixel-snap → gf post palette apply 를 거친 뒤 "
                "gf post inspect 로 pixel_art=true 를 확인하고 옮긴다."
            )
    return {
        "references": len(refs),
        "optional_missing": [r["file"] for r in refs if r["optional"] and not r["exists"]],
        "problems": problems,
        "hints": hints,
    }


def measure_audio(path: Path) -> dict:
    """ffmpeg 로 길이와 음량을 잰다. 에이전트는 듣지 못하므로 숫자로 확인한다."""
    binary = shutil.which("ffmpeg")
    if not binary:
        raise GfError("ffmpeg 를 찾지 못했다. 오디오 음량을 잴 수 없다.")
    result = subprocess.run(
        [binary, "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    return parse_volume(result.stderr)


def parse_volume(log: str) -> dict:
    def number(pattern: str) -> float | None:
        match = re.search(pattern, log)
        return float(match.group(1)) if match else None

    duration = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", log)
    seconds = None
    if duration:
        hours, minutes, rest = duration.groups()
        seconds = round(int(hours) * 3600 + int(minutes) * 60 + float(rest), 3)
    return {
        "duration_s": seconds,
        "mean_db": number(r"mean_volume:\s*(-?[\d.]+|-inf) dB"),
        "max_db": number(r"max_volume:\s*(-?[\d.]+|-inf) dB"),
    }


def loudness(path: Path) -> float | None:
    """EBU R128 통합 음량(LUFS). 0.4초보다 짧은 소리는 잴 수 없어 None."""
    result = subprocess.run(
        [shutil.which("ffmpeg") or "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128",
         "-f", "null", "-"], capture_output=True, text=True, timeout=120, check=False,
    )
    found = re.findall(r"\bI:\s+(-?[\d.]+) LUFS", result.stderr)
    return float(found[-1]) if found and float(found[-1]) > -70.0 else None


def inspect_audio(path: Path, loop: bool) -> tuple[dict, list[str]]:
    """파일을 풀어 잘림·직류 치우침·앞뒤 무음을 재고, 반복 재생할 소리면 이음매도 잰다. (잰 값, 경고)."""
    from gf.post import audio_loop

    samples, rate = audio_loop.decode(path)
    fields = {**audio_loop.file_report(samples, rate), "lufs": loudness(path), "loop": loop}
    warnings = []
    if fields["clipped_runs"]:
        warnings.append(f"파형이 잘린 곳이 {fields['clipped_runs']}군데 있다 (찢어지는 소리). 다시 생성하거나 음량을 낮춰 다시 만든다")
    if fields["dc_offset"] > audio_loop.MAX_DC_OFFSET:
        warnings.append(f"파형이 한쪽으로 치우쳤다 (직류 {fields['dc_offset']}). 시작·끝에서 딱 소리가 날 수 있다")
    if loop:
        fields["seam"] = audio_loop.seam_report(samples, rate)
        warnings += [f"반복 이음매: {problem}" for problem in fields["seam"]["problems"]]
        if fields["seam"]["problems"]:
            warnings.append("gf post audio-loop 로 다듬고 다시 잰다")
    elif fields["lead_silence_ms"] > LATE_SFX_MS:
        warnings.append(f"앞에 무음이 {fields['lead_silence_ms']}ms 있다. 효과음이면 그만큼 늦게 들린다")
    return fields, warnings


def loop_hints(project: Path) -> set[str]:
    """반복 재생할 것으로 보이는 오디오: 파일 이름이 음악·환경음 같거나, 가리키는 줄에 loop 가 있다."""
    found = set()
    for path in _walk(project):
        if path.suffix not in CODE_SUFFIXES or path.is_relative_to(project / "gf"):
            continue
        for line in path.read_text(errors="replace").splitlines():
            if _COMMENT.match(line):
                continue
            for match in _REFERENCE.finditer(line):
                target = _resolve(project, path, match.group(1).strip())
                if _kind(target) == "audio" and (LOOP_NAME.search(target.stem) or "loop" in line.lower()):
                    found.add(rel(project, target))
    return found


def balance(rows: list[dict]) -> dict | None:
    """반복 소리(음악)와 한 번 나는 소리(효과음)의 파일 음량 차이. 게임 안의 균형은 재생 볼륨까지 곱해진 값이라
    `gf engine audio` 의 측정으로 본다."""
    music = [row["rms_db"] for row in rows if row.get("loop") and "rms_db" in row]
    effects = sorted(row["rms_db"] for row in rows if row.get("loop") is False and "rms_db" in row)
    if not music or not effects:
        return None
    middle = effects[len(effects) // 2]
    return {"loop_rms_db": max(music), "oneshot_rms_db_median": middle, "loop_minus_oneshot_db": round(max(music) - middle, 1)}


def _audio_verdict(label: str, path: Path, measure) -> tuple[dict, str | None]:
    if not path.is_file():
        return {"file": label, "exists": False}, f"{label} 이 없다"
    if path.stat().st_size == 0:
        return {"file": label, "exists": True, "bytes": 0}, f"{label} 이 빈 파일이다"
    measured = measure(path)
    row = {"file": label, "exists": True, "bytes": path.stat().st_size, **measured}
    if measured["max_db"] is None:
        return row, f"{label} 을 오디오로 읽지 못했다"
    if measured["max_db"] <= SILENT_DB:
        return row, f"{label} 은 소리가 없다 (최대 {measured['max_db']} dB)"
    return row, None


def audio_report(project: Path, extra: list[Path], require: bool, measure=measure_audio,
                 inspect=None, loops: frozenset[str] = frozenset()) -> dict:
    """inspect 를 주면(`inspect_audio`) 소리가 나는 파일마다 더 재고, 고칠 만한 것을 warnings 에 담는다.
    loops 는 반복 재생할 파일(게임 프로젝트 기준 경로)이다."""
    refs = [item for item in references(project) if item["kind"] == "audio"]
    rows, problems, warnings = [], [], []
    targets = {item["file"]: project / item["file"] for item in refs if not (item["optional"] and not item["exists"])}
    targets.update({rel(project, path): path for path in extra})
    for label, path in sorted(targets.items()):
        row, problem = _audio_verdict(label, path, measure)
        rows.append(row)
        if problem:
            problems.append(problem)
        elif inspect is not None:
            fields, found = inspect(path, label in loops)
            row.update(fields)
            warnings += [f"{label}: {warning}" for warning in found]
    hints = []
    if require and not refs:
        problems.append("게임 코드가 오디오 파일을 하나도 참조하지 않는다 (소리 없는 빌드)")
        hints.append(
            "gf gen sfx / gf gen music 으로 만들어 assets/game/audio/ 에 두고 게임에서 재생한다. "
            "의도적으로 무음 게임이면 사용자에게 확인받은 뒤 .gf/config.toml 에 [check] allow_silent = true 를 적는다."
        )
    elif problems:
        hints.append("없는 파일은 다시 만들고, 무음 파일은 다시 생성한다. 사람에게 직접 들어 보게 한다.")
    report = {"referenced": len(refs), "audio": rows, "problems": problems, "hints": hints}
    if inspect is not None:
        report.update(warnings=warnings, balance=balance(rows))
    return report


def allows_silent(project: Path) -> bool:
    """사용자가 무음 게임으로 정했는가: .gf/config.toml 의 [check] allow_silent = true."""
    from gf.core import config

    return config.load(project).get("check", {}).get("allow_silent") is True


def _fresh_shots(project: Path, since: float) -> list[Path]:
    """마지막 변경 뒤에 찍은 플레이어 시점 스크린샷 (스모크 테스트의 첫 화면과 심사 쌍은 빼고)."""
    captures = project / "captures"
    if not captures.is_dir():
        return []
    skip = (captures / "test", captures / "judge")
    return [
        path for path in captures.rglob("*.png")
        if not any(path.is_relative_to(folder) for folder in skip) and path.stat().st_mtime >= since
    ]


def _nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def evidence_report(project: Path, stage: str, measure=measure_audio) -> dict:
    problems, hints = [], []
    if stage == "plan":
        if not _nonempty(project / "design" / "brief.md"):
            problems.append("design/brief.md 가 없거나 비었다")
            hints.append("gf-plan 절차로 설계 요약을 쓰고 사용자에게 보여 준 뒤 승인한다.")
    elif stage == "look":
        look = project / "design" / "look"
        if not _nonempty(project / "design" / "art-direction.md"):
            problems.append("design/art-direction.md 가 없거나 비었다")
        if not (look.is_dir() and any(p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} for p in look.iterdir())):
            problems.append("design/look/ 에 기준 이미지가 없다")
        if problems:
            hints.append("gf-look 절차로 기준 이미지를 design/look/ 에 두고 아트 디렉션을 쓴 뒤 승인한다.")
    if stage in ENGINE_STAGES:
        changed, source = last_change(project)
        result = project / TEST_RESULT
        changed_by = f" (마지막 변경: {rel(project, source)})" if source else ""
        if not result.is_file():
            problems.append(f"통과한 스모크 테스트 기록({TEST_RESULT})이 없다")
        else:
            try:
                passed = json.loads(result.read_text()).get("ok") is True
            except ValueError:
                passed = False
            if not passed:
                problems.append("마지막 스모크 테스트가 실패했다")
            elif result.stat().st_mtime < changed:
                problems.append(f"스모크 테스트 기록이 마지막 변경보다 오래됐다{changed_by}")
        if not _fresh_shots(project, changed):
            problems.append(f"마지막 변경 뒤에 찍은 스크린샷이 captures/ 에 없다{changed_by}")
        if problems:
            hints.append(
                "gf engine test 로 스모크 테스트를 다시 돌리고, gf engine capture 또는 gf engine bot 으로 "
                "지금 화면을 찍어 직접 본 다음 사용자에게 보여 준다."
            )
    if stage in ASSET_STAGES:
        report = assets_report(project)
        problems += report["problems"]
        hints += report["hints"]
    if stage in AUDIO_STAGES:
        report = audio_report(project, [], require=not allows_silent(project), measure=measure)
        problems += report["problems"]
        hints += report["hints"]
    return {"stage": stage, "problems": problems, "hints": hints}


def _finish(summary: str, report: dict) -> int:
    if report["problems"]:
        message = f"{summary}: " + " / ".join(report["problems"])
        if report["hints"]:
            message += " → " + " ".join(report["hints"])
        return fail(message, **report)
    return ok(cost_usd=0.0, files=[], **report)


def cmd_evidence(args) -> int:
    project = _project(args)
    stage = args.stage or state.load(project)["stage"]
    return _finish(f"'{stage}' 단계를 승인할 근거가 부족하다", evidence_report(project, stage))


def cmd_assets(args) -> int:
    return _finish("에셋 검사 실패", assets_report(_project(args)))


def cmd_audio(args) -> int:
    project = _project(args)
    extra = [(project / value).resolve() for value in args.files]
    require = args.require or (state.load(project)["stage"] in AUDIO_STAGES and not allows_silent(project))
    loops = loop_hints(project) | {rel(project, (project / value).resolve()) for value in args.loop}
    extra += [(project / value).resolve() for value in args.loop]
    report = audio_report(project, extra, require and not extra, inspect=inspect_audio, loops=frozenset(loops))
    if args.strict and report["warnings"]:
        report["problems"] += report["warnings"]
    return _finish("오디오 검사 실패", report)


def register(sub) -> None:
    p = sub.add_parser("check", help="훅과 단계 승인 전에 쓰는 검사")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("evidence", help="현재 단계를 승인해도 되는 근거가 있는지 본다")
    q.add_argument("--stage", choices=state.STAGES, help="검사할 단계 (기본: 현재 단계)")
    q.set_defaults(func=cmd_evidence)

    q = s.add_parser("assets", help="게임이 참조하는 에셋이 있는지, 픽셀 프로젝트에 원본이 섞였는지 본다")
    q.set_defaults(func=cmd_assets)

    q = s.add_parser("audio", help="게임이 참조하는 오디오가 있고 소리가 나는지, 잘림·무음·반복 이음매는 어떤지 잰다")
    q.add_argument("files", nargs="*", help="추가로 잴 오디오 파일 (게임 프로젝트 기준). 주면 그 파일들의 측정값을 낸다")
    q.add_argument("--require", action="store_true", help="오디오 참조가 하나도 없으면 실패로 본다")
    q.add_argument("--loop", action="append", default=[], metavar="FILE",
                   help="반복 재생할 파일. 끝에서 처음으로 넘어가는 이음매를 잰다 (이름이 theme/music/bgm/loop/ambient 이거나 "
                        "코드에서 loop 와 같은 줄에 있으면 알아서 잰다). 여러 번 줄 수 있다")
    q.add_argument("--strict", action="store_true", help="warnings(이음매, 잘림, 앞 무음)가 있으면 실패로 끝낸다")
    q.set_defaults(func=cmd_audio)
