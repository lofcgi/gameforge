from pathlib import Path

from gf.core.output import GfError

HARNESS_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = HARNESS_ROOT / "templates"


def project_dir(args) -> Path:
    return Path(args.project).expanduser().resolve()


def gf_dir(project: Path, must_exist: bool = True) -> Path:
    d = project / ".gf"
    if must_exist and not d.is_dir():
        raise GfError(f"{project} 는 gameforge 프로젝트가 아니다 (.gf 없음). 먼저 gf init 을 실행한다.")
    return d


def resolve(project: Path, value: str) -> Path:
    """상대 경로는 게임 프로젝트 기준으로 본다."""
    path = Path(value).expanduser()
    return (path if path.is_absolute() else project / path).resolve()


def inside(project: Path, value: str) -> Path:
    """결과 경로. 게임 프로젝트 밖이면 거부한다."""
    path = resolve(project, value)
    if not path.is_relative_to(project):
        raise GfError(f"결과는 게임 프로젝트 안에만 쓴다: {path}")
    return path


def source(project: Path, value: str) -> Path:
    path = resolve(project, value)
    if not path.exists():
        raise GfError(f"입력이 없다: {path}")
    return path


def rel(project: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project))
    except ValueError:
        return str(path)
