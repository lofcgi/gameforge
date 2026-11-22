"""Steam 상점의 공개 appdetails API 에서 스크린샷을 가져온다."""

import re
from pathlib import Path

import httpx

from gf.core.output import GfError
from gf.refs import fetch, store

API = "https://store.steampowered.com/api/appdetails"


def parse_appid(text: str) -> int:
    if text.isdigit():
        return int(text)
    match = re.search(r"store\.steampowered\.com/app/(\d+)", text)
    if not match:
        raise GfError(f"appid 숫자나 store.steampowered.com/app/<id> 주소가 아니다: {text}")
    return int(match.group(1))


def store_url(appid: int) -> str:
    return f"https://store.steampowered.com/app/{appid}/"


def details(http: httpx.Client, appid: int) -> dict:
    payload = fetch.get_json(http, API, {"appids": appid, "l": "english"})
    entry = payload.get(str(appid)) if isinstance(payload, dict) else None
    if not entry or not entry.get("success"):
        raise GfError(
            f"Steam 앱 {appid} 정보를 받을 수 없다. "
            "없는 앱이거나, 지역 제한 또는 연령 확인이 필요한 앱이다."
        )
    data = entry["data"]
    if not data.get("screenshots"):
        raise GfError(f"Steam 앱 {appid} ({data.get('name')}) 에는 공개 스크린샷이 없다.")
    return data


def collect(project: Path, http: httpx.Client, appid: int, limit: int) -> dict:
    data = details(http, appid)
    added, duplicates = [], []
    for shot in data["screenshots"][:limit]:
        image = fetch.get_bytes(http, shot["path_full"])
        meta, created = store.add(
            project,
            image,
            origin="steam",
            source_url=store_url(appid),
            page_title=data["name"],
            title=data["name"],
            extra={"appid": appid, "screenshot_id": shot.get("id")},
        )
        (added if created else duplicates).append(meta["file"])
    return {"title": data["name"], "appid": appid, "added": added, "duplicates": duplicates}
