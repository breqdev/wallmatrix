from pathlib import Path

from PIL import Image

from wallmatrix.sources.source import Source

class Colorbars(Source):
    def setup(self):
        self.bars = Image.open(Path(__file__).parent / "colorbars.png")

    def get_image(self):
        return self.bars