from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware

import app.settings as settings
from app.logger import logger


app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/ping")
def ping():
    return {"data": "pong"}


@app.get("/api/v1/precipitation/point")
def get_precipitation_of_lnglat_point(
    longitude: float,
    latitude: float,
    key: Union[str, None] = None,
) -> Dict:
    _check_key(key)
    if not settings.is_lnglat_valid(longitude, latitude):
        raise HTTPException(
            status_code=400,
            detail="Invalid longitude or latitude value.",
        )

    # TODO: most recent year
    most_recent_date_path = sorted(settings.RESULT_DATA_SUBDIR.iterdir())[-1]
    most_recent_time_path = sorted(most_recent_date_path.iterdir())[-1]
    start_datetime_str = f"{most_recent_time_path.parent.name}{most_recent_time_path.name}"
    logger.info(
        f"Fetching precipitation on {start_datetime_str} "
        f"at ({longitude}, {latitude})"
    )

    png_data = _load_png_data(most_recent_time_path)
    data = _png_data_to_precipitation(png_data)
    x, y = _lnglat2xy(longitude, latitude)
    precipitation_series = np.clip(data[:, x, y], 0, 128) # FIXME: clarify the magic number 128
    start_timestamp = datetime.strptime(start_datetime_str, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).timestamp()
    return {
        'longitude': longitude,
        'latitude': latitude,
        'start_timestamp': start_timestamp,
        'forecast_interval': settings.FRAME_INTERVAL,
        'forecast_steps': 18,
        'precipitation': precipitation_series.tolist(),
        'unit': "mm/h",
    }


def _check_key(key: Union[str, None] = None):
    # Naive auth with fixed key
    if not key or key != settings.DEMO_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _load_png_data(png_dir_path: Path) -> List[np.ndarray]:
    png_paths = sorted(
        png_dir_path.iterdir(),
        key=lambda p: int(p.stem.replace("pd", "").replace("-min", "")),
    )
    png_data = []
    for path in png_paths:
        logger.info(f" -> Loading {path}")
        img = cv2.imread(str(path), 2) # FIXME: clarify the magic number 2
        png_data.append(np.expand_dims(img, axis=0))

    logger.info(f"Fetched data_type={np.concatenate(png_data, axis=0).dtype}")
    logger.info(f"Fetched data_shape={np.concatenate(png_data, axis=0).shape}")
    logger.info(f"Fetched data max={np.max(np.concatenate(png_data, axis=0))}")
    logger.info(f"Fetched data min={np.min(np.concatenate(png_data, axis=0))}")

    return png_data


def _png_data_to_precipitation(png_data: List[np.ndarray]) -> np.ndarray:
    return np.concatenate(png_data, axis=0).astype(np.float32) / 10.0 - 3.0


def _lnglat2xy(
    longitude: float,
    latitude: float,
    min_longitude: float = settings.RESULT_BOUNDING_MIN_LNG,
    max_longitude: float = settings.RESULT_BOUNDING_MAX_LNG,
    min_latitude: float = settings.RESULT_BOUNDING_MIN_LAT,
    max_latitude: float = settings.RESULT_BOUNDING_MAX_LAT,
    resolution_longitude: float = settings.RESULT_RESOLUTION_LNG,
    resolution_latitude: float = settings.RESULT_RESOLUTION_LAT,
) -> Tuple[int, int]:
    if not settings.is_lnglat_valid(longitude, latitude):
        raise ValueError("Invalid longitude or latitude value.")
    
    if not settings.is_lnglat_valid(min_longitude, min_latitude):
        raise ValueError("Invalid min_longitude or min_latitude value.")
    
    if not settings.is_lnglat_valid(max_longitude, max_latitude):
        raise ValueError("Invalid max_longitude or max_latitude value.")
    
    if longitude < min_longitude or longitude > max_longitude:
        raise ValueError(
            f"longitude {longitude} is out of given range "
            f"[{min_longitude}, {max_longitude}]."
        )

    if latitude < min_latitude or latitude > max_latitude:
        raise ValueError(
            f"latitude {latitude} is out of given range "
            f"[{min_latitude}, {max_latitude}]."
        )

    return (
        int((latitude - min_latitude) / resolution_latitude),
        int((longitude - min_longitude) / resolution_longitude),
    )
