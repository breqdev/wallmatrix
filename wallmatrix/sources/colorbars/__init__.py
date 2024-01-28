from pathlib import Path

from PIL import Image

from wallmatrix.sources import Source

class Colorbars(Source):
    SOURCE_NAME = "Color Bar Test Pattern"

    def __init__(self):
        super().__init__()
        self.bars = Image.open(Path(__file__).parent / "colorbars.png")

    def get_image(self, data):
        return self.bars


__matrix_source__ = Colorbars
