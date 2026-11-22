"""외부에서 가져오기. 개인 정보가 담기지 않는 고정 User-Agent 만 보낸다."""

from urllib.parse import urlparse

import httpx

from gf.core.output import GfError

USER_AGENT = "gameforge-ref/0.1"
MAX_BYTES = 25 * 1024 * 1024
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def client(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        follow_redirects=True,
        transport=transport,
    )


def is_url(text: str) -> bool:
    return urlparse(text).scheme in ("http", "https")


def _check(url: str) -> None:
    if not is_url(url) or not urlparse(url).hostname:
        raise GfError(f"http(s) 주소만 가져올 수 있다: {url}")


def get_bytes(http: httpx.Client, url: str, *, referer: str | None = None) -> bytes:
    _check(url)
    headers = {"Referer": referer} if referer and is_url(referer) else {}
    chunks: list[bytes] = []
    size = 0
    try:
        with http.stream("GET", url, headers=headers) as response:
            if response.status_code != 200:
                raise GfError(f"가져오기 실패 (HTTP {response.status_code}): {url}")
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > MAX_BYTES:
                    raise GfError(f"파일이 너무 크다 (>{MAX_BYTES // 1024 // 1024}MB): {url}")
                chunks.append(chunk)
    except httpx.HTTPError as exc:
        raise GfError(f"가져오기 실패 ({type(exc).__name__}): {url}") from exc
    return b"".join(chunks)


def get_json(http: httpx.Client, url: str, params: dict) -> dict:
    _check(url)
    try:
        response = http.get(url, params=params)
    except httpx.HTTPError as exc:
        raise GfError(f"요청 실패 ({type(exc).__name__}): {url}") from exc
    if response.status_code != 200:
        raise GfError(f"요청 실패 (HTTP {response.status_code}): {url}")
    try:
        return response.json()
    except ValueError as exc:
        raise GfError(f"JSON 이 아닌 응답이다: {url}") from exc
