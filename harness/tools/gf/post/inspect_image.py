"""이미지를 숫자로 점검한다: 크기, 알파, 색 수, 진짜 픽셀 아트인지."""

import numpy as np
from PIL import Image

from gf.post import pixel
from gf.post.io import unique_colours

LIGHT = (236, 236, 236)
DARK = (24, 24, 28)
PARTIAL_ALPHA_LIMIT = 0.005


def report(pixels: np.ndarray, max_colours: int) -> dict:
    alpha = pixels[..., 3]
    partial = float(((alpha > 0) & (alpha < 255)).mean())
    colours = unique_colours(pixels)
    scale = pixel.integer_scale(pixels)
    reasons = []
    if colours > max_colours:
        reasons.append(f"색이 {colours}개로 한도 {max_colours}개를 넘는다")
    if partial > PARTIAL_ALPHA_LIMIT:
        reasons.append(f"반투명 픽셀이 {partial:.1%} 있다 (픽셀 아트는 알파가 0 또는 255)")
    if scale > 1:
        reasons.append(f"{scale}배로 확대된 상태다 (1x 가 아니다)")
    return {
        "size": [int(pixels.shape[1]), int(pixels.shape[0])],
        "alpha_coverage": round(float((alpha > 0).mean()), 4),
        "partial_alpha": round(partial, 4),
        "unique_colours": colours,
        "integer_scale": scale,
        "pixel_art": not reasons,
        "reasons": reasons,
    }


def check_image(pixels: np.ndarray, scale: int) -> Image.Image:
    """밝은 배경과 어두운 배경에 나란히 올린 확인용 이미지. 테두리 번짐이 한쪽에서 드러난다."""
    sprite = Image.fromarray(pixel.upscale(pixels, scale), "RGBA")
    pad = 8 * scale
    width, height = sprite.width + 2 * pad, sprite.height + 2 * pad
    sheet = Image.new("RGB", (2 * width, height), LIGHT)
    sheet.paste(DARK, (width, 0, 2 * width, height))
    sheet.paste(sprite, (pad, pad), sprite)
    sheet.paste(sprite, (width + pad, pad), sprite)
    return sheet
