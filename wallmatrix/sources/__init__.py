import time


class Source:
    CACHE_TTL = 60

    def __init__(self):
        self.data_cache = None
        self.data_cache_time = 0

    def setup(self):
        "Set up any lasting objects required by the source."
        pass

    def teardown(self):
        "Tear down any lasting objects required by the source."
        pass

    def get_data(self):
        """Return the data required by the source.
        Will be called once every minute.
        Useful to avoid hitting API quotas."""
        pass

    def get_image(self, data):
        """Return an image to display on the screen.
        Called once every second."""
        pass

    def get_data_and_image(self):
        if time.time() - self.data_cache_time > self.CACHE_TTL:
            self.data_cache = self.get_data()
            self.data_cache_time = time.time()

        return self.get_image(self.data_cache)
