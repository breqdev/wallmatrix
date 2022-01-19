import argparse
import time

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(
    prog="wallmatrix",
    description="Run or simulate the RGB matrix"
)

parser.add_argument("driver", choices=["real", "fake", "fake_macos"])


args = parser.parse_args()


if args.driver == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
elif args.driver == "fake":
    from wallmatrix.driver.fake import FakeMatrixDriver as Driver
elif args.driver == "fake_macos":
    from wallmatrix.driver.fake_macos import FakeMatrixDriver as Driver


driver = Driver()
driver.setup()
driver.current_source = next(iter(driver.sources))

# from wallmatrix.sources.colorbars import Colorbars as Source
# from wallmatrix.sources.weather import Weather as Source
# from wallmatrix.sources.mbta import MBTA as Source

try:
    driver.loop()
finally:
    driver.teardown()