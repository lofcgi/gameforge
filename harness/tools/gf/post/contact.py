"""사람이 고르기 쉽게 번호를 붙인 모음판을 만든다."""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BACKGROUND = (38, 38, 44, 255)
TILE = (58, 58, 66, 255)
LABEL_HEIGHT = 22
GAP = 8


def _thumbnail(path: Path, size: int) -> Image.Image:
    with Image.open(path) as image:
        image = image.convert("RGBA")
    scale = min(size / image.width, size / image.height)
    if scale >= 2:
        # 작은 픽셀 아트는 정수배·최근접으로 키워야 뭉개지지 않는다.
        factor = int(scale)
        return image.resize((image.width * factor, image.height * factor), Image.Resampling.NEAREST)
    if scale < 1:
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
    return image


def build(paths: list[Path], labels: list[str], columns: int | None, size: int) -> Image.Image:
    columns = columns or math.ceil(math.sqrt(len(paths)))
    rows = math.ceil(len(paths) / columns)
    cell_w, cell_h = size + GAP, size + LABEL_HEIGHT + GAP
    sheet = Image.new("RGBA", (columns * cell_w + GAP, rows * cell_h + GAP), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=15)
    for index, (path, label) in enumerate(zip(paths, labels)):
        row, column = divmod(index, columns)
        x, y = GAP + column * cell_w, GAP + row * cell_h
        draw.rectangle([x, y, x + size - 1, y + size - 1], fill=TILE)
        thumb = _thumbnail(path, size)
        sheet.alpha_composite(thumb, (x + (size - thumb.width) // 2, y + (size - thumb.height) // 2))
        draw.text((x + 2, y + size + 2), label, fill=(240, 240, 240, 255), font=font)
    return sheet
