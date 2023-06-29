import os
from pathlib import Path


DEMO_KEY = os.environ.get('DEMO_KEY', "demo")

__DATA_WORKSPACE_STR__ = os.environ.get('DATA_WORKSPACE', "/data")
DATA_WORKSPACE: Path = Path(__DATA_WORKSPACE_STR__)
DATA_WORKSPACE.mkdir(parents=True, exist_ok=True)

__RESULT_DATA_SUBDIR_STR__ = os.environ.get('RESULT_DATA_SUBDIR', "results/NowcastNet")
RESULT_DATA_SUBDIR: Path = DATA_WORKSPACE / __RESULT_DATA_SUBDIR_STR__
RESULT_DATA_SUBDIR.mkdir(parents=True, exist_ok=True)

RESULT_BOUNDING_MIN_LNG = float(os.environ.get('RESULT_BOUNDING_MIN_LNG', -130.0))
RESULT_BOUNDING_MAX_LNG = float(os.environ.get('RESULT_BOUNDING_MAX_LNG', -60.0))
RESULT_BOUNDING_MIN_LAT = float(os.environ.get('RESULT_BOUNDING_MIN_LAT', 20.0))
RESULT_BOUNDING_MAX_LAT = float(os.environ.get('RESULT_BOUNDING_MAX_LAT', 55.0))

def is_lnglat_valid(longitude: float, latitude: float):
    return (
        longitude is not None
        and -180 <= longitude <= 180
        and latitude is not None
        and -90 <= latitude <= 90
    )

if not is_lnglat_valid(RESULT_BOUNDING_MIN_LNG, RESULT_BOUNDING_MIN_LAT):
    raise ValueError("Invalid RESULT_BOUNDING_MIN_LNG or RESULT_BOUNDING_MIN_LAT")

if not is_lnglat_valid(RESULT_BOUNDING_MAX_LNG, RESULT_BOUNDING_MAX_LAT):
    raise ValueError("Invalid RESULT_BOUNDING_MAX_LNG or RESULT_BOUNDING_MAX_LAT")

RESULT_RESOLUTION_LNG = float(os.environ.get('RESULT_RESOLUTION_LNG', 0.02))
RESULT_RESOLUTION_LAT = float(os.environ.get('RESULT_RESOLUTION_LAT', 0.02))

FRAME_INTERVAL = os.environ.get('FRAME_INTERVAL', "10m")
