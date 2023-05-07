import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from mrms.logger import logger


class MRMSDownloader:

    def __init__(self, base_dir: os.PathLike="data"):
        self.base_dir = Path(base_dir)

    def run(self):
        while True:
            _wait = self._poll()
            time.sleep(_wait)

    def _poll(self):
        ### Note: all times should be in UTC
        ### Note: there is a 2-minute delay for a file to be online
        now = datetime.now(timezone.utc) - timedelta(minutes=2)

        # Round down to nearest 10 minutes
        last = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=(now.minute // 10) * 10,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )

        dt_str = datetime.strftime(last, "%Y%m%d-%H%M%S")
        filename = f"MRMS_PrecipRate_00.00_{dt_str}.grib2.gz"
        url = f"https://mrms.ncep.noaa.gov/data/2D/PrecipRate/{filename}"

        save_dir = self._ensure_save_dir(dt=last)
        save_path = save_dir / filename

        try:
            self._download(url, save_path)
            return self._wait_time(now=now, last=last)
        except HTTPError as e:
            _status = e.response.status_code
            logger.error(
                f"Failed to download {url}: "
                f"[{_status}] {e.response.reason}"
            )
            if _status == 404:
                # Possibly a time nuance that the file is not online yet
                # Just wait for a short time and retry
                return 10

    def _ensure_save_dir(self, dt: datetime) -> os.PathLike:
        save_dir = self.base_dir / str(dt.year) / f"{dt.month:02d}{dt.day:02d}"
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def _download(self, url: str, save_path: os.PathLike) -> None:
        logger.info(f"Downloading {url}...")
        res = requests.get(url)
        res.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(res.content)
        logger.info(f"Saved to {save_path}")

    def _wait_time(self, now: datetime, last: datetime) -> int:
        # Wait until the next 10-minute mark
        next = last + timedelta(minutes=10)
        wait_time = (next - now).total_seconds()
        return int(wait_time)
