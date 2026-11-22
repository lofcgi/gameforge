"""모델의 입력 스키마와 단가. 플랫폼 API 가 429 를 자주 내므로 프로젝트의 .gf/cache/ 에 둔다."""

import json
import time
from pathlib import Path

from gf.core import fal
from gf.core.fal_commands import summarize_schema
from gf.core.output import GfError
from gf.core.paths import gf_dir

TTL_SECONDS = 24 * 3600


def cache_path(project: Path, endpoint: str) -> Path:
    return gf_dir(project) / "cache" / "fal" / (endpoint.replace("/", "__") + ".json")


def describe(project: Path, endpoint: str, refresh: bool = False) -> dict:
    """{"endpoint", "input": 필드 요약, "price": 단가} 를 돌려준다."""
    path = cache_path(project, endpoint)
    if path.is_file() and not refresh:
        cached = json.loads(path.read_text())
        if time.time() - cached["fetched"] < TTL_SECONDS:
            return cached
    fields = summarize_schema(fal.schema(endpoint))
    if not fields:
        raise GfError(f"{endpoint} 의 입력 스키마를 읽지 못했다. `gf fal schema {endpoint}` 로 확인한다.")
    info = {"endpoint": endpoint, "fetched": time.time(), "input": fields, "price": fal.price(endpoint)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n")
    return info
