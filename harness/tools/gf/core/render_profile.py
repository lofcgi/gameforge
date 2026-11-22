"""2D 템플릿의 화면 설정을 스타일에 맞춘다.

템플릿은 픽셀 아트용(기준 해상도 그대로, nearest, 정수배)으로 들어 있다. 픽셀이 아닌 2D 그림을 그 설정으로
그리면 320x180 으로 뭉개진 뒤 확대된다. `--style 2d` 는 레벨 단위(320x180)는 그대로 두고, 화면을 창 해상도로
그리며(Godot: 스트레치 canvas_items, web: 창 크기 캔버스) 그림을 단위당 4픽셀로 놓는다(1280x720 에서 1:1).
"""

from pathlib import Path

from gf.core.output import GfError

HD_PIXELS_PER_UNIT = 4

# (파일, 템플릿에 있는 줄, 바꿀 줄). 템플릿이 바뀌어 줄을 못 찾으면 조용히 넘어가지 않고 실패한다.
HD_EDITS = {
    "godot-2d": [
        ("project.godot", 'window/stretch/mode="viewport"', 'window/stretch/mode="canvas_items"'),
        ("project.godot", 'window/stretch/scale_mode="integer"', 'window/stretch/scale_mode="fractional"'),
        ("project.godot", "art/pixels_per_unit=1", f"art/pixels_per_unit={HD_PIXELS_PER_UNIT}"),
        ("project.godot", "textures/canvas_textures/default_texture_filter=0",
         "textures/canvas_textures/default_texture_filter=1"),
        ("project.godot", "2d/snap/snap_2d_transforms_to_pixel=true", "2d/snap/snap_2d_transforms_to_pixel=false"),
        ("project.godot", "2d/snap/snap_2d_vertices_to_pixel=true", "2d/snap/snap_2d_vertices_to_pixel=false"),
        ("project.godot", "theme/default_font_antialiasing=0", "theme/default_font_antialiasing=1"),
        ("project.godot", "theme/default_font_subpixel_positioning=0", "theme/default_font_subpixel_positioning=1"),
    ],
    "web-2d": [
        ("src/view.js", "ppu: 1, smooth: false", f"ppu: {HD_PIXELS_PER_UNIT}, smooth: true"),
    ],
}


def apply(project: Path, template: str, style: str) -> dict | None:
    """복사된 2D 템플릿을 스타일에 맞게 고치고, 적용된 화면 설정을 돌려준다. 2D 템플릿이 아니면 None."""
    if template not in HD_EDITS:
        return None
    if style != "2d":
        return {"units": [320, 180], "pixels_per_unit": 1, "filter": "nearest", "scaling": "integer"}
    for name, old, new in HD_EDITS[template]:
        path = project / name
        text = path.read_text()
        if text.count(old) != 1:
            raise GfError(f"템플릿 {template}/{name} 에서 '{old}' 를 정확히 한 번 찾지 못해 고해상도 2D 설정을 적용할 수 없다.")
        path.write_text(text.replace(old, new))
    return {"units": [320, 180], "pixels_per_unit": HD_PIXELS_PER_UNIT, "filter": "linear", "scaling": "window"}
