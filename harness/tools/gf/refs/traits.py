"""고른 묶음의 측정 가능한 특성. 정성적인 해석은 에이전트가 이미지와 이 결과를 보고 따로 쓴다."""

import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gf.core.output import GfError
from gf.core.state import now
from gf.refs import store

LUMA = np.array([0.2126, 0.7152, 0.0722])
STAT_SIDE = 256
PALETTE_SIDE = 64
EDGE_THRESHOLD = 0.08
CELL_MAX = 64
CELL_ALIGNED_SHARE = 0.9
CELL_DIFF_TOLERANCE = 48
ASPECTS = {
    "21:9": 21 / 9, "16:9": 16 / 9, "16:10": 1.6, "3:2": 1.5, "4:3": 4 / 3, "1:1": 1.0,
    "3:4": 0.75, "2:3": 2 / 3, "9:16": 9 / 16,
}  # fmt: skip
ACCENT_COLOURS = 3
ACCENT_MIN_SATURATION = 0.5
ACCENT_MIN_VALUE = 0.3
SCALARS = ["brightness", "contrast", "saturation", "warmth", "edge_density"]


def _rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def _edge_density(luma: np.ndarray) -> float:
    dx = np.diff(luma, axis=1)[:-1, :]
    dy = np.diff(luma, axis=0)[:, :-1]
    return float((np.hypot(dx, dy) > EDGE_THRESHOLD).mean())


def _axis_cell(rgb: np.ndarray, axis: int) -> int | None:
    """한 축에서 색이 바뀌는 자리가 일정한 간격의 격자선에 몰려 있으면 그 간격을 돌려준다."""
    change = np.abs(np.diff(rgb.astype(np.int16), axis=axis)).sum(axis=2) > CELL_DIFF_TOLERANCE
    profile = change.sum(axis=1 - axis).astype(np.int64)
    total = profile.sum()
    if total == 0:
        return None
    positions = np.arange(1, len(profile) + 1)
    for size in range(min(CELL_MAX, rgb.shape[axis] // 4), 1, -1):
        on_grid = np.bincount(positions % size, weights=profile, minlength=size).max()
        if on_grid / total >= CELL_ALIGNED_SHARE:
            return size
    return None


def pixel_cell(rgb: np.ndarray) -> int | None:
    """확대된 픽셀 아트의 칸 크기(px). 가로세로가 같은 값일 때만 인정한다."""
    horizontal = _axis_cell(rgb, 1)
    if horizontal is None or horizontal != _axis_cell(rgb, 0):
        return None
    return horizontal


def aspect_label(ratio: float) -> str:
    name, value = min(ASPECTS.items(), key=lambda item: abs(item[1] - ratio))
    return name if abs(value - ratio) / value <= 0.03 else "기타"


def image_stats(path: Path) -> dict:
    image = _rgb(path)
    small = image.copy()
    small.thumbnail((STAT_SIDE, STAT_SIDE), Image.Resampling.BOX)
    pixels = np.asarray(small, dtype=np.float64) / 255.0
    luma = pixels @ LUMA
    high, low = pixels.max(axis=2), pixels.min(axis=2)
    saturation = np.divide(high - low, high, out=np.zeros_like(high), where=high > 0)
    return {
        "file": path.name,
        "width": image.width,
        "height": image.height,
        "aspect": round(image.width / image.height, 3),
        "brightness": round(float(luma.mean()), 4),
        "contrast": round(float(luma.std()), 4),
        "saturation": round(float(saturation.mean()), 4),
        "warmth": round(float((pixels[..., 0] - pixels[..., 2]).mean()), 4),
        "edge_density": round(_edge_density(luma), 4),
        "pixel_cell": pixel_cell(np.asarray(image)),
    }


def _seed_centres(points: np.ndarray, weights: np.ndarray, k: int) -> np.ndarray:
    """무작위 없이 고른다: 가장 많은 색에서 시작해, 멀고 많은 색을 차례로 더한다."""
    centres = [points[weights.argmax()]]
    nearest = ((points - centres[0]) ** 2).sum(axis=1)
    while len(centres) < k and nearest.max() > 0:
        centres.append(points[(nearest * weights).argmax()])
        nearest = np.minimum(nearest, ((points - centres[-1]) ** 2).sum(axis=1))
    return np.array(centres)


def _assign(points: np.ndarray, centres: np.ndarray) -> np.ndarray:
    return ((points[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)


def palette(pixels: np.ndarray, k: int) -> list[dict]:
    """가중 k-평균으로 대표 색 k개와 비중을 구한다. pixels 는 N×3 uint8."""
    bins = pixels.astype(np.int32) >> 4
    keys = (bins[:, 0] << 8) | (bins[:, 1] << 4) | bins[:, 2]
    _, inverse, counts = np.unique(keys, return_inverse=True, return_counts=True)
    sums = np.zeros((len(counts), 3))
    np.add.at(sums, inverse, pixels)
    points, weights = sums / counts[:, None], counts.astype(np.float64)
    centres = _seed_centres(points, weights, k)
    for _ in range(30):
        labels = _assign(points, centres)
        moved = centres.copy()
        for index in range(len(centres)):
            mask = labels == index
            if mask.any():
                moved[index] = np.average(points[mask], axis=0, weights=weights[mask])
        if np.allclose(moved, centres):
            break
        centres = moved
    shares = np.bincount(_assign(points, centres), weights=weights, minlength=len(centres))
    shares = shares / weights.sum()
    colours = []
    for index in np.argsort(-shares):
        if shares[index] == 0:
            continue
        rgb = [round(float(value)) for value in centres[index]]
        colours.append(
            {
                "hex": "#{:02x}{:02x}{:02x}".format(*rgb),
                "rgb": rgb,
                "share": round(float(shares[index]), 4),
            }
        )
    return colours


def _palette_pixels(paths: list[Path]) -> np.ndarray:
    # 가장 가까운 픽셀을 그대로 집어야 경계에서 섞인 색이 생기지 않는다.
    samples = [
        np.asarray(_rgb(path).resize((PALETTE_SIDE, PALETTE_SIDE), Image.Resampling.NEAREST))
        for path in paths
    ]
    return np.concatenate([sample.reshape(-1, 3) for sample in samples])


def accents(pixels: np.ndarray) -> list[dict]:
    """선명한 색만 따로 뽑는다. 면적이 작은 강조색은 전체 팔레트에서 무채색에 묻히기 때문이다."""
    high = pixels.max(axis=1).astype(np.float64)
    low = pixels.min(axis=1)
    vivid = (high >= ACCENT_MIN_VALUE * 255) & (high - low >= ACCENT_MIN_SATURATION * high)
    if not vivid.any():
        return []
    share = float(vivid.mean())
    return [
        {**colour, "share": round(colour["share"] * share, 4)}
        for colour in palette(pixels[vivid], ACCENT_COLOURS)
    ]


def _spread(values: list[float]) -> dict:
    array = np.array(values)
    return {
        "mean": round(float(array.mean()), 4),
        "min": round(float(array.min()), 4),
        "max": round(float(array.max()), 4),
    }


def _temperature(warmth: float) -> str:
    if warmth > 0.04:
        return "warm"
    return "cool" if warmth < -0.04 else "neutral"


def analyse(paths: list[Path], k: int) -> dict | None:
    if not paths:
        return None
    per_image = [image_stats(path) for path in paths]
    summary = {name: _spread([stats[name] for stats in per_image]) for name in SCALARS}
    cells = [stats["pixel_cell"] for stats in per_image if stats["pixel_cell"]]
    pixels = _palette_pixels(paths)
    return {
        "count": len(paths),
        "palette": palette(pixels, k),
        "accents": accents(pixels),
        **summary,
        "temperature": _temperature(summary["warmth"]["mean"]),
        "pixel_art": {
            "images_with_grid": len(cells),
            "cell_sizes": dict(sorted(Counter(cells).items())),
        },
        "aspects": dict(
            Counter(aspect_label(stats["aspect"]) for stats in per_image).most_common()
        ),
        "images": per_image,
    }


def _difference(reference: dict, anti: dict) -> dict:
    """레퍼런스 평균 − 안티 평균. 양수면 레퍼런스 쪽이 더 크다."""
    return {name: round(reference[name]["mean"] - anti[name]["mean"], 4) for name in SCALARS}


def swatch(groups: dict[str, list[dict]], path: Path) -> None:
    """팔레트를 비중만큼의 폭으로 그린다. 한 줄 안에서의 상대 비중이다."""
    width, row, label = 760, 90, 150
    image = Image.new("RGB", (width, row * len(groups)), (24, 24, 28))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=20)
    for line, (name, colours) in enumerate(groups.items()):
        top = line * row
        draw.text((10, top + 32), name, font=font, fill=(255, 255, 255))
        left = float(label)
        total = sum(colour["share"] for colour in colours)
        for colour in colours:
            right = left + (width - label) * colour["share"] / total
            draw.rectangle(
                (round(left), top + 6, round(right), top + row - 6), fill=tuple(colour["rgb"])
            )
            left = right
    image.save(path)


def build(project: Path, k: int) -> dict:
    directory = store.picked(project)
    metas = store.items(directory)
    groups = {
        kind: [directory / meta["file"] for meta in metas if meta["kind"] == kind]
        for kind in store.KINDS
    }
    if not groups["reference"]:
        raise GfError("고른 레퍼런스가 없다. 먼저 gf ref pick 으로 고른다.")
    reference, anti = analyse(groups["reference"], k), analyse(groups["anti"], k)
    result = {
        "generated": now(),
        "k": k,
        "reference": reference,
        "anti": anti,
        "difference": _difference(reference, anti) if anti else None,
        "notes": {
            item["file"]: {"kind": item["kind"], "note": item["note"], "tags": item["tags"]}
            for item in metas
        },
    }
    (directory / "traits.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    rows = {}
    for name, group in (("REF", reference), ("ANTI", anti)):
        if group:
            rows[name] = group["palette"]
            if group["accents"]:
                rows[f"{name} ACCENT"] = group["accents"]
    swatch(rows, directory / "traits-palette.png")
    return result
