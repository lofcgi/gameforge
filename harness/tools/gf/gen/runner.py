"""모든 생성 명령이 공유하는 흐름: 스키마 맞추기 → 비용 추정 → 한도 확인 → 호출 → 내려받기 → 기록."""

import sys
import time
from pathlib import Path
from typing import Any

from gf.core import config, fal, ledger
from gf.core.output import GfError, ok
from gf.core.paths import gf_dir, inside, project_dir, rel, resolve
from gf.gen import catalog, cost, mapping
from gf.gen.mapping import Upload

FALLBACK_SUFFIX = {"image": ".png", "video": ".mp4", "model3d": ".glb", "audio": ".mp3"}


def media(project: Path, value: str) -> Upload | str:
    """입력 파일. http(s) URL 은 그대로 넘기고 로컬 경로는 호출 직전에 올린다."""
    if value.startswith(("http://", "https://")):
        return value
    path = resolve(project, value)
    if not path.is_file():
        raise GfError(f"입력 파일이 없다: {path}")
    return Upload(path)


def _map_uploads(value: Any, convert) -> Any:
    if isinstance(value, Upload):
        return convert(value)
    if isinstance(value, list):
        return [_map_uploads(item, convert) for item in value]
    return value


def _shown(project: Path, arguments: dict) -> dict:
    return {k: _map_uploads(v, lambda u: f"<upload:{rel(project, u.path)}>") for k, v in arguments.items()}


def _uploaded(arguments: dict) -> dict:
    return {k: _map_uploads(v, lambda u: fal.upload(u.path)) for k, v in arguments.items()}


def result_files(value: Any, trail: tuple = ()) -> list[tuple[str, dict]]:
    """결과 JSON 안의 파일 객체를 (위치 이름, 객체)로 모은다. 위치 이름이 파일 이름에 붙는다."""
    found = []
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.startswith("http"):
            found.append(("-".join(str(part) for part in trail), value))
        for key, child in value.items():
            found += result_files(child, (*trail, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found += result_files(child, (*trail, index))
    return found


def _download(result: dict, out_dir: Path, name: str, kind: str) -> list[Path]:
    unique: dict[str, tuple[str, dict]] = {}
    for label, item in result_files(result):
        unique.setdefault(item["url"], (label, item))
    if not unique:
        raise GfError(f"결과에 파일 URL 이 없다: {str(result)[:400]}")
    saved = []
    for label, item in unique.values():
        suffix = fal.extension_for(item["url"], item.get("content_type"), FALLBACK_SUFFIX[kind])
        stem = name if len(unique) == 1 else f"{name}_{label}"
        saved.append(fal.download(item["url"], out_dir / f"{stem}{suffix}"))
    return saved


def _refuse_overwrite(out_dir: Path, name: str) -> None:
    taken = [p.name for p in out_dir.glob(f"{name}*") if p.stem == name or p.name.startswith(f"{name}_")]
    if taken:
        raise GfError(f"{out_dir} 에 이미 '{name}' 결과가 있다 ({', '.join(sorted(taken)[:3])}). --name 을 바꾼다.")


def _estimate(args, info: dict, arguments: dict) -> tuple[float | None, str | None]:
    estimated, note = cost.estimate(info["price"], cost.usage(info["input"], arguments))
    if estimated is None and args.estimate_usd is not None:
        return args.estimate_usd, f"{note} --estimate-usd 로 받은 값을 썼다."
    return estimated, note


def generate(args, role: str, kind: str, semantic: dict, direct: dict) -> int:
    project = project_dir(args)
    gf_dir(project)
    fal.load_key(project)
    endpoint = args.model or config.model_for(project, role)
    info = catalog.describe(project, endpoint, args.refresh)
    extra = dict(mapping.parse_extra(pair, lambda value: resolve(project, value)) for pair in args.arg or [])
    arguments = mapping.build(endpoint, info["input"], semantic, direct, extra)
    estimated, note = _estimate(args, info, arguments)
    out_dir = inside(project, args.out or f"assets/raw/{kind}")
    name = args.name or f"{kind}-{time.strftime('%Y%m%d-%H%M%S')}"
    _refuse_overwrite(out_dir, name)
    summary = {
        "role": role,
        "endpoint": endpoint,
        "arguments": _shown(project, arguments),
        "unit": info["price"],
        "cost_usd": estimated,
        "cost_note": note,
    }
    if args.dry_run:
        return ok(files=[], dry_run=True, **summary)
    fal.guard_budget(project, endpoint, estimated, args.max_usd, args.allow_unknown_cost)
    if estimated is None:
        print(f"경고: {note} --allow-unknown-cost 로 한도 확인 없이 호출한다.", file=sys.stderr)
    result = fal.run(endpoint, _uploaded(arguments), log=lambda message: print(message, file=sys.stderr))
    files = [rel(project, path) for path in _download(result, out_dir, name, kind)]
    prompt = semantic.get("prompt")
    fal.record(project, endpoint, role, info["price"], estimated, files, prompt)
    if args.keep:
        ledger.remember_prompt(project, role=role, endpoint=endpoint, prompt=prompt, arguments=summary["arguments"], files=files)
    return ok(files=files, **summary, result=result)
