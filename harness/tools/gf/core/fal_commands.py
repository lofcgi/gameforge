import json

from gf.core import fal
from gf.core.output import GfError, ok
from gf.core.paths import project_dir, rel, resolve


def _input_schema(model: dict) -> dict:
    """OpenAPI 문서에서 POST 요청 본문의 스키마만 뽑는다."""
    spec = model.get("openapi") or {}
    schemas = (spec.get("components") or {}).get("schemas") or {}
    for path_item in (spec.get("paths") or {}).values():
        post = path_item.get("post")
        if not post:
            continue
        content = ((post.get("requestBody") or {}).get("content") or {}).get("application/json") or {}
        ref = (content.get("schema") or {}).get("$ref")
        if ref:
            return schemas.get(ref.rsplit("/", 1)[-1], {})
    return {}


def summarize_schema(model: dict) -> dict:
    schema = _input_schema(model)
    required = set(schema.get("required") or [])
    fields = {}
    for name, spec in (schema.get("properties") or {}).items():
        field = {"required": name in required}
        for key in ("type", "enum", "default", "description", "minimum", "maximum"):
            if key in spec:
                field[key] = spec[key]
        if "anyOf" in spec:
            field["anyOf"] = [a.get("type") or a.get("$ref", "").rsplit("/", 1)[-1] for a in spec["anyOf"]]
            # enum 이 anyOf 안(값 | null)에 들어 있는 필드도 호출 전에 값을 확인할 수 있게 올려 둔다.
            nested = [value for a in spec["anyOf"] for value in a.get("enum", [])]
            if nested and "enum" not in field:
                field["enum"] = nested
        if "description" in field:
            field["description"] = field["description"][:200]
        fields[name] = field
    return fields


def collect_urls(value, found: list[dict]) -> None:
    """결과 JSON 안에서 파일 URL을 가진 객체를 모두 찾는다."""
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.startswith("http"):
            found.append(value)
        for child in value.values():
            collect_urls(child, found)
    elif isinstance(value, list):
        for child in value:
            collect_urls(child, found)


def search(args) -> int:
    fal.load_key(project_dir(args))
    return ok(models=fal.search(args.query, args.limit))


def price(args) -> int:
    fal.load_key(project_dir(args))
    return ok(prices=[fal.price(endpoint) for endpoint in args.endpoint])


def schema(args) -> int:
    fal.load_key(project_dir(args))
    model = fal.schema(args.endpoint)
    return ok(endpoint=args.endpoint, input=summarize_schema(model))


def run(args) -> int:
    project = project_dir(args)
    fal.load_key(project)
    arguments = json.loads(args.args)
    for pair in args.upload or []:
        if "=" not in pair:
            raise GfError("--upload 는 필드=파일경로 형태다.")
        field, path = pair.split("=", 1)
        arguments[field] = fal.upload(resolve(project, path))
    unit = fal.price(args.endpoint)
    fal.guard_budget(project, args.endpoint, args.estimate_usd, args.max_usd, args.allow_unknown_cost)
    result = fal.run(args.endpoint, arguments)
    out = resolve(project, args.out)
    files: list[dict] = []
    collect_urls(result, files)
    saved = []
    for index, item in enumerate(files):
        suffix = fal.extension_for(item["url"], item.get("content_type"), ".bin")
        target = out / f"{args.name}_{index}{suffix}"
        fal.download(item["url"], target)
        saved.append(rel(project, target))
    if (project / ".gf").is_dir():
        fal.record(project, args.endpoint, None, unit, args.estimate_usd, saved, arguments.get("prompt"))
    return ok(endpoint=args.endpoint, files=saved, unit=unit, cost_usd=args.estimate_usd, result=result)


def register(sub) -> None:
    p = sub.add_parser("fal", help="fal 모델 검색·단가·스키마·호출")
    s = p.add_subparsers(dest="cmd", required=True)
    q = s.add_parser("search")
    q.add_argument("query")
    q.add_argument("--limit", type=int, default=20)
    q.set_defaults(func=search)
    q = s.add_parser("price")
    q.add_argument("endpoint", nargs="+")
    q.set_defaults(func=price)
    q = s.add_parser("schema")
    q.add_argument("endpoint")
    q.set_defaults(func=schema)
    q = s.add_parser("run", help="임의 모델을 호출하고 결과 파일을 내려받는다")
    q.add_argument("endpoint")
    q.add_argument("--args", default="{}", help="입력 JSON")
    q.add_argument("--upload", action="append", help="필드=로컬파일. 업로드한 URL을 그 필드에 넣는다")
    q.add_argument("--out", default="assets/raw")
    q.add_argument("--name", default="out")
    q.add_argument("--estimate-usd", type=float, help="직접 추정한 비용. 한도와 비교하고 기록에 남긴다")
    q.add_argument("--max-usd", type=float)
    q.add_argument("--allow-unknown-cost", action="store_true", help="비용을 모르는 채로 호출한다 (한도 확인 없음)")
    q.set_defaults(func=run)
