import datetime

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from PIL import Image, ImageDraw

from wallmatrix.sources import Source
from wallmatrix.fonts import font, small_font


class WorldClock(Source):
    SOURCE_NAME = "World Clock"

    ZONES = [
        ["LAX", "America/Los_Angeles", (255, 0, 0)],
        ["UTC", "UTC", (0, 255, 255)],
        ["BER", "Europe/Berlin", (255, 255, 0)],
        ["PEK", "Asia/Shanghai", (255, 0, 255)],
    ]

    def __init__(self):
        super().__init__()
        self.incr = 0

    def get_image(self, data):
        canvas = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(canvas)

        local_time = datetime.datetime.now()

        DATE_COLOR = (255, 128, 0)

        month = local_time.strftime("%m")
        if month[0] == "1":
            draw.line((0, 1, 0, 5), fill=DATE_COLOR)
        draw.text((2, 1), month[1:], font=small_font, fill=DATE_COLOR)

        draw.point((6, 3), fill=DATE_COLOR)

        date = local_time.strftime("%d")
        draw.text((8, 1), date, font=small_font, fill=DATE_COLOR)

        time = local_time.strftime("%H%M")
        draw.text((16, 1), time, font=small_font, fill=(0, 255, 0))

        code, zone, color = self.ZONES[self.incr // 10]
        self.incr = (self.incr + 1) % (len(self.ZONES) * 10)

        draw.text((1, 9), code[:2], font=font, fill=color)
        draw.text((11, 10), code[2:], font=small_font, fill=color)

        zone_time = datetime.datetime.now(zoneinfo.ZoneInfo(zone))
        zone_str = zone_time.strftime("%H%M")

        draw.text((16, 9), zone_str, font=small_font, fill=color)

        return canvas


__matrix_source__ = WorldClock
