import argparse
import importlib
import sys

from gf.core.output import GfError, fail

MODULES = [
    "gf.core.commands",
    "gf.core.fal_commands",
    "gf.gen.commands",
    "gf.post.commands",
    "gf.blender.commands",
    "gf.engine.commands",
    "gf.refs.commands",
    "gf.judge.commands",
    "gf.core.check_commands",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gf", description="gameforge 하네스 도구")
    parser.add_argument("--project", default=".", help="게임 프로젝트 디렉터리")
    sub = parser.add_subparsers(dest="group", required=True)
    for name in MODULES:
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError as exc:
            if exc.name != name:
                raise
            continue
        module.register(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args) or 0
    except GfError as exc:
        return fail(str(exc))


if __name__ == "__main__":
    sys.exit(main())
