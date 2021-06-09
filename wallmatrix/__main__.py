import argparse
import time

parser = argparse.ArgumentParser(
    prog="wallmatrix",
    description="Run or simulate the RGB matrix"
)

parser.add_argument("driver", choices=["real", "fake"])


args = parser.parse_args()


if args.driver == "real":
    from wallmatrix.driver.real import RealMatrixDriver as Driver
elif args.driver == "fake":
    from wallmatrix.driver.fake import FakeMatrixDriver as Driver


driver = Driver()
driver.setup()

# from wallmatrix.sources.colorbars import Colorbars as Source
# from wallmatrix.sources.weather import Weather as Source
from wallmatrix.sources.mbta import MBTA as Source

source = Source()
source.setup()

driver.sources.append(source)
driver.current_source = source

try:
    driver.loop()
finally:
    source.teardown()