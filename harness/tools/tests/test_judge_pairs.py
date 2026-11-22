import json

import pytest
from PIL import Image

from gf import cli
from gf.core.output import GfError
from gf.judge import pairs

RED, BLUE, GREEN = (255, 0, 0), (0, 0, 255), (0, 255, 0)


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".gf").mkdir()
    return tmp_path


@pytest.fixture
def shots(tmp_path):
    before, after, target = (tmp_path / name for name in ("before.png", "after.png", "look.png"))
    Image.new("RGB", (320, 180), RED).save(before)
    Image.new("RGB", (640, 360), BLUE).save(after)
    Image.new("RGB", (400, 400), GREEN).save(target)
    return before, after, target


def colour_of(path):
    with Image.open(path) as image:
        return image.getpixel((image.width // 2, image.height // 2))


def secret(project, pair_id):
    return json.loads(pairs.secret_path(project, pair_id).read_text())


def run(project, capsys, *argv):
    code = cli.main(["--project", str(project), *argv])
    return code, json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_pair_writes_neutral_same_size_images(project, shots):
    before, after, target = shots
    result = pairs.create(project, "r1", before, after, target=target)
    folder = project / "captures" / "judge" / "r1"
    assert sorted(path.name for path in folder.iterdir()) == [
        "X.png",
        "Y.png",
        "rubric.md",
        "target.png",
    ]
    sizes = {Image.open(folder / name).size for name in ("X.png", "Y.png", "target.png")}
    assert sizes == {(320, 180)}
    assert result["size"] == [320, 180]
    assert result["aspect_mismatch"] is True
    assert colour_of(folder / "target.png") == GREEN
    assert "블라인드" in (folder / "rubric.md").read_text()


def test_mapping_matches_what_was_written(project, shots):
    before, after, _ = shots
    pairs.create(project, "r1", before, after)
    folder = pairs.pair_dir(project, "r1")
    mapping = secret(project, "r1")["mapping"]
    expected = {"a": RED, "b": BLUE}
    assert colour_of(folder / "X.png") == expected[mapping["X"]]
    assert colour_of(folder / "Y.png") == expected[mapping["Y"]]
    assert sorted(mapping.values()) == ["a", "b"]


def test_order_is_randomised(project, shots):
    before, after, _ = shots
    seen = set()
    for index in range(40):
        pairs.create(project, f"r{index}", before, after)
        seen.add(secret(project, f"r{index}")["mapping"]["X"])
    assert seen == {"a", "b"}


def test_judge_folder_and_output_do_not_reveal_the_mapping(project, shots, capsys):
    before, after, _ = shots
    code, out = run(
        project, capsys, "judge", "pair", "--a", str(before), "--b", str(after), "--id", "r1"
    )
    assert code == 0 and out["ok"]
    assert out["judge_reads"] == "captures/judge/r1"
    assert out["judge_must_not_read"] == ".gf/judge"
    assert "mapping" not in out
    printed = json.dumps(out)
    assert "before" not in printed and "after" not in printed

    folder = pairs.pair_dir(project, "r1")
    assert not pairs.secret_path(project, "r1").is_relative_to(folder)
    for path in folder.rglob("*"):
        data = path.read_bytes()
        assert b"before" not in data and b"after.png" not in data
        assert b"mapping" not in data
    for name in ("X.png", "Y.png"):
        with Image.open(folder / name) as image:
            assert not image.info


def test_pair_validation(project, shots):
    before, after, target = shots
    pairs.create(project, "r1", before, after)
    with pytest.raises(GfError, match="이미 있다"):
        pairs.create(project, "r1", before, after)
    with pytest.raises(GfError, match="id"):
        pairs.create(project, "../escape", before, after)
    with pytest.raises(GfError, match="이미지가 없다"):
        pairs.create(project, "r2", before, project / "missing.png")
    with pytest.raises(GfError, match="--target"):
        pairs.create(project, "r3", before, after, target=target, mode="target")
    assert not pairs.pair_dir(project, "r2").exists()


def test_record_resolves_winner_to_the_real_image(project, shots):
    before, after, _ = shots
    pairs.create(project, "r1", before, after, flip=True)
    scores = {"X": {"readability": 8}, "Y": {"readability": 5}}
    result = pairs.record(project, "r1", "X", scores=scores, notes="윤곽이 또렷하다")
    entry = result["entry"]
    assert entry["winner"] == "b"
    assert entry["winner_file"] == str(after)
    assert entry["scores"] == {"b": {"readability": 8}, "a": {"readability": 5}}
    history = pairs.load_history(project)
    assert history == [entry]
    assert secret(project, "r1")["recorded"] is True
    with pytest.raises(GfError, match="이미 기록"):
        pairs.record(project, "r1", "Y")
    with pytest.raises(GfError, match="없다"):
        pairs.record(project, "ghost", "X")


def play(project, shots, pair_id, winner_side, mode="change", series="s"):
    """winner_side: 'a', 'b', 'tie' — 실제 쪽을 정해 두고 그에 맞는 라벨로 기록한다."""
    before, after, _ = shots
    pairs.create(project, pair_id, before, after, mode=mode, series=series, flip=False)
    label = {"a": "X", "b": "Y", "tie": "tie"}[winner_side]
    return pairs.record(project, pair_id, label)["summary"]


def test_change_series_stops_after_two_rounds_without_a_win(project, shots):
    assert play(project, shots, "1", "b")["stop"]["met"] is False
    assert play(project, shots, "2", "tie")["stop"]["met"] is False
    summary = play(project, shots, "3", "a")
    assert summary["stop"]["met"] is True
    assert (summary["wins"], summary["ties"], summary["losses"]) == (1, 1, 1)
    assert play(project, shots, "4", "b")["stop"]["met"] is False


def test_target_series_stops_when_game_beats_target_twice(project, shots):
    assert play(project, shots, "1", "b", mode="target")["stop"]["met"] is False
    assert play(project, shots, "2", "a", mode="target")["stop"]["met"] is False
    assert play(project, shots, "3", "tie", mode="target")["stop"]["met"] is False
    summary = play(project, shots, "4", "b", mode="target")
    assert summary["stop"]["met"] is True
    assert summary["wins"] == 2


def test_series_are_counted_separately(project, shots):
    play(project, shots, "1", "b", series="hero")
    play(project, shots, "2", "b", series="hero")
    summary = play(project, shots, "3", "a", series="ui")
    assert (summary["rounds"], summary["wins"], summary["losses"]) == (1, 0, 1)


def test_cli_record_and_history(project, shots, capsys):
    before, after, _ = shots
    run(
        project,
        capsys,
        "judge",
        "pair",
        "--a",
        str(before),
        "--b",
        str(after),
        "--id",
        "r1",
        "--series",
        "hero",
    )
    loser = next(label for label, side in secret(project, "r1")["mapping"].items() if side == "a")
    code, out = run(
        project, capsys, "judge", "record", "--id", "r1", "--winner", loser,
        "--scores", '{"X": {"cohesion": 6}, "Y": {"cohesion": 6}}', "--notes", "수정 전이 낫다",
    )  # fmt: skip
    assert code == 0
    assert out["winner"] == "a" and out["winner_file"] == str(before)
    assert out["keep_change"] is False
    assert out["counts"] == {"rounds": 1, "wins": 0, "ties": 0, "losses": 1}
    assert out["stop"]["met"] is False
    assert any("지우지 않는다" in rule for rule in out["rules"])

    run(
        project,
        capsys,
        "judge",
        "pair",
        "--a",
        str(before),
        "--b",
        str(after),
        "--id",
        "r2",
        "--series",
        "hero",
    )
    code, out = run(project, capsys, "judge", "record", "--id", "r2", "--winner", "tie")
    assert out["keep_change"] is True and out["stop"]["met"] is True

    code, out = run(project, capsys, "judge", "history", "--series", "hero")
    assert out["series"]["hero"]["rounds"] == 2
    assert [item["id"] for item in out["series"]["hero"]["results"]] == ["r1", "r2"]

    code, out = run(project, capsys, "judge", "history", "--series", "none")
    assert code == 1 and "기록이 없다" in out["error"]

    code, out = run(
        project, capsys, "judge", "record", "--id", "r2", "--winner", "X", "--scores", "{bad"
    )
    assert code == 1 and not out["ok"]


def test_cli_pair_reads_paths_relative_to_the_project(project, shots, capsys, monkeypatch, tmp_path_factory):
    """다른 gf 명령처럼 상대 경로는 현재 폴더가 아니라 게임 프로젝트 기준이다."""
    monkeypatch.chdir(tmp_path_factory.mktemp("elsewhere"))
    code, out = run(project, capsys, "judge", "pair", "--a", "before.png", "--b", "after.png",
                    "--target", "look.png", "--id", "rel")
    assert code == 0 and out["ok"]
