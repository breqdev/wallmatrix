import time

class MatrixDriver:
    INTERVAL = 10

    def __init__(self):
        self.sources = []
        self.current_source = None

    def refresh(self):
        if not self.current_source:
            return

        self.image = self.current_source.get_image()

        self.update_image()

    def update_image(self):
        pass

    def loop(self):
        while True:
            start_time = time.time()

            self.refresh()

            time.sleep(max(0, self.INTERVAL + start_time - time.time()))