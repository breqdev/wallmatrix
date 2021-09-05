from wallmatrix.driver import MatrixDriver

# TkInter doesn't run in background threads on MacOS
# Thus, we need a MacOS-specific fake driver

class FakeMatrixDriver(MatrixDriver):
    def setup(self):
        self.old_image = None

    def update_image(self):
        if self.image != self.old_image:
            self.image.show()
            self.old_image = self.image
