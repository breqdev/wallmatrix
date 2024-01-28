from __future__ import annotations
from typing_extensions import Literal, TypedDict
import requests
import datetime

from PIL import Image, ImageDraw

from wallmatrix.fonts import font, small_font
from wallmatrix.sources import Source


class TransitLine(TypedDict):
    color: str
    route: str
    origin: str
    direction: int
    walk_min: int


class MBTA(Source):
    SOURCE_NAME = "MBTA North from NEU"

    LINES: list[TransitLine] = [
        {
            "color": "00843D",
            "route": "Green-B,Green-C,Green-D",
            "origin": "place-hymnl",  # Hynes Convention Center
            "direction": 1,  # East
            "walk_min": 6,
        },
        {
            "color": "FFC72C",
            "route": "1",
            "origin": "93",  # Mass Ave
            "direction": 0,  # North
            "walk_min": 6,
        },
    ]

    def get_wait_time(self, line: TransitLine) -> int | Literal["N/A"]:
        resp = requests.get(
            "https://api-v3.mbta.com/predictions",
            params={
                "filter[stop]": line["origin"],
                "filter[route]": line["route"],
                "filter[direction_id]": line["direction"],
                "include": "stop",
                "sort": "arrival_time",
                "page[limit]": "5",
            },
        ).json()

        predictions = resp["data"]

        current_time = datetime.datetime.now()

        for prediction in predictions:
            departure_time = prediction["attributes"]["departure_time"]
            if departure_time is None:
                continue
            departure_time = datetime.datetime.strptime(
                departure_time, "%Y-%m-%dT%H:%M:%S%z"
            )
            departure_time = departure_time.replace(tzinfo=None)
            wait_time = departure_time - current_time

            if wait_time < datetime.timedelta(minutes=line["walk_min"]):
                continue
            else:
                break
        else:
            return "N/A"

        max_wait = datetime.timedelta(hours=1)
        if wait_time >= max_wait:
            return "N/A"

        minutes = int(wait_time / datetime.timedelta(minutes=1)) - line["walk_min"]

        return minutes

    def draw_line(self, line: TransitLine):
        wait_time = self.get_wait_time(line)

        canvas = Image.new("RGB", (32, 8))
        draw = ImageDraw.Draw(canvas)

        # Draw the colored ring around the T
        draw.ellipse((0, 0, 7, 7), outline="#" + line["color"])

        # Draw the T
        draw.rectangle((2, 3, 4, 3), fill=(196, 196, 196))
        draw.rectangle((3, 4, 3, 5), fill=(196, 196, 196))

        # Display the time remaining
        draw.text((9, 1), str(wait_time), font=font, fill="#" + line["color"])
        if wait_time == "N/A":
            return canvas

        # Draw the M manually (it's extra wide)
        draw.rectangle((19, 3, 22, 3), fill="#" + line["color"])
        draw.rectangle((19, 4, 19, 6), fill="#" + line["color"])
        draw.rectangle((21, 4, 21, 6), fill="#" + line["color"])
        draw.rectangle((23, 4, 23, 6), fill="#" + line["color"])

        # Draw the rest of "min"
        draw.text((25, 2), "in", font=small_font, fill="#" + line["color"])

        return canvas

    def get_data(self) -> Image.Image:
        canvas = Image.new("RGB", (32, 16))

        for i, line in enumerate(self.LINES):
            line_canvas = self.draw_line(line)
            canvas.paste(line_canvas, (0, i * 8, 32, i * 8 + 8))

        return canvas

    def get_image(self, data: Image.Image) -> Image.Image:
        # We cache the entire canvas
        return data


__matrix_source__ = MBTA
