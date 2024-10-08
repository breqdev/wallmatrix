import os
from typing import Any
import requests
import datetime

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

from wallmatrix.fonts import font, small_font
from wallmatrix.sources import Source

api_key = os.environ["OPENWEATHERMAP_KEY"]
base_url = "https://api.openweathermap.org/data/2.5/weather?"
zip_code = os.getenv("ZIP_CODE", "02145")

url = base_url + "appid=" + api_key + "&zip=" + zip_code

icon_path = Path(__file__).parent / "icons"


def k_to_f(k: float) -> float:
    return (k - 273.15) * 9 / 5 + 32


def k_to_c(k: float) -> float:
    return k - 273.15


class Weather(Source[dict[str, Any]]):
    SOURCE_NAME = "Local Weather Conditions"

    DAYTIME: dict[str, list[int]] = {
        "cloud": [803],
        "cloud_moon": [],
        "cloud_sun": [801, 802],
        "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
        "cloud_wind_moon": [],
        "cloud_wind_sun": [701],
        "clouds": [804],
        "lightning": [210, 211, 212, 221],
        "moon": [],
        "rain0": [302, 310, 311, 312, 313, 314, 321],
        "rain0_sun": [300, 301],
        "rain1": [502, 521, 522],
        "rain1_moon": [],
        "rain1_sun": [500, 501],
        "rain2": [503, 504, 531],
        "rain_lightning": [200, 201, 202, 230, 231, 232],
        "rain_snow": [511, 615, 616],
        "snow": [602, 613, 621, 622],
        "snow_moon": [],
        "snow_sun": [600, 601, 611, 612, 620],
        "sun": [800],
        "wind": [771, 781],
    }

    NIGHTTIME: dict[str, list[int]] = {
        "cloud": [803],
        "cloud_moon": [801, 802],
        "cloud_sun": [],
        "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
        "cloud_wind_moon": [701],
        "cloud_wind_sun": [],
        "clouds": [804],
        "lightning": [210, 211, 212, 221],
        "moon": [800],
        "rain0": [300, 301, 302, 310, 311, 312, 313, 314, 321],
        "rain0_sun": [],
        "rain1": [502, 521, 522],
        "rain1_moon": [500, 501],
        "rain1_sun": [],
        "rain2": [503, 504, 531],
        "rain_lightning": [200, 201, 202, 230, 231, 232],
        "rain_snow": [511, 615, 616],
        "snow": [602, 613, 621, 622],
        "snow_moon": [600, 601, 611, 612, 620],
        "snow_sun": [],
        "sun": [],
        "wind": [771, 781],
    }

    def get_icon(self, code: int, daytime: bool = True):
        mapping = self.DAYTIME if daytime else self.NIGHTTIME

        for icon, codes in mapping.items():
            if code in codes:
                return icon

    def get_data(self):
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_image(self, data):
        canvas = Image.new("RGB", (32, 16))
        temp: float = data["main"]["temp"]
        temp_f = int(k_to_f(temp))
        temp_c = int(k_to_c(temp))

        icon_code = data["weather"][0]["icon"]

        is_daytime = icon_code[-1] == "d"
        icon_name = self.get_icon(data["weather"][0]["id"], is_daytime)

        icon = Image.open(icon_path / f"{icon_name}.png")
        icon.thumbnail((16, 16), Image.LANCZOS)

        canvas.paste(icon, (-1, 0))

        draw = ImageDraw.Draw(canvas)
        draw.text((15, 1), str(temp_f), font=small_font, fill=(255, 255, 255))
        draw.line((23, 2, 23, 4), fill=(255, 255, 255))
        draw.text((25, 1), str(temp_c), font=small_font, fill=(255, 255, 255))

        now = datetime.datetime.now()

        hour = now.hour % 12
        if hour == 0:
            hour = 12

        # Draw the hour
        draw.text((15, 9), f"{hour:>2}", font=small_font, fill=(255, 255, 255))

        # Draw the colon
        draw.point((23, 10), fill=(255, 255, 255))
        draw.point((23, 12), fill=(255, 255, 255))

        # Draw the minutes
        minutes = str(now.minute).zfill(2)

        draw.text((25, 9), minutes, font=small_font, fill=(255, 255, 255))

        canvas = ImageEnhance.Brightness(canvas).enhance(0.5)

        return canvas


__matrix_source__ = Weather
