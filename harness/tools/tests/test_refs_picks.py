import io
import json

import pytest
from PIL import Image

from gf import cli
from gf.refs import picks, sheet, store


def png(colour) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (64, 36), colour).save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".gf").mkdir()
    return tmp_path


def add(project, index, **fields) -> str:
    return store.add(project, png((index, index, index)), origin="manual", **fields)[0]["file"]


def run(project, capsys, *argv) -> tuple[int, dict]:
    code = cli.main(["--project", str(project), *argv])
    return code, json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_pick_copies_image_and_metadata(project):
    file = add(project, 1, title="게임 A")
    item = picks.set_item(project, file, picked=True, note="조명만")
    assert item["picked"]
    picked = store.picked(project)
    assert (picked / file).read_bytes() == (store.inbox(project) / file).read_bytes()
    meta = store.get(picked, file)
    assert meta["note"] == "조명만"
    assert meta["picked_at"]
    assert store.get(store.inbox(project), file)["note"] == "조명만"


def test_changing_a_picked_item_updates_the_copy(project):
    file = add(project, 1)
    picks.set_item(project, file, picked=True)
    picks.set_item(project, file, kind="anti", note="너무 어둡다")
    meta = store.get(store.picked(project), file)
    assert (meta["kind"], meta["note"]) == ("anti", "너무 어둡다")


def test_changing_an_unpicked_item_does_not_pick_it(project):
    file = add(project, 1)
    item = picks.set_item(project, file, note="메모만")
    assert not item["picked"]
    assert picks.picked_files(project) == set()


def test_unpick_removes_copy_and_index_entry(project):
    first, second = add(project, 1), add(project, 2)
    picks.set_item(project, first, picked=True)
    picks.set_item(project, second, picked=True)
    picks.set_item(project, first, picked=False)
    index = picks.write_index(project)
    assert [entry["file"] for entry in index["picks"]] == [second]
    assert not (store.picked(project) / first).exists()
    assert (store.inbox(project) / first).exists()


def test_index_counts_kinds_and_is_written(project):
    first, second = add(project, 1), add(project, 2)
    picks.set_item(project, first, picked=True, note="팔레트")
    picks.set_item(project, second, picked=True, kind="anti")
    index = picks.write_index(project)
    assert (index["reference"], index["anti"]) == (1, 1)
    assert json.loads((store.picked(project) / picks.INDEX).read_text()) == index
    assert index["picks"][0]["note"] == "팔레트"


def test_dominance_warns_when_one_title_dominates(project):
    for index in range(4):
        picks.set_item(project, add(project, index, title="게임 A"), picked=True)
    picks.set_item(project, add(project, 10, title="게임 B"), picked=True)
    warning = picks.write_index(project)["warnings"][0]
    assert (warning["by"], warning["name"], warning["count"], warning["total"]) == (
        "title",
        "게임 A",
        4,
        5,
    )
    assert "게임 A" in warning["message"]


def test_dominance_uses_domain_when_there_is_no_title(project):
    for index in range(3):
        url = f"https://www.example.com/{index}"
        picks.set_item(project, add(project, index, source_url=url), picked=True)
    warning = picks.write_index(project)["warnings"][0]
    assert (warning["by"], warning["name"]) == ("domain", "example.com")


def test_no_warning_for_mixed_sources_few_picks_or_anti(project):
    for index, title in enumerate(["A", "A", "B", "C"]):
        picks.set_item(project, add(project, index, title=title), picked=True)
    assert picks.write_index(project)["warnings"] == []
    for index in range(10, 15):
        picks.set_item(project, add(project, index, title="A"), picked=True, kind="anti")
    assert picks.write_index(project)["warnings"] == []


def test_two_picks_from_one_title_do_not_warn(project):
    for index in range(2):
        picks.set_item(project, add(project, index, title="A"), picked=True)
    assert picks.write_index(project)["warnings"] == []


def test_cli_pick_and_unpick_by_sheet_number(project, capsys):
    files = [add(project, index, title="게임 A") for index in range(4)]
    sheet.build(project, "inbox")
    code, out = run(project, capsys, "ref", "pick", "1", "2", "3", "--note", "색감")
    assert code == 0 and out["ok"]
    assert out["reference"] == 3
    assert out["warnings"][0]["name"] == "게임 A"
    assert out["files"] == [f"references/picked/{name}" for name in files[:3]]

    code, out = run(project, capsys, "ref", "pick", "4", "--anti")
    assert (out["reference"], out["anti"]) == (3, 1)

    code, out = run(project, capsys, "ref", "unpick", "2")
    assert code == 0 and out["reference"] == 2 and out["warnings"] == []

    code, out = run(project, capsys, "ref", "unpick", "2")
    assert code == 1 and not out["ok"] and "고르지 않은" in out["error"]

    code, out = run(project, capsys, "ref", "unpick", "--all")
    assert (out["reference"], out["anti"]) == (0, 0)


def test_cli_status_counts(project, capsys):
    add(project, 1)
    store.add(project, png("red"), origin="steam", kind="anti")
    code, out = run(project, capsys, "ref", "status")
    assert code == 0
    assert out["inbox"] == {
        "count": 2,
        "by_origin": {"manual": 1, "steam": 1},
        "by_kind": {"reference": 1, "anti": 1},
    }
    assert "server" not in out and "token_file" not in out["paths"]


def test_cli_requires_a_gameforge_project(tmp_path, capsys):
    code, out = run(tmp_path, capsys, "ref", "status")
    assert code == 1 and "gf init" in out["error"]
