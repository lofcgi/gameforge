"""기본 모델들의 실제 스키마(2026-11-22 에 받은 요약, tests/fixtures/schemas)로 인자 맞추기를 검증한다."""

import argparse
import json
import time
from pathlib import Path

import pytest

from gf.core import fal
from gf.core.output import GfError
from gf.gen import commands, cost, mapping
from gf.gen.mapping import Upload

FIXTURES = Path(__file__).parent / "fixtures" / "schemas"


def fixture(endpoint: str) -> dict:
    return json.loads((FIXTURES / (endpoint.replace("/", "__") + ".json")).read_text())


def build(endpoint: str, semantic: dict, direct: dict | None = None, extra: dict | None = None) -> dict:
    return mapping.build(endpoint, fixture(endpoint)["input"], semantic, direct or {}, extra or {})


def estimate(endpoint: str, arguments: dict):
    info = fixture(endpoint)
    return cost.estimate(info["price"], cost.usage(info["input"], arguments))


PNG = Upload(Path("a.png"))
GLB = Upload(Path("a.glb"))


def test_image_concept():
    endpoint = "fal-ai/nano-banana-2"
    arguments = build(endpoint, {"prompt": "a knight", "image": []}, {"aspect_ratio": "1:1", "resolution": "0.5K", "num_images": 2})
    assert arguments == {"prompt": "a knight", "aspect_ratio": "1:1", "resolution": "0.5K", "num_images": 2}
    assert estimate(endpoint, arguments)[0] == 0.16


def test_image_concept_has_no_reference_field():
    with pytest.raises(GfError, match="'image' 입력을 넣을 필드가 없다") as error:
        build("fal-ai/nano-banana-2", {"prompt": "x", "image": [PNG]})
    assert "prompt*" in str(error.value)


def test_image_edit_takes_list():
    arguments = build("fal-ai/nano-banana-2/edit", {"prompt": "make it blue", "image": [PNG, PNG]})
    assert arguments == {"prompt": "make it blue", "image_urls": [PNG, PNG]}
    assert estimate("fal-ai/nano-banana-2/edit", arguments)[0] == 0.08


def test_rembg_takes_single_image_and_cost_is_unknown():
    arguments = build("fal-ai/birefnet/v2", {"image": [PNG]})
    assert arguments == {"image_url": PNG}
    estimated, note = estimate("fal-ai/birefnet/v2", arguments)
    assert estimated is None and "compute seconds" in note


def test_single_image_field_rejects_several():
    with pytest.raises(GfError, match="하나만"):
        build("fal-ai/birefnet/v2", {"image": [PNG, PNG]})


def test_video_sprite_duration_is_string_enum():
    endpoint = "fal-ai/kling-video/v3/turbo/standard/image-to-video"
    arguments = build(endpoint, {"prompt": "walk", "image": [PNG], "end_image": [], "duration": 3.0})
    assert arguments == {"prompt": "walk", "image_url": PNG, "duration": "3"}
    assert estimate(endpoint, arguments)[0] == 0.336
    assert estimate(endpoint, {"image_url": PNG})[0] == 0.56
    with pytest.raises(GfError, match="가능한 값"):
        build(endpoint, {"image": [PNG], "duration": 2})
    with pytest.raises(GfError, match="end_image"):
        build(endpoint, {"image": [PNG], "end_image": [PNG]})


def test_video_look_token_price_is_not_converted():
    endpoint = "bytedance/seedance-2.5/image-to-video"
    arguments = build(
        endpoint,
        {"prompt": "pan", "image": [PNG], "end_image": [PNG], "duration": 4},
        {"resolution": "480p", "generate_audio": False},
    )
    assert arguments == {
        "prompt": "pan",
        "image_url": PNG,
        "end_image_url": PNG,
        "duration": "4",
        "resolution": "480p",
        "generate_audio": False,
    }
    estimated, note = estimate(endpoint, arguments)
    assert estimated is None and "1000 tokens" in note
    with pytest.raises(GfError, match="가능한 값"):
        build(endpoint, {"image": [PNG]}, {"resolution": "240p"})


def test_model3d_options():
    endpoint = "tripo3d/p2/image-to-3d"
    arguments = build(endpoint, {"image": [PNG]}, {"face_limit": 5000, "pbr": False, "quad": None, "texture": True})
    assert arguments == {"image_url": PNG, "face_limit": 5000, "pbr": False, "texture": True}
    assert estimate(endpoint, arguments)[0] is None


def test_rig():
    endpoint = "fal-ai/meshy/rigging"
    arguments = build(endpoint, {"model": [GLB]}, {"height_meters": 1.8, "enable_animation": True})
    assert arguments == {"model_url": GLB, "height_meters": 1.8, "enable_animation": True}
    assert estimate(endpoint, arguments) == (0.8, None)


def test_sfx_prompt_goes_to_text():
    endpoint = "elevenlabs/sound-effects/v3"
    arguments = build(endpoint, {"prompt": "coin pickup", "duration": 1}, {"loop": None})
    assert arguments == {"text": "coin pickup", "duration_seconds": 1.0}
    assert estimate(endpoint, arguments)[0] == 0.002
    estimated, note = estimate(endpoint, {"text": "coin pickup"})
    assert estimated is None and "길이" in note


def test_tts_cost_by_characters():
    endpoint = "fal-ai/elevenlabs/tts/eleven-v3"
    arguments = build(endpoint, {"prompt": "x" * 250}, {"voice": "Rachel"})
    assert arguments == {"text": "x" * 250, "voice": "Rachel"}
    assert estimate(endpoint, arguments) == (0.025, None)


def test_music_duration_in_milliseconds():
    endpoint = "elevenlabs/music/v2.5"
    arguments = build(endpoint, {"prompt": "calm loop", "duration": 10}, {"force_instrumental": True})
    assert arguments == {"prompt": "calm loop", "music_length_ms": 10000, "force_instrumental": True}
    assert estimate(endpoint, arguments)[0] == 0.1


def test_unknown_direct_field_lists_real_fields():
    with pytest.raises(GfError, match="'face_limit' 필드가 없다"):
        build("fal-ai/birefnet/v2", {"image": [PNG]}, {"face_limit": 100})


def test_missing_required_field():
    with pytest.raises(GfError, match="필수 필드가 비었다: image_url"):
        build("fal-ai/birefnet/v2", {})


def test_extra_args_pass_through_and_must_exist():
    arguments = build("fal-ai/birefnet/v2", {"image": [PNG]}, extra={"model": "Matting"})
    assert arguments["model"] == "Matting"
    with pytest.raises(GfError, match="'nope' 필드가 없다"):
        build("fal-ai/birefnet/v2", {"image": [PNG]}, extra={"nope": 1})


def test_parse_extra():
    assert mapping.parse_extra("refine_foreground=false", Path) == ("refine_foreground", False)
    assert mapping.parse_extra("model=General Use (Heavy)", Path) == ("model", "General Use (Heavy)")
    assert mapping.parse_extra("mask_url=@m.png", Path) == ("mask_url", Upload(Path("m.png")))
    with pytest.raises(GfError):
        mapping.parse_extra("oops", Path)


def test_range_check():
    with pytest.raises(GfError, match="범위"):
        build("fal-ai/nano-banana-2", {"prompt": "x"}, {"num_images": 9})


# --- 명령 전체 흐름 (네트워크 없이: 캐시에 스키마를 심고 fal 호출을 바꿔 끼운다) ---


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("FAL_KEY", "test-key")
    cache = tmp_path / ".gf" / "cache" / "fal"
    cache.mkdir(parents=True)
    for path in FIXTURES.glob("*.json"):
        info = json.loads(path.read_text())
        info["fetched"] = time.time()
        (cache / path.name).write_text(json.dumps(info))
    monkeypatch.setattr(fal, "schema", lambda endpoint: pytest.fail("네트워크로 스키마를 받으려 했다"))
    monkeypatch.setattr(fal, "run", lambda *a, **k: pytest.fail("fal 을 호출하려 했다"))
    return tmp_path


def run(project, *argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(project))
    commands.register(parser.add_subparsers(dest="group"))
    args = parser.parse_args(["gen", *argv])
    return args.func(args)


def last_json(capsys) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_dry_run_prints_endpoint_arguments_and_cost(project, capsys):
    (project / "hero.png").write_bytes(b"png")
    assert run(project, "video", "hero.png", "--prompt", "walk cycle", "--duration", "3", "--dry-run") == 0
    result = last_json(capsys)
    assert result["ok"] and result["dry_run"] and result["files"] == []
    assert result["endpoint"] == "fal-ai/kling-video/v3/turbo/standard/image-to-video"
    assert result["arguments"] == {"prompt": "walk cycle", "image_url": "<upload:hero.png>", "duration": "3"}
    assert result["cost_usd"] == 0.336
    assert result["unit"]["unit"] == "seconds"
    assert not (project / ".gf" / "ledger.jsonl").exists()


def test_dry_run_reports_null_cost_with_reason(project, capsys):
    (project / "hero.png").write_bytes(b"png")
    assert run(project, "model3d", "hero.png", "--face-limit", "3000", "--no-pbr", "--dry-run") == 0
    result = last_json(capsys)
    assert result["cost_usd"] is None and "credits" in result["cost_note"]
    assert result["arguments"] == {"image_url": "<upload:hero.png>", "face_limit": 3000, "pbr": False}


def test_image_with_refs_points_to_edit(project):
    (project / "ref.png").write_bytes(b"png")
    with pytest.raises(GfError, match=r"gf gen edit .*--image"):
        run(project, "image", "a knight", "--ref", "ref.png", "--dry-run")


def test_missing_input_file(project):
    with pytest.raises(GfError, match="입력 파일이 없다"):
        run(project, "rembg", "nope.png", "--dry-run")


def test_budget_guard_stops_before_calling(project):
    with pytest.raises(GfError, match="한도"):
        run(project, "image", "a knight", "--count", "4", "--max-usd", "0.1")


def test_config_override_and_model_flag(project, capsys):
    (project / ".gf" / "config.toml").write_text('[roles]\n"audio.sfx" = "elevenlabs/music/v2.5"\n')
    assert run(project, "sfx", "boom", "--duration", "6", "--dry-run") == 0
    result = last_json(capsys)
    assert result["endpoint"] == "elevenlabs/music/v2.5"
    assert result["arguments"] == {"prompt": "boom", "music_length_ms": 6000}
    assert run(project, "sfx", "boom", "--model", "elevenlabs/sound-effects/v3", "--dry-run") == 0
    assert last_json(capsys)["arguments"] == {"text": "boom"}


def test_full_run_downloads_records_and_keeps_prompt(project, capsys, monkeypatch):
    calls = {}

    def fake_run(endpoint, arguments, log=None):
        calls["run"] = (endpoint, arguments)
        return {"images": [{"url": "https://cdn.test/a.png"}, {"url": "https://cdn.test/b", "content_type": "image/png"}]}

    def fake_download(url, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")
        return target

    monkeypatch.setattr(fal, "upload", lambda path: f"https://cdn.test/up/{path.name}")
    monkeypatch.setattr(fal, "run", fake_run)
    monkeypatch.setattr(fal, "download", fake_download)
    (project / "in.png").write_bytes(b"png")

    assert run(project, "edit", "make it red", "--image", "in.png", "--count", "2", "--name", "hero", "--keep") == 0
    result = last_json(capsys)
    assert calls["run"] == (
        "fal-ai/nano-banana-2/edit",
        {"prompt": "make it red", "image_urls": ["https://cdn.test/up/in.png"], "num_images": 2},
    )
    assert result["files"] == ["assets/raw/image/hero_images-0.png", "assets/raw/image/hero_images-1.png"]
    assert result["cost_usd"] == 0.16
    entry = json.loads((project / ".gf" / "ledger.jsonl").read_text())
    assert entry["role"] == "image.edit" and entry["cost_usd"] == 0.16 and entry["files"] == result["files"]
    kept = json.loads((project / ".gf" / "prompts.jsonl").read_text())
    assert kept["prompt"] == "make it red" and kept["arguments"]["image_urls"] == ["<upload:in.png>"]

    with pytest.raises(GfError, match="이미 'hero' 결과가 있다"):
        run(project, "edit", "again", "--image", "in.png", "--name", "hero")


def test_single_result_file_uses_plain_name(project, capsys, monkeypatch):
    monkeypatch.setattr(fal, "upload", lambda path: "https://cdn.test/up")
    monkeypatch.setattr(fal, "run", lambda *a, **k: {"image": {"url": "https://cdn.test/cut.png"}})
    monkeypatch.setattr(fal, "download", lambda url, target: target)
    (project / "in.png").write_bytes(b"png")
    assert run(project, "rembg", "in.png", "--name", "cut", "--allow-unknown-cost") == 0
    result = last_json(capsys)
    assert result["files"] == ["assets/raw/image/cut.png"]
    assert result["cost_usd"] is None


def test_unknown_cost_needs_estimate_or_explicit_flag(project, capsys, monkeypatch):
    called = []
    monkeypatch.setattr(fal, "upload", lambda path: "https://cdn.test/up")
    monkeypatch.setattr(fal, "run", lambda *a, **k: called.append(a) or {"image": {"url": "https://cdn.test/cut.png"}})
    monkeypatch.setattr(fal, "download", lambda url, target: target)
    (project / "in.png").write_bytes(b"png")
    with pytest.raises(GfError, match="--estimate-usd.*--allow-unknown-cost"):
        run(project, "rembg", "in.png", "--name", "a")
    assert not called
    with pytest.raises(GfError, match="한도"):
        run(project, "rembg", "in.png", "--name", "a", "--estimate-usd", "5")
    assert not called
    assert run(project, "rembg", "in.png", "--name", "a", "--estimate-usd", "0.01") == 0
    assert last_json(capsys)["cost_usd"] == 0.01 and len(called) == 1


def test_end_image_on_sprite_role_points_to_look_role_and_loop(project):
    (project / "hero.png").write_bytes(b"png")
    with pytest.raises(GfError, match=r"--role video\.look.*gf post loop"):
        run(project, "video", "hero.png", "--end-image", "hero.png", "--duration", "3", "--dry-run")


def test_schema_summary_lifts_enum_out_of_any_of():
    """nano-banana-2 의 aspect_ratio 는 enum 이 anyOf 안에 있다. 놓치면 틀린 값이 유료 호출까지 간다."""
    from gf.core.fal_commands import summarize_schema

    model = {"openapi": {
        "paths": {"/": {"post": {"requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/In"}}}}}}},
        "components": {"schemas": {"In": {"properties": {
            "aspect_ratio": {"anyOf": [{"enum": ["auto", "1:1", "9:16"], "type": "string"}, {"type": "null"}], "default": "auto"},
        }}}},
    }}
    fields = summarize_schema(model)
    assert fields["aspect_ratio"]["enum"] == ["auto", "1:1", "9:16"]
    with pytest.raises(GfError, match="가능한 값"):
        mapping.coerce("aspect_ratio", fields["aspect_ratio"], "1:2")
    assert mapping.coerce("aspect_ratio", fields["aspect_ratio"], "9:16") == "9:16"
