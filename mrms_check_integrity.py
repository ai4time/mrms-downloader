import os
from datetime import datetime, timedelta
from pathlib import Path

import anylearn


def run():
    if os.environ.get('ANYLEARN_TASK_ID', None) is not None:
        data_workspace = anylearn.get_dataset("yhuang/MRMS").download()
    else:
        data_workspace = "./data"
    data_workspace = Path(data_workspace)

    missing = []

    curr = datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0)
    end = datetime(year=2023, month=7, day=13, hour=0, minute=0, second=0)
    while curr < end:
        dt_dir_str = datetime.strftime(curr, "%Y/%m/%d/mrms/ncep/PrecipRate")
        dt_file_str = datetime.strftime(curr, "%Y%m%d-%H%M%S")
        filename = f"MRMS_PrecipRate_00.00_{dt_file_str}.grib2.gz"
        path = data_workspace / dt_dir_str / filename
        if not path.exists():
            missing.append(dt_file_str)
        curr += timedelta(minutes=2)

if __name__ == "__main__":
    run()
