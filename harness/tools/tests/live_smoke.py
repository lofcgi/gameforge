"""실제 fal 호출 시험. 돈이 든다. pytest 가 모으지 않으며 손으로 실행한다.

    uv run --project <harness>/tools python <harness>/tools/tests/live_smoke.py --project <게임 프로젝트>
    ... --only image,rembg      일부만
    ... --skip video.look,rig   일부 제외
    ... --only rig --model assets/raw/smoke/x.glb   앞 단계 결과를 다시 만들지 않고 이어서

생성기마다 가장 싼 설정으로 한 번씩만 호출한다. 실패해도 다시 시도하지 않는다.
앞 단계의 결과가 필요한 단계(예: rig 는 model3d 의 GLB)는 앞 단계가 실패하면 건너뛴다.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
OUT = "assets/raw/smoke"
CHARACTER = (
    "full-body stylized game character, a small round robot knight with a short cape, standing in a neutral A-pose, "
    "front view, centered, flat solid pure green #00FF00 background, no shadow, no ground, no text"
)

# (이름, gf gen 인자, 호출 한도 USD, 필요한 앞 단계).
# {image}, {model} 은 앞 단계가 만든 파일로 바뀐다.
# video.look 과 model3d 의 단가 단위(tokens, credits)는 환산할 수 없어 --estimate-usd 에 대략의 값을 준다.
STEPS = [
    ("image", ["image", CHARACTER, "--resolution", "0.5K", "--aspect", "1:1"], 0.2, None),
    ("edit", ["edit", "change the cape colour to bright orange, keep everything else", "--image", "{image}", "--resolution", "0.5K"], 0.2, "image"),
    ("rembg", ["rembg", "{image}", "--estimate-usd", "0.01"], 0.1, "image"),
    ("video.sprite", ["video", "{image}", "--role", "video.sprite", "--prompt", "the character walks in place, side to side sway, static camera, background stays flat green", "--duration", "3"], 0.5, "image"),
    ("video.look", ["video", "{image}", "--role", "video.look", "--prompt", "slow camera push-in, the character looks around", "--duration", "4", "--resolution", "480p", "--no-audio", "--estimate-usd", "0.9"], 1.5, "image"),
    ("model3d", ["model3d", "{image}", "--face-limit", "8000", "--no-pbr", "--estimate-usd", "0.5"], 1.0, "image"),
    ("rig", ["rig", "{model}", "--height", "1.2"], 1.0, "model3d"),
    ("sfx", ["sfx", "short bright coin pickup chime", "--duration", "1"], 0.1, None),
    ("tts", ["tts", "Ready."], 0.1, None),
    ("music", ["music", "calm chiptune loop, gentle and warm", "--duration", "5", "--instrumental"], 0.2, None),
]


def gf(project: Path, arguments: list[str]) -> dict:
    command = ["uv", "run", "-q", "--project", str(TOOLS), "gf", "--project", str(project), "gen", *arguments]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    lines = completed.stdout.strip().splitlines()
    if not lines:
        return {"ok": False, "error": completed.stderr.strip()[-400:] or "출력이 없다"}
    return json.loads(lines[-1])


def first_file(result: dict, suffixes: tuple[str, ...]) -> str | None:
    return next((f for f in result.get("files", []) if f.lower().endswith(suffixes)), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True, help="gf init 으로 만든 게임 프로젝트")
    parser.add_argument("--only", help="쉼표로 구분한 단계 이름")
    parser.add_argument("--skip", default="", help="쉼표로 구분한 단계 이름")
    parser.add_argument("--image", help="image 단계를 건너뛰고 쓸 기존 이미지 (프로젝트 기준 경로)")
    parser.add_argument("--model", help="model3d 단계를 건너뛰고 쓸 기존 GLB (프로젝트 기준 경로)")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    only = set(args.only.split(",")) if args.only else {name for name, *_ in STEPS}
    skip = set(args.skip.split(",")) - {""}
    stamp = time.strftime("%H%M%S")
    produced = {name: path for name, path in (("image", args.image), ("model3d", args.model)) if path}
    rows = []
    for name, arguments, cap, needs in STEPS:
        if name not in only or name in skip:
            continue
        if needs and needs not in produced:
            rows.append((name, "SKIP", None, f"{needs} 결과가 없다"))
            continue
        filled = [a.format(image=produced.get("image", ""), model=produced.get("model3d", "")) for a in arguments]
        filled += ["--name", f"{name.replace('.', '-')}-{stamp}", "--out", OUT, "--max-usd", str(cap)]
        print(f"[{name}] gf gen {' '.join(filled[:1])} ...", file=sys.stderr)
        result = gf(project, filled)
        if not result["ok"]:
            rows.append((name, "FAIL", None, result["error"][:160]))
            continue
        if name == "image":
            produced[name] = first_file(result, (".png", ".jpg", ".jpeg", ".webp"))
        if name == "model3d":
            produced[name] = first_file(result, (".glb",))
        rows.append((name, "PASS", result["cost_usd"], ", ".join(result["files"])))

    total = sum(cost for _, status, cost, _ in rows if status == "PASS" and cost is not None)
    print(f"\n{'단계':<14}{'결과':<6}{'추정 USD':>10}  내용")
    for name, status, cost, detail in rows:
        print(f"{name:<14}{status:<6}{'-' if cost is None else format(cost, '.4f'):>10}  {detail}")
    print(f"\n추정 비용 합계: ${total:.4f} (비용을 추정할 수 없는 호출은 빠져 있다)")
    return 1 if any(status == "FAIL" for _, status, _, _ in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
