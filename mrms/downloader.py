import abc
import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from mrms.logger import logger


class AbstractDownloader(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def download1(self, dt: datetime) -> bool:
        raise NotImplementedError


class MrmsDownloader(AbstractDownloader):

    def __init__(self, base_dir: os.PathLike="data"):
        super().__init__()
        self.base_dir = Path(base_dir)

    def download1(self, dt: datetime) -> bool:
        dt_str = datetime.strftime(dt, "%Y%m%d-%H%M%S")
        remote_filename = f"MRMS_PrecipRate_00.00_{dt_str}.grib2.gz"
        local_filename = f"PrecipRate_00.00_{dt_str}.grib2.gz"
        url = f"https://mrms.ncep.noaa.gov/data/2D/PrecipRate/{remote_filename}"

        save_dir = self._ensure_save_dir(dt)
        save_path = save_dir / local_filename

        try:
            self._download(url, save_path)
            self._2png(save_path)
            return True
        except HTTPError as e:
            _status = e.response.status_code
            logger.error(
                f"Failed to download {url}: "
                f"[{_status}] {e.response.reason}"
            )
            return False

    def _ensure_save_dir(self, dt: datetime) -> os.PathLike:
        save_dir = self.base_dir / str(dt.year) / f"{dt.month:02d}" / f"{dt.day:02d}" / "mrms" / "ncep" / "PrecipRate"
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def _download(self, url: str, save_path: os.PathLike) -> None:
        logger.info(f"Downloading {url}...")
        res = requests.get(url)
        res.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(res.content)
        logger.info(f"Saved to {save_path}")

    def _2png(self, grib2gz_path: os.PathLike) -> None:
        import gzip

        import cv2
        import pygrib

        # Unzip to get grib2
        grib2gz_path = Path(grib2gz_path)
        with gzip.open(grib2gz_path, 'rb') as fin:
            grib2_path = grib2gz_path.with_suffix('')
            with open(grib2_path, 'wb') as fout:
                shutil.copyfileobj(fin, fout)

        data = pygrib.open(str(grib2_path))
        for var in data:
            precip = var['values']
        data.close()

        precip = (precip+3)*10
        precip = precip.astype('int16')

        png_save_path = grib2_path.with_suffix('.png')
        cv2.imwrite(str(png_save_path), precip)
        logger.info(f"Converted to {png_save_path}")


class TjwfSimulatedDownloader(AbstractDownloader):

    def __init__(
        self,
        source_dir: os.PathLike="data",
        target_dir: os.PathLike="data",
    ):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)

    def download1(self, dt: datetime) -> bool:
        # Construct filename
        dt_str = datetime.strftime(dt, "%Y%m%d%H%M%S")
        filename = f"Z_OTHE_RADAMCR_{dt_str}.bin.bz2"

        # Construct source path
        source_date_dir = self.source_dir / str(dt.year) / datetime.strftime(dt, "%Y%m%d")
        source_path = source_date_dir / filename
        if not source_path.exists():
            logger.warning(f"Source file {source_path} does not exist")
            source_path = source_date_dir / "RADAR_MOSAIC" / "MCR" / filename
            logger.warning(f"Trying {source_path}")
            if not source_path.exists():
                logger.error(f"Source file {source_path} does not exist")
                return

        # Make target save path
        save_dir = self._ensure_save_dir(dt=dt)
        save_path = save_dir / filename

        self._download(source_path, save_path)

    def _ensure_save_dir(self, dt: datetime) -> os.PathLike:
        save_dir = self.target_dir / str(dt.year) / datetime.strftime(dt, "%Y%m%d")
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def _download(self, source_path: os.PathLike, save_path: os.PathLike) -> None:
        logger.info(f"Copying {source_path}...")
        shutil.copy(str(source_path), str(save_path))
        logger.info(f"Saved to {save_path}")


class OldMRMSDownloader:

    def __init__(
        self,
        base_dir: os.PathLike="data",
        tz: datetime.tzinfo=timezone.utc,
    ):
        self.base_dir = Path(base_dir)
        self.tz = tz

    def run(self):
        while True:
            _wait = self._poll()
            time.sleep(_wait)

    def _poll(self):
        ### Note: there is a 2-minute delay for a file to be online
        # TODO: make the delay generic
        now = datetime.now(self.tz) - timedelta(minutes=2)

        # Round down to nearest 10 minutes
        # TODO: make the interval generic
        last = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=(now.minute // 10) * 10,
            second=0,
            microsecond=0,
            tzinfo=self.tz,
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
