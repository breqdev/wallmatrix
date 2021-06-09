import sys

if len(sys.argv) < 2:
    raise ValueError("usage: wallmatrix {real|fake}")

if sys.argv[1] == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
elif sys.argv[1] == "fake":
    from wallmatrix.driver.fake import FakeMatrixDriver as Driver

__all__ = ["Driver"]