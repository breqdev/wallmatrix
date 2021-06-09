import os

if os.getenv("MATRIX_DRIVER") == "REAL":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
else:
    from wallmatrix.driver.fake import FakeMatrixDriver as Driver

__all__ = ["Driver"]