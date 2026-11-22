import io
import json

import httpx
import pytest
from PIL import Image

from gf.core.output import GfError
from gf.refs import fetch, steam, store, video


def png(colour, size=(64, 36)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".gf").mkdir()
    return tmp_path


def test_add_writes_image_and_metadata(project):
    meta, created = store.add(
        project,
        png("red"),
        origin="manual",
        source_url="https://example.com/a.png",
        page_title="예시",
        note=" 조명만 ",
        tags="밤, 네온,밤",
    )
    assert created
    image = store.inbox(project) / meta["file"]
    assert image.is_file()
    saved = json.loads(image.with_suffix(".json").read_text())
    assert saved == meta
    assert saved["origin"] == "manual"
    assert saved["kind"] == "reference"
    assert saved["note"] == "조명만"
    assert saved["tags"] == ["밤", "네온"]
    assert (saved["width"], saved["height"]) == (64, 36)
    assert len(saved["sha256"]) == 64
    assert saved["captured"]


def test_same_bytes_are_deduplicated(project):
    first, created = store.add(project, png("red"), origin="manual")
    again, created_again = store.add(project, png("red"), origin="steam", note="다른 메모")
    assert created and not created_again
    assert again == first
    assert len(store.items(store.inbox(project))) == 1


def test_rejects_non_image_and_unknown_fields(project):
    with pytest.raises(GfError, match="이미지로 읽을 수 없는"):
        store.add(project, b"<html>not an image</html>", origin="manual")
    with pytest.raises(GfError, match="출처"):
        store.add(project, png("red"), origin="scraper")
    with pytest.raises(GfError, match="종류"):
        store.add(project, png("red"), origin="manual", kind="maybe")
    assert store.items(store.inbox(project)) == []


def test_unsupported_format_is_converted_to_png(project):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "blue").save(buffer, "BMP")
    meta, _ = store.add(project, buffer.getvalue(), origin="manual")
    assert meta["file"].endswith(".png")
    with Image.open(store.inbox(project) / meta["file"]) as image:
        assert image.format == "PNG"


def test_get_rejects_names_with_directories(project):
    with pytest.raises(GfError):
        store.get(store.inbox(project), "../.gf/state.json")


def test_source_key_prefers_title_then_domain():
    assert store.source_key({"title": "어떤 게임", "source_url": "https://a.com/x"}) == (
        "title",
        "어떤 게임",
    )
    assert store.source_key({"source_url": "https://www.a.com/x"}) == ("domain", "a.com")
    assert store.source_key({"source_url": None}) is None


def steam_transport(payload: dict) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"] == fetch.USER_AGENT
        assert "cookie" not in request.headers
        if request.url.host == "store.steampowered.com":
            return httpx.Response(200, json=payload)
        colour = "red" if "one" in request.url.path else "blue"
        return httpx.Response(200, content=png(colour))

    return httpx.MockTransport(handler)


def test_steam_collects_screenshots_with_metadata(project):
    payload = {
        "42": {
            "success": True,
            "data": {
                "name": "Some Game",
                "screenshots": [
                    {"id": 0, "path_full": "https://cdn.example/one.jpg"},
                    {"id": 1, "path_full": "https://cdn.example/two.jpg"},
                    {"id": 2, "path_full": "https://cdn.example/three.jpg"},
                ],
            },
        }
    }
    with fetch.client(steam_transport(payload)) as http:
        result = steam.collect(project, http, 42, limit=2)
    assert len(result["added"]) == 2
    metas = store.items(store.inbox(project))
    assert {meta["title"] for meta in metas} == {"Some Game"}
    assert {meta["appid"] for meta in metas} == {42}
    assert metas[0]["source_url"] == "https://store.steampowered.com/app/42/"
    assert metas[0]["origin"] == "steam"


def test_steam_reports_missing_or_gated_app(project):
    gated = steam_transport({"7": {"success": False}})
    with fetch.client(gated) as http, pytest.raises(GfError, match="연령 확인"):
        steam.collect(project, http, 7, limit=3)
    payload = {"7": {"success": True, "data": {"name": "빈 게임"}}}
    empty = steam_transport(payload)
    with fetch.client(empty) as http, pytest.raises(GfError, match="스크린샷이 없다"):
        steam.collect(project, http, 7, limit=3)


def test_steam_appid_parsing():
    assert steam.parse_appid("620") == 620
    assert steam.parse_appid("https://store.steampowered.com/app/620/Some_Name/") == 620
    with pytest.raises(GfError):
        steam.parse_appid("https://example.com/app/620")


def test_fetch_refuses_non_http_and_http_errors():
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    with fetch.client(transport) as http:
        with pytest.raises(GfError, match="http"):
            fetch.get_bytes(http, "file:///etc/passwd")
        with pytest.raises(GfError, match="404"):
            fetch.get_bytes(http, "https://example.com/missing.png")


def test_frame_timestamps_use_segment_midpoints():
    assert video.timestamps(100, every=None, count=4, limit=40) == [12.5, 37.5, 62.5, 87.5]
    assert video.timestamps(100, every=30, count=None, limit=40) == [15, 45, 75]
    assert video.timestamps(100, every=1, count=None, limit=5) == [0.5, 1.5, 2.5, 3.5, 4.5]
    with pytest.raises(GfError):
        video.timestamps(100, every=0, count=None, limit=5)


def test_ref_add_reads_local_paths_relative_to_the_project(tmp_path, capsys, monkeypatch, tmp_path_factory):
    """다른 gf 명령처럼 상대 경로는 현재 폴더가 아니라 게임 프로젝트 기준이다."""
    import json

    from PIL import Image

    from gf import cli

    (tmp_path / ".gf").mkdir()
    (tmp_path / "assets").mkdir()
    Image.new("RGB", (64, 48), (40, 120, 200)).save(tmp_path / "assets" / "shot.png")
    monkeypatch.chdir(tmp_path_factory.mktemp("elsewhere"))
    assert cli.main(["--project", str(tmp_path), "ref", "add", "assets/shot.png"]) == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert len(out["added"]) == 1


def test_cli_add_records_image_url_and_source_page(project, capsys, monkeypatch):
    from gf import cli

    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["referer"] = request.headers.get("referer")
        return httpx.Response(200, content=png("green"))

    real_client = fetch.client
    monkeypatch.setattr(fetch, "client", lambda: real_client(httpx.MockTransport(handler)))
    code = cli.main(
        [
            "--project", str(project), "ref", "add", "https://cdn.example/736x/a.jpg",
            "--source-url", "https://board.example/pin/1/", "--title", "어떤 작가",
            "--note", "팔레트",
        ]
    )  # fmt: skip
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert code == 0 and len(out["added"]) == 1
    (meta,) = store.items(store.inbox(project))
    assert meta["image_url"] == "https://cdn.example/736x/a.jpg"
    assert meta["source_url"] == "https://board.example/pin/1/"
    assert meta["title"] == "어떤 작가"
    assert seen["referer"] == "https://board.example/pin/1/"


def test_cli_add_without_source_page_keeps_image_url_as_source(project, capsys, monkeypatch):
    from gf import cli

    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=png("green")))
    real_client = fetch.client
    monkeypatch.setattr(fetch, "client", lambda: real_client(transport))
    assert cli.main(["--project", str(project), "ref", "add", "https://cdn.example/a.jpg"]) == 0
    capsys.readouterr()
    (meta,) = store.items(store.inbox(project))
    assert meta["source_url"] == meta["image_url"] == "https://cdn.example/a.jpg"
    assert meta["title"] is None

    code = cli.main(
        ["--project", str(project), "ref", "add", "https://cdn.example/b.jpg",
         "--source-url", "not-a-url"]
    )  # fmt: skip
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert code == 1 and "--source-url" in out["error"]
