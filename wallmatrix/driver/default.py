import os

if os.environ["DRIVER"] == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
elif os.environ["DRIVER"] == "fake":
    from wallmatrix.driver.fake import FakeMatrixDriver as Driver

__all__ = ["Driver"]