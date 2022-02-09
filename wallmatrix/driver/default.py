import os
import platform

if os.environ["DRIVER"] == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
else:
    from wallmatrix.driver.driver import MatrixDriver as Driver

__all__ = ["Driver"]
