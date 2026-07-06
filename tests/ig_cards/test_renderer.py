from PIL import Image

from scripts.ig_cards import renderer

MINIMAL_HTML = """<!DOCTYPE html>
<html><head><style>
  html, body { margin:0; padding:0; width:1080px; height:1350px; background:#16181c; }
</style></head>
<body></body></html>"""


def test_render_to_png_creates_file_with_correct_dimensions(tmp_path):
    output_path = tmp_path / "test-card.png"

    renderer.render_to_png(MINIMAL_HTML, str(output_path))

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.size == (1080, 1350)
