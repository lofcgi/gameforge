"""프레임을 스프라이트 시트 한 장으로 묶고 매니페스트(JSON)와 Godot SpriteFrames(.tres)를 만든다."""

import math

import numpy as np

from gf.core.output import GfError


def pack(frames: list[np.ndarray], columns: int | None, padding: int) -> tuple[np.ndarray, list[dict]]:
    sizes = {frame.shape[:2] for frame in frames}
    if len(sizes) != 1:
        raise GfError(f"프레임 크기가 서로 다르다 ({len(sizes)}종). 먼저 gf post align 으로 맞춘다.")
    height, width = sizes.pop()
    columns = columns or math.ceil(math.sqrt(len(frames)))
    rows = math.ceil(len(frames) / columns)
    sheet = np.zeros((rows * (height + padding) - padding, columns * (width + padding) - padding, 4), dtype=np.uint8)
    rects = []
    for index, frame in enumerate(frames):
        row, column = divmod(index, columns)
        x, y = column * (width + padding), row * (height + padding)
        sheet[y : y + height, x : x + width] = frame
        rects.append({"x": x, "y": y, "w": width, "h": height})
    return sheet, rects


def manifest(image: str, name: str, fps: float, loop: bool, rects: list[dict]) -> dict:
    return {
        "image": image,
        "frame_size": [rects[0]["w"], rects[0]["h"]],
        "animations": {name: {"fps": fps, "loop": loop, "frames": rects}},
    }


def godot_sprite_frames(texture_res_path: str, name: str, fps: float, loop: bool, rects: list[dict]) -> str:
    """Godot 4 의 SpriteFrames 리소스 텍스트. AnimatedSprite2D 에 바로 넣을 수 있다."""
    lines = [
        f'[gd_resource type="SpriteFrames" load_steps={len(rects) + 2} format=3]',
        "",
        f'[ext_resource type="Texture2D" path="{texture_res_path}" id="1"]',
        "",
    ]
    for index, rect in enumerate(rects):
        lines += [
            f'[sub_resource type="AtlasTexture" id="frame_{index}"]',
            'atlas = ExtResource("1")',
            f"region = Rect2({rect['x']}, {rect['y']}, {rect['w']}, {rect['h']})",
            "",
        ]
    entries = ", ".join(
        f'{{\n"duration": 1.0,\n"texture": SubResource("frame_{index}")\n}}' for index in range(len(rects))
    )
    lines += [
        "[resource]",
        "animations = [{",
        f'"frames": [{entries}],',
        f'"loop": {"true" if loop else "false"},',
        f'"name": &"{name}",',
        f'"speed": {float(fps)}',
        "}]",
        "",
    ]
    return "\n".join(lines)
