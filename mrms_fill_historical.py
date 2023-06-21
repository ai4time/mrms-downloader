import argparse
import os
import time
from datetime import datetime, timedelta, timezone

import anylearn

from ingestion import round_down, MrmsTimer, MrmsIsuDownloader
from ingestion.logger import logger


if os.environ.get('ANYLEARN_TASK_ID', None) is not None:
    data_workspace = anylearn.get_dataset("yhuang/MRMS").download()
else:
    data_workspace = "./data"


def run(
    start_dt: datetime,
    end_dt: datetime,
    force_overwrite: bool = False,
    debouncing_seconds: int = 1,
):
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
        if not download(downloader, dt, force_overwrite):
            errors.append(dt)
        time.sleep(debouncing_seconds)

    logger.error(f"/!\ Errors: {errors}")
    return errors


def download(
    downloader: MrmsIsuDownloader,
    dt: datetime,
    force_overwrite: bool = False,
) -> bool:
    try:
        if not force_overwrite and downloader.save_path(dt).exists():
            logger.info(f"Skipping {dt}")
            return True
        return downloader.download1(dt)
    except Exception as e:
        logger.error(f"Failed to download {dt}: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MRMS downloader filling missing data")
    parser.add_argument(
        "--start",
        type=str,
        default=(datetime.now(timezone.utc) - timedelta(weeks=1)).strftime("%Y%m%d%H%M%S"),
        help="start time in format of YYYYMMDDHHMMSS.",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=(datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d%H%M%S"),
        help="end time in format of YYYYMMDDHHMMSS.",
    )
    parser.add_argument(
        "--timezone-offset-hours",
        type=str,
        default="0",
        help="timezone offset in hours, example: +8 for Asia/Shanghai. Default UTC.",
    )
    parser.add_argument(
        "--force-overwrite",
        action="store_true",
        help="force overwrite existing files.",
    )
    
    args = parser.parse_args()
    tz = timezone(timedelta(hours=int(args.timezone_offset_hours)))
    start = datetime.strptime(args.start, "%Y%m%d%H%M%S").replace(tzinfo=tz)
    end = datetime.strptime(args.end, "%Y%m%d%H%M%S").replace(tzinfo=tz)
    force_overwrite = args.force_overwrite
    run(start, end, force_overwrite)
