import os

from PIL import Image

from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

from wallmatrix.driver.driver import MatrixDriver


class RealMatrixDriver(MatrixDriver):
    def setup(self):
        self.options = RGBMatrixOptions()
        self.options.rows = 16
        self.options.drop_privileges = False

        self.matrix = RGBMatrix(options=self.options)

    def update_image(self):
        if os.environ.get("INVERT"):
            image = self.image.rotate(180)
        else:
            image = self.image.rotate(0)

        self.matrix.SetImage(image.convert("RGB"))

    def teardown(self):
        super().teardown()

        self.matrix.Clear()
