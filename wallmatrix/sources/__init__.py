from abc import ABC, abstractmethod
import time
from typing import Generic, TypeVar
from PIL.Image import Image

T = TypeVar("T")


class Source(ABC, Generic[T]):
    CACHE_TTL = 60

    def __init__(self):
        self.data_cache = self.get_data()
        self.data_cache_time = 0

    def setup(self):
        "Set up any lasting objects required by the source."
        pass

    def teardown(self):
        "Tear down any lasting objects required by the source."
        pass

    @abstractmethod
    def get_data(self) -> T:
        """Return the data required by the source.
        Will be called once every minute.
        Useful to avoid hitting API quotas."""

    @abstractmethod
    def get_image(self, data: T) -> Image:
        """Return an image to display on the screen.
        Called once every second."""

    def get_data_and_image(self) -> Image:
        if time.time() - self.data_cache_time > self.CACHE_TTL:
            self.data_cache = self.get_data()
            self.data_cache_time = time.time()

        return self.get_image(self.data_cache)
