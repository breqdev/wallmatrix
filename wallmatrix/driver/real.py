from PIL import Image

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    RGBMatrix = None
    RGBMatrixOptions = None

from wallmatrix.driver import MatrixDriver


class RealMatrixDriver(MatrixDriver):
    def setup(self):
        self.options = RGBMatrixOptions()
        self.options.rows = 16
        self.options.drop_privileges = False

        self.matrix = RGBMatrix(options=self.options)

    def update_image(self):
        self.matrix.SetImage(self.image.convert("RGB"))

    def teardown(self):
        pass
