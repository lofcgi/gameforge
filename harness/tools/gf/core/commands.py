import shutil
import subprocess
from pathlib import Path

from gf.core import ledger, render_profile, state
from gf.core.output import GfError, ok
from gf.core.paths import TEMPLATES, gf_dir, project_dir

PROJECT_DIRS = [
    "design/look",
    "references/inbox",
    "references/picked",
    "assets/raw",
    "assets/game",
    "captures",
]


def init(args) -> int:
    project = project_dir(args)
    if (project / ".gf").exists():
        raise GfError(f"{project} 에는 이미 .gf 가 있다.")
    template = TEMPLATES / f"{args.engine}-{args.dim}"
    if not template.is_dir():
        raise GfError(f"템플릿이 없다: {template}")
    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, project, dirs_exist_ok=True)
    render = render_profile.apply(project, template.name, args.style)
    gf_dir(project, must_exist=False).mkdir()
    for sub in PROJECT_DIRS:
        (project / sub).mkdir(parents=True, exist_ok=True)
    name = args.name or project.name
    state.save(project, state.new(name, args.engine, args.dim, args.style))
    (project / ".gf" / "config.toml").write_text("# 역할별 모델을 바꾸려면 [roles] 아래에 적는다.\n")
    return ok(project=str(project), template=template.name, render=render, state=state.load(project))


def state_show(args) -> int:
    project = project_dir(args)
    return ok(state=state.load(project), spent_usd=round(ledger.total(project), 4))


def state_set(args) -> int:
    return ok(state=state.set_stage(project_dir(args), args.stage))


def state_approve(args) -> int:
    return ok(state=state.approve(project_dir(args), args.note))


def _version(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[0] if lines else None


def doctor(args) -> int:
    import os

    from gf.core import fal

    tools = {
        "godot": _version(["godot", "--version"]),
        "blender": _version(["blender", "--version"]),
        "ffmpeg": _version(["ffmpeg", "-version"]),
        "node": _version(["node", "--version"]),
        "bun": _version(["bun", "--version"]),
    }
    chrome = Path("/Applications/Google Chrome.app").exists()
    try:
        fal.load_key(project_dir(args))
        key = True
    except GfError:
        key = bool(os.environ.get("FAL_KEY"))
    missing = [name for name, version in tools.items() if version is None]
    return ok(tools=tools, chrome=chrome, fal_key=key, missing=missing)


def register(sub) -> None:
    p = sub.add_parser("init", help="템플릿으로 게임 프로젝트를 만든다")
    p.add_argument("--engine", choices=state.ENGINES, required=True)
    p.add_argument("--dim", choices=state.DIMS, required=True)
    p.add_argument("--style", choices=state.STYLES, required=True)
    p.add_argument("--name")
    p.set_defaults(func=init)

    p = sub.add_parser("state", help="단계 상태")
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("show").set_defaults(func=state_show)
    q = s.add_parser("set")
    q.add_argument("stage", choices=state.STAGES)
    q.set_defaults(func=state_set)
    q = s.add_parser("approve", help="현재 단계를 승인하고 다음 단계로 넘어간다")
    q.add_argument("--note", default="")
    q.set_defaults(func=state_approve)

    sub.add_parser("doctor", help="환경 점검").set_defaults(func=doctor)
