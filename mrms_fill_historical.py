import os
import time
from datetime import datetime, timedelta, timezone

import anylearn

from mrms import round_down, MrmsTimer, MrmsIsuDownloader
from mrms.logger import logger


if os.environ.get('ANYLEARN_TASK_ID', None) is not None:
    data_workspace = anylearn.get_dataset("yhuang/MRMS").download()
else:
    data_workspace = "./data"


def run(start_dt: datetime, end_dt: datetime, debouncing_seconds: int=1):
    timer = MrmsTimer()
    downloader = MrmsIsuDownloader(base_dir=data_workspace)

    datetime_collection = []
    _from = round_down(start_dt, timer.interval) + timer.interval
    _to = round_down(end_dt, timer.interval)
    while _from < _to:
        datetime_collection.append(_from)
        _from += timer.interval

    errors = []
    for dt in datetime_collection:
        try:
            if downloader.save_path(dt).exists():
                logger.info(f"Skipping {dt}")
                continue
            if not downloader.download1(dt):
                errors.append(dt)
            time.sleep(debouncing_seconds)
        except Exception as e:
            logger.error(f"Failed to download {dt}: {e}")
            errors.append(dt)

    logger.error(f"/!\ Errors: {errors}")
    return errors


if __name__ == "__main__":
    start = datetime.now(timezone.utc) - timedelta(weeks=1)
    end = datetime.now(timezone.utc) - timedelta(days=1)
    run(start, end)
