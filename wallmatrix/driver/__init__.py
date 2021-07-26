import time
import os
import importlib
import traceback
import queue
import dataclasses
from pathlib import Path

from PIL import Image, ImageDraw

from wallmatrix.fonts import large_font

import wallmatrix


@dataclasses.dataclass
class DriverEvent:
    action: str
    source: str = None
    message: str = None


class MatrixDriver:
    INTERVAL = 10

    def __init__(self):
        self.sources = {}
        self.current_source = os.getenv("DEFAULT_SOURCE")

        self.load_sources()

        self.message_queue = queue.Queue()
        self.last_refresh = 0

    def load_sources(self):
        source_path = Path(wallmatrix.__file__).parent / "sources"

        for child in source_path.iterdir():
            if child.name == "__init__.py":
                continue

            import_name = None
            if child.is_dir():
                if (child / "__init__.py").exists():
                    import_name = "wallmatrix.sources." + child.name

            if child.is_file():
                if child.name.endswith(".py"):
                    import_name = (
                        "wallmatrix.sources." + child.name[:-len(".py")])

            if not import_name:
                continue

            module = importlib.import_module(import_name)

            source = getattr(module, "__matrix_source__", None)

            if source:
                source = source()

                self.sources[import_name] = source

                source.setup()

    def refresh(self):
        self.last_refresh = time.time()

        if not self.current_source:
            return

        try:
            self.image = self.sources[self.current_source].get_data_and_image()
        except Exception:
            traceback.print_exc()

        self.update_image()

    def flash_message(self, message):
        canvas = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(canvas)

        width = large_font.getsize(message)[0]

        for x_offset in range(32, -width, -1):
            draw.rectangle((0, 0, 32, 16), fill=(0, 0, 0))
            draw.text((x_offset, 1), message, font=large_font)
            self.image = canvas
            self.update_image()
            time.sleep(0.1)

    def update_image(self):
        pass

    def loop(self):
        while True:
            try:
                event = self.message_queue.get(block=False)
            except queue.Empty:
                pass
            else:
                if event.action == "SOURCE_CHANGED":
                    self.current_source = event.source
                    self.refresh()
                elif event.action == "FLASH_MESSAGE":
                    self.flash_message(event.message)
                else:
                    print("Unrecognized action " + event.action)

            if time.time() - self.last_refresh > 1:
                self.refresh()

    def teardown(self):
        for source in self.sources.values():
            source.teardown()