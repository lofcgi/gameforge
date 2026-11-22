from pathlib import Path

from gf.blender import glb, runner
from gf.core.output import GfError, ok
from gf.core.paths import inside, project_dir, rel, source
from gf.post import contact


def _target(project: Path, model: Path, out: str | None, suffix: str) -> Path:
    """결과 GLB 경로. 기본은 입력 옆에 '<이름>_<작업>.glb'."""
    target = inside(project, out) if out else inside(project, str(model.with_name(f"{model.stem}_{suffix}.glb")))
    if target.suffix.lower() != ".glb":
        raise GfError(f"결과는 .glb 로만 내보낸다: {target.name}")
    return target


def info(args) -> int:
    project = project_dir(args)
    model = source(project, args.model)
    backend = args.backend
    if backend == "auto":
        backend = "blender" if runner.find_blender() else "trimesh"
    if backend == "blender":
        stats = runner.run_script(runner.SCRIPTS / "info.py", [str(model)])
    else:
        stats = glb.stats(model)
    return ok(files=[], cost_usd=0.0, backend=backend, model=rel(project, model), **stats)


def _transform(args, script: str, suffix: str, options: list[str]) -> int:
    project = project_dir(args)
    model = source(project, args.model)
    target = _target(project, model, args.out, suffix)
    result = runner.run_script(runner.SCRIPTS / script, [str(model), str(target), *options])
    return ok(files=[rel(project, target)], cost_usd=0.0, **result)


def clean(args) -> int:
    return _transform(args, "clean.py", "clean", ["--merge-distance", str(args.merge_distance)])


def decimate(args) -> int:
    if args.triangles <= 0:
        raise GfError("--triangles 는 양수여야 한다.")
    return _transform(args, "decimate.py", "decimated", ["--triangles", str(args.triangles)])


def rescale(args) -> int:
    if args.height <= 0:
        raise GfError("--height 는 양수여야 한다.")
    return _transform(args, "rescale.py", "scaled", ["--height", str(args.height), "--turn", str(args.turn)])


def turntable(args) -> int:
    project = project_dir(args)
    model = source(project, args.model)
    out_dir = inside(project, args.out)
    name = args.name or model.stem
    options = ["--name", name, "--count", str(args.count), "--size", str(args.size)]
    options += ["--elevation", str(args.elevation)]
    result = runner.run_script(runner.SCRIPTS / "turntable.py", [str(model), str(out_dir), *options])
    renders = [Path(path) for path in result["files"]]
    sheet = out_dir / f"{name}_sheet.png"
    contact.build(renders, [str(i) for i in range(len(renders))], None, min(args.size, 384)).save(sheet)
    files = [rel(project, path) for path in [*renders, sheet]]
    return ok(files=files, cost_usd=0.0, sheet=rel(project, sheet), engine=result["engine"], stats=result["stats"])


def run(args) -> int:
    project = project_dir(args)
    script = source(project, args.script)
    arguments = args.script_args[1:] if args.script_args[:1] == ["--"] else args.script_args
    result = runner.run_script(script, arguments, cwd=project, echo=True)
    return ok(files=result.get("files", []), cost_usd=0.0, script=rel(project, script), result=result)


def register(sub) -> None:
    p = sub.add_parser("blender", help="Blender 배경 실행: 3D 정리와 미리보기")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("info", help="삼각형·정점 수, 크기, 재질, 뼈대·애니메이션 유무")
    q.add_argument("model")
    q.add_argument("--backend", choices=["auto", "blender", "trimesh"], default="auto", help="auto 는 Blender 가 없을 때 trimesh(GLB 전용)를 쓴다")
    q.set_defaults(func=info)

    q = s.add_parser("clean", help="겹친 정점 합치기, 법선 정리, 변환 굽기, 원점을 바닥 중심으로")
    q.add_argument("model")
    q.add_argument("--out", help="결과 GLB (기본: <이름>_clean.glb)")
    q.add_argument("--merge-distance", type=float, default=0.0001, help="이 거리 안의 정점을 합친다(미터)")
    q.set_defaults(func=clean)

    q = s.add_parser("decimate", help="목표 삼각형 수까지 줄인다 (UV 유지)")
    q.add_argument("model")
    q.add_argument("--triangles", type=int, required=True, help="목표 삼각형 수")
    q.add_argument("--out", help="결과 GLB (기본: <이름>_decimated.glb)")
    q.set_defaults(func=decimate)

    q = s.add_parser("rescale", help="키를 미터 단위로 맞추고 바닥 중심을 원점에 둔다 (GLB: Y 위, +Z 정면)")
    q.add_argument("model")
    q.add_argument("--height", type=float, required=True, help="목표 키(미터)")
    q.add_argument("--turn", type=float, default=0.0, help="위쪽 축 둘레로 돌릴 각도(도). 모델의 정면이 +Z 를 보게 맞춘다 (+X 를 보는 생성 모델은 -90). 턴테이블 0번에 정면이 보이면 맞다")
    q.add_argument("--out", help="결과 GLB (기본: <이름>_scaled.glb)")
    q.set_defaults(func=rescale)

    q = s.add_parser("turntable", help="모델 둘레를 돌며 미리보기 PNG 를 렌더한다")
    q.add_argument("model")
    q.add_argument("--out", default="captures/turntable")
    q.add_argument("--name", help="파일 이름 앞부분 (기본: 모델 이름)")
    q.add_argument("--count", type=int, default=8, help="렌더할 장수")
    q.add_argument("--size", type=int, default=512, help="한 변(px)")
    q.add_argument("--elevation", type=float, default=20.0, help="카메라 올려본 각도(도)")
    q.set_defaults(func=turntable)

    q = s.add_parser("run", help="임의의 Python 스크립트를 Blender 에서 실행한다 (코드로 모델 만들기)")
    q.add_argument("script")
    q.add_argument("script_args", nargs="...", help="스크립트에 넘길 인자 (sys.argv 의 -- 뒤)")
    q.set_defaults(func=run)
