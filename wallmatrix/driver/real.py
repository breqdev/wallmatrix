import os

from PIL import Image

from rgbmatrix import RGBMatrix, RGBMatrixOptions

from wallmatrix.driver import MatrixDriver


class RealMatrixDriver(MatrixDriver):
    def setup(self):
        self.options = RGBMatrixOptions()
        self.options.rows = 16
        self.options.drop_privileges = False

        self.matrix = RGBMatrix(options=self.options)

    def update_image(self):
        image = self.image.convert("RGB")
        if os.environ.get("INVERT"):
            image = image.rotate(180)

        self.matrix.SetImage(image)

    def teardown(self):
        super().teardown()

        self.matrix.Clear()
