import os
import platform

if os.environ["DRIVER"] == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
elif os.environ["DRIVER"] == "fake":
    if platform.system() == "Darwin":
        from wallmatrix.driver.fake_macos import FakeMatrixDriver as Driver
    else:
        from wallmatrix.driver.fake import FakeMatrixDriver as Driver

__all__ = ["Driver"]