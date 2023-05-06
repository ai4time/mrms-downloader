import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from mrms.logger import logger


class MRMSDownloader:
    def run(self):
        while True:
            self._poll()
            time.sleep(600)

    def _poll(self):
        ### Note: all times should be in UTC
        ### Note: there is a 2-minute delay for a file to be online
        now = datetime.utcnow() - timedelta(minutes=2)

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

        base_dir = Path("data")
        save_dir = base_dir / str(last.year) / f"{last.month:02d}{last.day:02d}"
        save_dir.mkdir(parents=True, exist_ok=True)

        save_path = save_dir / filename
        self._download(url, save_path)

    def _download(self, url: str, save_path: os.PathLike) -> None:
        logger.info(f"Downloading {url}...")
        res = requests.get(url)
        res.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(res.content)
        logger.info(f"Saved to {save_path}")
