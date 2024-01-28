import datetime
from PIL import Image, ImageDraw
from wallmatrix.fonts import font, small_font

from wallmatrix.sources import Source


class Sar(Source):
    SOURCE_NAME = "Days Until SAR"

    SAR_DATE = datetime.date(2024, 3, 1)

    def get_image(self, data):
        canvas = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(canvas)

        today = datetime.date.today()
        days_left = (self.SAR_DATE - today).days

        draw.text((3, 5), str(days_left), font=font, fill=(255, 255, 255))

        draw.text((16, 1), "days", font=small_font, fill=(128, 128, 128))
        draw.text((16, 9), "left", font=small_font, fill=(128, 128, 128))

        return canvas


__matrix_source__ = Sar
