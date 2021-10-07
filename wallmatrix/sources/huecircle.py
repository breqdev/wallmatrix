import colorsys

from PIL import Image, ImageDraw

from wallmatrix.sources import Source


class HueCircle(Source):
    SOURCE_NAME = "Hue Circle"
    CACHE_TTL = 5

    def setup(self):
        self.hue = 0

    def get_data(self):
        self.hue += 5
        return tuple(int(i * 256) for i in colorsys.hsv_to_rgb(self.hue / 360, 1, 1))

    def get_image(self, data):
        return Image.new("RGB", (32, 16), data)

__matrix_source__ = HueCircle
