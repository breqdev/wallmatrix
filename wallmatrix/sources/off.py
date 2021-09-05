from PIL import Image, ImageDraw

from wallmatrix.sources import Source


class Off(Source):
    SOURCE_NAME = "Off"

    def get_image(self, data):
        return Image.new("RGB", (32, 16))

__matrix_source__ = Off
