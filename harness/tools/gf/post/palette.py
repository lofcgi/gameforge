"""공용 팔레트: 여러 이미지에서 N색을 뽑아 저장하거나, 저장된 팔레트로 이미지를 맞춘다."""

import json
from pathlib import Path

import numpy as np
from PIL import Image

from gf.core.output import GfError
from gf.post.chroma import parse_colour, to_hex

KMEANS_ROUNDS = 24
SWATCH = 32
SWATCH_COLUMNS = 8


def _luminance(colours: np.ndarray) -> np.ndarray:
    return colours @ np.array([0.299, 0.587, 0.114])


def _bins(visible: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """색을 채널당 5비트 칸으로 묶어 (칸의 평균색, 픽셀 수)로 줄인다. 큰 이미지에서도 수만 개를 넘지 않는다."""
    keys = (visible >> 3).astype(np.int32) @ np.array([1024, 32, 1])
    _, inverse, counts = np.unique(keys, return_inverse=True, return_counts=True)
    sums = np.zeros((len(counts), 3))
    np.add.at(sums, inverse, visible)
    return sums / counts[:, None], counts


def _spread_seeds(colours: np.ndarray, weights: np.ndarray, count: int) -> np.ndarray:
    """가장 흔한 색에서 시작해 이미 고른 색들과 가장 먼 색을 차례로 고른다."""
    chosen = [int(np.argmax(weights))]
    nearest = ((colours - colours[chosen[0]]) ** 2).sum(axis=1)
    for _ in range(count - 1):
        chosen.append(int(np.argmax(nearest)))
        nearest = np.minimum(nearest, ((colours - colours[chosen[-1]]) ** 2).sum(axis=1))
    return colours[chosen].copy()


def _cluster(colours: np.ndarray, weights: np.ndarray, count: int) -> np.ndarray:
    """가중 k-means. 넓게 퍼진 색 무리부터 나뉘므로 외곽선의 어두운 색들이 여러 칸을 차지하지 않는다."""
    centres = _spread_seeds(colours, weights, count)
    for _ in range(KMEANS_ROUNDS):
        distances = ((colours[:, None, :] - centres[None, :, :]) ** 2).sum(axis=-1)
        owner = np.argmin(distances, axis=1)
        for index in range(count):
            mine = owner == index
            if mine.any():
                centres[index] = np.average(colours[mine], axis=0, weights=weights[mine])
    return np.unique(np.rint(centres).astype(np.uint8), axis=0)


def extract(images: list[np.ndarray], count: int) -> np.ndarray:
    """불투명한 픽셀만 모아 count 색으로 줄인다. 이미 count 색 이하면 그 색을 그대로 쓴다."""
    visible = np.concatenate([p[p[..., 3] >= 128][:, :3] for p in images])
    if len(visible) == 0:
        raise GfError("불투명한 픽셀이 없어 팔레트를 뽑을 수 없다.")
    unique = np.unique(visible, axis=0)
    if len(unique) > count:
        colours, counts = _bins(visible)
        # 픽셀 수 그대로 쓰면 넓은 면의 색이 팔레트를 다 차지하고 눈·하이라이트 같은 작은
        # 강조색이 사라진다. 제곱근만큼만 반영한다.
        unique = _cluster(colours, np.sqrt(counts), count)
    return unique[np.argsort(_luminance(unique.astype(np.float32)))]


def save(colours: np.ndarray, json_path: Path, sources: list[str]) -> list[Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"count": len(colours), "colors": [to_hex(c) for c in colours], "sources": sources}
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    rows = -(-len(colours) // SWATCH_COLUMNS)
    swatch = np.zeros((rows * SWATCH, SWATCH_COLUMNS * SWATCH, 4), dtype=np.uint8)
    for index, colour in enumerate(colours):
        y, x = divmod(index, SWATCH_COLUMNS)
        swatch[y * SWATCH : (y + 1) * SWATCH, x * SWATCH : (x + 1) * SWATCH] = [*colour, 255]
    png_path = json_path.with_suffix(".png")
    Image.fromarray(swatch, "RGBA").save(png_path)
    return [json_path, png_path]


def load(path: Path) -> np.ndarray:
    """gf 팔레트 JSON, 한 줄에 색 하나인 .hex, 또는 색 견본 이미지를 읽는다."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        texts = json.loads(path.read_text())["colors"]
    elif suffix == ".hex":
        texts = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    else:
        with Image.open(path) as image:
            pixels = np.array(image.convert("RGBA"))
        return np.unique(pixels[pixels[..., 3] > 0][:, :3], axis=0)
    if not texts:
        raise GfError(f"팔레트가 비어 있다: {path}")
    return np.array([parse_colour(text) for text in texts]).astype(np.uint8)


def _nearest(colours: np.ndarray, palette: np.ndarray) -> np.ndarray:
    difference = colours[:, None, :].astype(np.int32) - palette[None, :, :].astype(np.int32)
    return palette[np.argmin((difference**2).sum(axis=-1), axis=1)]


def _dithered(pixels: np.ndarray, palette: np.ndarray) -> np.ndarray:
    holder = Image.new("P", (1, 1))
    holder.putpalette(palette.astype(np.uint8).ravel().tolist())
    source = Image.fromarray(np.ascontiguousarray(pixels[..., :3]), "RGB")
    mapped = source.quantize(palette=holder, dither=Image.Dither.FLOYDSTEINBERG)
    return np.array(mapped.convert("RGB"))


def apply(pixels: np.ndarray, palette: np.ndarray, dither: bool = False) -> np.ndarray:
    """모든 픽셀을 팔레트의 가장 가까운 색으로 바꾼다. 알파는 건드리지 않는다."""
    result = pixels.copy()
    if dither:
        result[..., :3] = _dithered(pixels, palette)
    else:
        unique, inverse = np.unique(pixels[..., :3].reshape(-1, 3), axis=0, return_inverse=True)
        mapped = np.concatenate([_nearest(chunk, palette) for chunk in np.array_split(unique, max(1, len(unique) // 4096))])
        result[..., :3] = mapped[inverse.ravel()].reshape(pixels.shape[0], pixels.shape[1], 3)
    result[result[..., 3] == 0, :3] = 0
    return result
