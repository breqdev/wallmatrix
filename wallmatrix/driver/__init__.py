import time
import importlib
from pathlib import Path

import wallmatrix

class MatrixDriver:
    INTERVAL = 10

    def __init__(self):
        self.sources = {}
        self.current_source = None

        self.load_sources()

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
        if not self.current_source:
            return

        self.image = self.sources[self.current_source].get_image()

        self.update_image()

    def update_image(self):
        pass

    def loop(self):
        while True:
            start_time = time.time()

            self.refresh()

            time.sleep(max(0, self.INTERVAL + start_time - time.time()))

    def teardown(self):
        for source in self.sources.values():
            source.teardown()