from __future__ import annotations
from typing_extensions import TypedDict
import requests
import datetime
import os

from PIL import Image, ImageDraw

from wallmatrix.fonts import font
from wallmatrix.sources import Source


class TransitLine(TypedDict):
    color: str
    route: str
    origin: str
    direction: int


class MBTA(Source):
    SOURCE_NAME = "MBTA from The Avapartment"
    CACHE_TTL = 30

    LINES: list[TransitLine] = [
        {
            "color": "00843D",
            "route": "Green-E",
            "origin": "place-mgngl",  # Magoun Square
            "direction": 0,  # West
        },
        {
            "color": "FFC72C",
            "route": "89",
            "origin": "2698",  # Broadway @ Cedar St
            "direction": 1,  # towards Sullivan
        },
    ]

    def get_time_text(self, line: TransitLine) -> tuple[list[str], list[str]]:
        """
        Returns the upcoming departure times to display.

        The first string, shown in emphasized text, contains the realtime
        predicted departure times. The second string contains scheduled
        departures.
        """

        predictions_response = requests.get(
            "https://api-v3.mbta.com/predictions",
            params={
                "filter[stop]": line["origin"],
                "filter[route]": line["route"],
                "filter[direction_id]": line["direction"],
                "include": "stop",
                "sort": "arrival_time",
                "page[limit]": "10",
            },
            headers={"Authorization": f"Bearer {os.environ['MBTA_TOKEN']}"},
        )

        predictions_response.raise_for_status()

        predictions = predictions_response.json()["data"]

        # Handle mapping the current date/time to the service date/time
        # The current date/time and service date/time are the same UNLESS
        # it is between midnight and 3 AM, in which case the date is _yesterday_
        # and the time is 24 + (actual hour).
        # For instance, 1 AM on 9/2/24 is considered "25:00" on 9/1/24.

        # We have to rawdog the date representation here bc datetime, quite
        # rationally, won't represent hours above 24 for us

        wall_time = datetime.datetime.now().replace(tzinfo=None)

        if wall_time.hour < 3:
            service_date = wall_time.date() - datetime.timedelta(days=1)
            service_hour = wall_time.hour + 24
            service_minute = wall_time.minute
        else:
            service_date = wall_time.date()
            service_hour = wall_time.hour
            service_minute = wall_time.minute

        schedule_response = requests.get(
            "https://api-v3.mbta.com/schedules",
            params={
                "filter[stop]": line["origin"],
                "filter[route]": line["route"],
                "filter[direction_id]": line["direction"],
                "include": "stop",
                "sort": "arrival_time",
                "page[limit]": "10",
                "filter[date]": service_date.strftime("%Y-%m-%d"),
                "filter[min_time]": f"{service_hour:02}:{service_minute:02}",
                "filter[max_time]": f"{service_hour+2:02}:{service_minute:02}",
            },
            headers={"Authorization": f"Bearer {os.environ['MBTA_TOKEN']}"},
        )

        schedule_response.raise_for_status()

        schedules = schedule_response.json()["data"]

        current_time = datetime.datetime.now()

        realtime_times = []
        scheduled_times = []

        # Pull from realtime predictions first
        realtime_trips = set()

        for prediction in predictions:
            if len(realtime_times) >= 3:
                break

            trip_id = prediction["relationships"]["trip"]["data"]["id"]

            departure_time = prediction["attributes"]["departure_time"]
            if departure_time is None:
                continue

            realtime_trips.add(trip_id)
            departure_time = datetime.datetime.strptime(
                departure_time, "%Y-%m-%dT%H:%M:%S%z"
            )

            departure_time = departure_time.replace(tzinfo=None)
            wait_time = departure_time - current_time

            if wait_time <= datetime.timedelta(minutes=0):
                print(f"Rejecting trip {trip_id}, departed before now")
                continue
            if wait_time >= datetime.timedelta(minutes=100):
                print(f"Rejecting trip {trip_id}, departs more than 100 min from now")
                continue

            realtime_times.append(wait_time)

        # Then, pull from schedules
        for schedule in schedules:
            if len(realtime_times) + len(scheduled_times) >= 3:
                break

            trip_id = schedule["relationships"]["trip"]["data"]["id"]
            if trip_id in realtime_trips:
                print(f"Rejecting schedule for {trip_id}, already checked realtime")
                continue

            departure_time = schedule["attributes"]["departure_time"]
            if departure_time is None:
                continue
            departure_time = datetime.datetime.strptime(
                departure_time, "%Y-%m-%dT%H:%M:%S%z"
            )

            departure_time = departure_time.replace(tzinfo=None)
            wait_time = departure_time - current_time

            if wait_time <= datetime.timedelta(minutes=0):
                print(
                    f"Rejecting trip {trip_id}, departed {departure_time} before now {current_time}"
                )
                continue
            if wait_time >= datetime.timedelta(minutes=100):
                print(f"Rejecting trip {trip_id}, departs more than 100 min from now")
                continue

            scheduled_times.append(wait_time)

        if len(realtime_times) + len(scheduled_times) == 0:
            return ("N/A", "")

        realtime_text = [
            str(int(time / datetime.timedelta(minutes=1))) for time in realtime_times
        ]

        scheduled_text = [
            str(int(time / datetime.timedelta(minutes=1))) for time in scheduled_times
        ]

        return [realtime_text, scheduled_text]

    def draw_line(self, line: TransitLine):
        realtime, scheduled = self.get_time_text(line)

        canvas = Image.new("RGB", (32, 8))
        draw = ImageDraw.Draw(canvas)

        # Draw the colored ring around the T
        draw.ellipse((0, 0, 7, 7), outline="#" + line["color"])

        # Draw the T
        draw.rectangle((2, 2, 5, 3), fill=(196, 196, 196))
        draw.rectangle((3, 4, 4, 5), fill=(196, 196, 196))

        # Display the time remaining
        x = 9
        for item in realtime:
            length = draw.textlength(item, font=font)
            if (x + length) > 32:
                return canvas

            draw.text((x, 1), item, font=font, fill="#" + line["color"])
            x += length + 3

        for item in scheduled:
            length = draw.textlength(item, font=font)
            if (x + length) > 32:
                return canvas

            draw.text((x, 1), item, font=font, fill=(196, 196, 196))
            x += length + 3

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
