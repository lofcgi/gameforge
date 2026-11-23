"""컷마다 여섯 장면(처음~끝)을 찍어 captures/cutscenes/<intro|ending>_NN.png 한 장으로 붙인다.

실행 중인 컷신 씬을 단독으로 띄워(`--cs-snap`, `--cs-times`) 그 시각의 화면을 받는다.

실행: uv run -q --project <harness>/tools python captures.py
"""

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[4]
OUT = PROJECT / "captures/cutscenes"
SHOTS = {
    "intro": [8.6, 9.0, 10.6, 10.0, 4.6, 6.2, 10.4, 16.2, 5.0, 9.0],
    "ending": [9.0, 11.4, 10.0],
}
SPREAD = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
EDGE = 0.6


def main() -> None:
    for scene, durations in SHOTS.items():
        times = [[round(EDGE + (dur - EDGE * 2) * at, 2) for at in SPREAD] for dur in durations]
        jobs = ",".join(f"{shot}:{t}" for shot, row in enumerate(times) for t in row)
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(
                ["godot", "--path", str(PROJECT), f"scenes/cutscenes/{scene}.tscn", "--", f"--cs-snap={folder}", f"--cs-times={jobs}"],
                check=True,
            )
            for shot, row in enumerate(times):
                sheet = Image.new("RGB", (640 * 3, 360 * 2))
                for i, t in enumerate(row):
                    frame = Image.open(Path(folder) / f"s{shot:02d}_t{t:05.2f}.png").convert("RGB").resize((640, 360), Image.NEAREST)
                    ImageDraw.Draw(frame).text((4, 346), f"{scene}{shot + 1:02d} t={t}s", fill=(255, 255, 0))
                    sheet.paste(frame, ((i % 3) * 640, (i // 3) * 360))
                sheet.save(OUT / f"{scene}_{shot + 1:02d}.png")
                print(OUT / f"{scene}_{shot + 1:02d}.png")


if __name__ == "__main__":
    main()
