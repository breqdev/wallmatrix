import requests
import datetime

from PIL import Image, ImageDraw

from wallmatrix.fonts import font, small_font
from wallmatrix.sources import Source


class MBTA(Source):
    SOURCE_NAME = "MBTA North from NEU"

    LINES = [
        {
            "color": "ED8B00",
            "line": "line-Orange",
            "route": "Orange",
            "origin": "place-rugg",  # Ruggles
            "destination": "place-haecl",  # Haymarket
            "direction": 1,  # North
            "walk-min": 6,
        },
        {
            "color": "00843D",
            "line": "line-Green",
            "route": "Green-E",
            "origin": "place-nuniv",  # NEU
            "destination": "place-haecl",  # Haymarket
            "direction": 1,  # East
            "walk-min": 10,
        },
    ]

    def get_wait_time(self, line):
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

        soonest_valid = None

        current_time = datetime.datetime.now()

        for prediction in predictions:
            departure_time = prediction["attributes"]["departure_time"]
            departure_time = datetime.datetime.strptime(
                departure_time, "%Y-%m-%dT%H:%M:%S%z"
            )
            departure_time = departure_time.replace(tzinfo=None)
            wait_time = departure_time - current_time

            if wait_time < datetime.timedelta(minutes=line["walk-min"]):
                continue

            soonest_valid = prediction
            break

        if not soonest_valid:
            return "N/A"

        max_wait = datetime.timedelta(hours=1)
        if wait_time >= max_wait:
            return "N/A"

        minutes = int(wait_time / datetime.timedelta(minutes=1)) - line["walk-min"]

        return minutes

    def draw_line(self, line):
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

        # Draw the M manually (it's extra wide)
        draw.rectangle((19, 3, 22, 3), fill="#" + line["color"])
        draw.rectangle((19, 4, 19, 6), fill="#" + line["color"])
        draw.rectangle((21, 4, 21, 6), fill="#" + line["color"])
        draw.rectangle((23, 4, 23, 6), fill="#" + line["color"])

        # Draw the rest of "min"
        draw.text((25, 2), "in", font=small_font, fill="#" + line["color"])

        return canvas

    def get_data(self):
        canvas = Image.new("RGB", (32, 16))

        for i, line in enumerate(self.LINES):
            line_canvas = self.draw_line(line)
            canvas.paste(line_canvas, (0, i * 8, 32, i * 8 + 8))

        return canvas

    def get_image(self, data):
        # We cache the entire canvas
        return data


__matrix_source__ = MBTA
