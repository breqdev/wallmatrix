from pathlib import Path

from PIL import ImageFont

import wallmatrix

font_path = Path(wallmatrix.__file__).parent / "fonts"

font = ImageFont.load(font_path / "5x7.pil")
small_font = ImageFont.load(font_path / "tom-thumb.pil")
large_font = ImageFont.load(font_path / "6x13.pil")
