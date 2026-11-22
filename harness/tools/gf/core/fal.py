"""fal 호출. 키는 .env 에서 환경변수로만 로드하고 어디에도 출력하지 않는다."""

import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from gf.core import ledger
from gf.core.output import GfError

PLATFORM = "https://api.fal.ai/v1"


def load_key(start: Path) -> None:
    if os.environ.get("FAL_KEY"):
        return
    for directory in [start, *start.parents]:
        env = directory / ".env"
        if env.is_file():
            load_dotenv(env)
            if os.environ.get("FAL_KEY"):
                return
    raise GfError("FAL_KEY 를 찾지 못했다. 프로젝트나 상위 폴더의 .env 에 FAL_KEY 를 넣는다.")


def _platform_get(path: str, params: Any) -> dict:
    headers = {"Authorization": f"Key {os.environ['FAL_KEY']}"}
    delay = 1.5
    for _ in range(6):
        response = httpx.get(f"{PLATFORM}{path}", params=params, headers=headers, timeout=60)
        if response.status_code == 429:
            time.sleep(delay)
            delay *= 2
            continue
        if response.status_code == 404:
            raise GfError(f"fal 에 없는 모델이다: {params}")
        response.raise_for_status()
        return response.json()
    raise GfError("fal 플랫폼 API 가 계속 429 를 돌려준다. 잠시 뒤 다시 시도한다.")


def search(query: str, limit: int = 20) -> list[dict]:
    data = _platform_get("/models", {"q": query, "limit": limit})
    return [
        {
            "endpoint_id": m.get("endpoint_id"),
            "category": (m.get("metadata") or {}).get("category"),
            "name": (m.get("metadata") or {}).get("display_name"),
            "status": (m.get("metadata") or {}).get("status"),
        }
        for m in data.get("models", [])
    ]


def price(endpoint: str) -> dict:
    data = _platform_get("/models/pricing", {"endpoint_id": endpoint})
    prices = data.get("prices") or []
    if not prices:
        raise GfError(f"{endpoint} 의 단가 정보가 비어 있다.")
    return prices[0]


def schema(endpoint: str) -> dict:
    data = _platform_get("/models", {"endpoint_id": endpoint, "expand": "openapi-3.0"})
    models = data.get("models") or []
    if not models:
        raise GfError(f"fal 에 없는 모델이다: {endpoint}")
    return models[0]


def upload(path: Path) -> str:
    import fal_client

    if not path.is_file():
        raise GfError(f"업로드할 파일이 없다: {path}")
    try:
        return fal_client.upload_file(str(path))
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        raise GfError(f"fal 업로드 실패 ({path.name}): {exc.response.status_code} {detail}") from exc
    except fal_client.client.FalClientError as exc:
        raise GfError(f"fal 업로드 실패 ({path.name}): {exc}") from exc


def run(endpoint: str, arguments: dict, log=None) -> dict:
    import fal_client

    def on_update(update):
        if log and isinstance(update, fal_client.InProgress):
            for entry in update.logs or []:
                log(entry.get("message", ""))

    try:
        return fal_client.subscribe(
            endpoint, arguments=arguments, with_logs=bool(log), on_queue_update=on_update
        )
    except fal_client.client.FalClientError as exc:
        raise GfError(f"fal 호출 실패 ({endpoint}): {exc}") from exc


def download(url: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=300, follow_redirects=True) as response:
        response.raise_for_status()
        with target.open("wb") as handle:
            for chunk in response.iter_bytes():
                handle.write(chunk)
    return target


def extension_for(url: str, content_type: str | None, fallback: str) -> str:
    suffix = Path(url.split("?")[0]).suffix
    if suffix:
        return suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type)
        if guessed:
            return guessed
    return fallback


def guard_budget(
    project: Path, endpoint: str, estimate_usd: float | None, max_usd: float | None, allow_unknown: bool = False
) -> None:
    """추정 비용이 한도 안인지 본다. 추정할 수 없는 호출은 사용자가 명시적으로 허락해야 지나간다."""
    from gf.core import config

    limit = max_usd if max_usd is not None else config.load(project)["budget"]["max_usd_per_call"]
    if estimate_usd is None:
        if allow_unknown:
            return
        raise GfError(
            f"{endpoint} 의 비용을 추정할 수 없어 한도를 확인하지 못한다. "
            "대략의 금액을 --estimate-usd <USD> 로 주거나(한도와 비교한다), "
            "비용을 모르는 채로 호출하려면 --allow-unknown-cost 를 붙인다."
        )
    if estimate_usd > limit:
        raise GfError(
            f"{endpoint} 추정 비용 ${estimate_usd:.2f} 가 한도 ${limit:.2f} 를 넘는다. --max-usd 로 한도를 올린다."
        )


def record(project: Path, endpoint: str, role: str | None, unit_price: dict, cost_usd: float | None, files: list[str], prompt: str | None = None) -> None:
    ledger.record(
        project,
        endpoint=endpoint,
        role=role,
        unit=unit_price.get("unit"),
        unit_price=unit_price.get("unit_price"),
        cost_usd=cost_usd,
        files=files,
        prompt=prompt,
    )
