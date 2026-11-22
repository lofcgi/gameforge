import json
from pathlib import Path

from gf.core.paths import gf_dir
from gf.core.state import now


def record(project: Path, **entry) -> None:
    line = json.dumps({"at": now(), **entry}, ensure_ascii=False)
    with (gf_dir(project) / "ledger.jsonl").open("a") as handle:
        handle.write(line + "\n")


def total(project: Path) -> float:
    ledger = gf_dir(project) / "ledger.jsonl"
    if not ledger.is_file():
        return 0.0
    return sum(json.loads(line).get("cost_usd") or 0.0 for line in ledger.read_text().splitlines() if line)


def remember_prompt(project: Path, **entry) -> None:
    """채택된 프롬프트를 이후 생성의 기준으로 남긴다."""
    line = json.dumps({"at": now(), **entry}, ensure_ascii=False)
    with (gf_dir(project) / "prompts.jsonl").open("a") as handle:
        handle.write(line + "\n")
