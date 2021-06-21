import os
import requests
import datetime

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

from wallmatrix.fonts import font, small_font
from wallmatrix.sources import Source

api_key = os.environ["OPENWEATHERMAP_KEY"]
base_url = "https://api.openweathermap.org/data/2.5/weather?"
zip_code = "04074"

url = base_url + "appid=" + api_key + "&zip=" + zip_code

icon_path = Path(__file__).parent / "icons"


def k_to_f(k):
    return (k - 273.15) * 9/5 + 32


class Weather(Source):
    def get_image(self):
        canvas = Image.new("RGB", (32, 16))

        response = requests.get(url).json()

        temperature = int(k_to_f(response["main"]["temp"]))

        icon_code = response["weather"][0]["icon"]
        # icon = requests.get(
        #     f"https://openweathermap.org/img/wn/{icon_code}@2x.png", stream=True
        # ).raw
        # icon.decode_content = True
        # icon = Image.open(icon)

        icon = Image.open(icon_path / f"{icon_code}.png")
        icon.thumbnail((16, 16), Image.ANTIALIAS)

        canvas.paste(icon, (-1, 0))

        draw = ImageDraw.Draw(canvas)
        draw.text((16, 1), f"{temperature}°", font=font, fill=(255, 255, 255))

        now = datetime.datetime.now()

        hour_digit = now.hour % 12
        if hour_digit == 0:
            hour_digit = 12

        # Draw the first digit of the hour
        if hour_digit >= 10:
            draw.line((16, 9, 16, 13), fill=(255, 255, 255))

        # Draw the last digit of the hour
        draw.text((18, 9), str(hour_digit)[-1], font=small_font, fill=(255, 255, 255))

        # Draw the colon
        draw.point((22, 10), fill=(255, 255, 255))
        draw.point((22, 12), fill=(255, 255, 255))

        # Draw the minutes
        minutes = str(now.minute).zfill(2)

        draw.text((24, 9), minutes, font=small_font, fill=(255, 255, 255))

        canvas = ImageEnhance.Brightness(canvas).enhance(0.5)

        return canvas

__matrix_source__ = Weather