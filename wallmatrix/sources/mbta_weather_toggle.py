import time

from wallmatrix.sources import Source
from wallmatrix.sources.mbta import MBTA
from wallmatrix.sources.weather import Weather


class MbtaWeatherToggle(Source):
    SOURCE_NAME = "MBTA and Weather"
    CACHE_TTL = 30

    def __init__(self):
        self.mbta = MBTA()
        self.weather = Weather()

        # MBTA and weather have different cache TTL
        self.last_weather_update = time.time()
        self.weather_data = None

        super().__init__()

    def get_data(self):
        if not self.weather_data or time.time() - self.last_weather_update > 45:
            self.last_weather_update = time.time()
            self.weather_data = self.weather.get_data()

        mbta_data = self.mbta.get_data()

        return [mbta_data, self.weather_data]

    def get_image(self, data):
        mbta_data, weather_data = data

        if time.time() % 20 < 10:
            return self.mbta.get_image(mbta_data)
        else:
            return self.weather.get_image(weather_data)


__matrix_source__ = MbtaWeatherToggle
