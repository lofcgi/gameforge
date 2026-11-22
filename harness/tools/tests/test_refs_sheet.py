import io
import json

import pytest
from PIL import Image

from gf.core.output import GfError
from gf.refs import picks, sheet, store


def png(colour) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (64, 36), colour).save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".gf").mkdir()
    return tmp_path


def fill(project, count):
    return [
        store.add(project, png((index, 0, 255 - index)), origin="manual")[0]["file"]
        for index in range(count)
    ]


def test_sheet_paginates_and_numbers_in_capture_order(project):
    files = fill(project, 23)
    index = sheet.build(project, "inbox")
    assert index["pages"] == ["references/sheets/inbox-01.png", "references/sheets/inbox-02.png"]
    assert [entry["n"] for entry in index["items"]] == list(range(1, 24))
    assert [entry["file"] for entry in index["items"]] == files
    assert [entry["page"] for entry in index["items"]] == [1] * 20 + [2] * 3
    saved = json.loads(sheet.index_path(project, "inbox").read_text())
    assert saved == index
    with Image.open(project / index["pages"][0]) as page:
        assert page.size == (5 * 376 + 8, 4 * 224 + 8)


def test_sheet_draws_each_thumbnail_in_its_slot(project):
    store.add(project, png((255, 0, 0)), origin="manual")
    store.add(project, png((0, 0, 255)), origin="manual")
    index = sheet.build(project, "inbox")
    with Image.open(project / index["pages"][0]) as page:
        centre_y = 8 + 216 // 2
        assert page.getpixel((8 + 184, centre_y)) == (255, 0, 0)
        assert page.getpixel((8 + 376 + 184, centre_y)) == (0, 0, 255)
        assert page.getpixel((8 + 2 * 376 + 184, centre_y)) == sheet.BACKGROUND


def test_rebuilding_removes_stale_pages(project):
    files = fill(project, 21)
    sheet.build(project, "inbox")
    image = store.inbox(project) / files[-1]
    image.unlink()
    image.with_suffix(".json").unlink()
    index = sheet.build(project, "inbox")
    assert len(index["pages"]) == 1
    assert not (sheet.sheets_dir(project) / "inbox-02.png").exists()


def test_empty_set_is_an_error(project):
    with pytest.raises(GfError, match="비어 있다"):
        sheet.build(project, "inbox")


def test_numbers_resolve_against_the_sheet_the_user_saw(project):
    files = fill(project, 3)
    with pytest.raises(GfError, match="먼저 gf ref sheet"):
        sheet.resolve(project, "inbox", [1])
    sheet.build(project, "inbox")
    store.add(project, png("white"), origin="manual")
    assert sheet.resolve(project, "inbox", [3, 1, 3]) == [files[2], files[0]]
    with pytest.raises(GfError, match="없는 번호: 4"):
        sheet.resolve(project, "inbox", [4])


def test_sheet_index_marks_picked_and_anti(project):
    files = fill(project, 3)
    picks.set_item(project, files[0], picked=True)
    picks.set_item(project, files[1], picked=True, kind="anti")
    index = sheet.build(project, "inbox")
    assert [(entry["picked"], entry["kind"]) for entry in index["items"]] == [
        (True, "reference"),
        (True, "anti"),
        (False, "reference"),
    ]
    picked_index = sheet.build(project, "picked")
    assert [entry["file"] for entry in picked_index["items"]] == files[:2]
