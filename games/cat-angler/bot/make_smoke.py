"""정책 봇의 기록(trace.jsonl)에서 고정 입력 스크립트 bot/smoke.json 을 만든다.

균형이나 배치를 바꿔 스모크가 어긋나면 다시 만든다:
  CA_BOT_STOP=sold gf engine bot --policy bot/full_run.py --seconds 116 --shot-every 200
  python3 bot/make_smoke.py captures/bot/<방금 만든 폴더>/trace.jsonl
스모크: 타이틀 → 새로 시작 → 여는 컷신 건너뛰기 → 채집 → 미끼 공방 → 부두 → 출항 → 닻 → 낚시 → 귀항 → 어시장에서 팔기.
"""

import json
import sys
from pathlib import Path

trace = Path(sys.argv[1])
seed = 0
actions = []
for line in trace.read_text().splitlines():
    entry = json.loads(line)
    if entry["type"] == "header":
        seed = entry.get("seed", 0)
    elif entry["type"] == "input":
        for name in entry["actions"]:
            actions.append({"t": round(entry["t"], 4), "press" if entry["down"] else "release": name})
out = Path(__file__).with_name("smoke.json")
out.write_text(json.dumps({"seed": seed, "actions": actions}, ensure_ascii=False, indent=1) + "\n")
print(f"{out}: 입력 {len(actions)}개, 시드 {seed}, 마지막 입력 {actions[-1]['t']}초")
