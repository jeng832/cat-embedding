# src/cat_embedding/geo.py
import numpy as np
from typing import Optional, Tuple
from PIL import Image, ExifTags

def normalize_latlon(lat: Optional[float], lon: Optional[float],
                     bounds: Optional[Tuple[float,float,float,float]] = None) -> np.ndarray:
    # bounds = (min_lat, max_lat, min_lon, max_lon)
    if lat is None or lon is None or bounds is None:
        return np.zeros(2, dtype=float)
    min_lat, max_lat, min_lon, max_lon = bounds
    if max_lat == min_lat or max_lon == min_lon:
        return np.zeros(2, dtype=float)
    nlat = (lat - min_lat) / (max_lat - min_lat)
    nlon = (lon - min_lon) / (max_lon - min_lon)
    return np.clip(np.array([nlat, nlon], dtype=float), 0.0, 1.0)


def _rational_to_float(value) -> float:
    """Converts a PIL Exif rational or tuple to float.

    Handles PIL's IFDRational type and (numerator, denominator) tuples.
    """
    try:
        # PIL.IFDRational has numerator/denominator attributes
        numerator = getattr(value, "numerator", None)
        denominator = getattr(value, "denominator", None)
        if numerator is not None and denominator:
            return float(numerator) / float(denominator)
    except Exception:
        pass

    if isinstance(value, tuple) and len(value) == 2 and value[1] not in (0, None):
        return float(value[0]) / float(value[1])

    # Fallback
    return float(value)


def _dms_to_degrees(dms, ref: str) -> Optional[float]:
    """Convert EXIF GPS DMS format to decimal degrees.

    dms is typically a sequence of three rationals: (deg, min, sec).
    ref is one of 'N','S','E','W'.
    """
    if not dms or len(dms) != 3:
        return None
    try:
        degrees = _rational_to_float(dms[0])
        minutes = _rational_to_float(dms[1])
        seconds = _rational_to_float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None


def extract_gps_from_image(image_path: str) -> Optional[Tuple[float, float]]:
    """Extract (lat, lon) from image EXIF GPS if available.

    Returns None if GPS is not present or cannot be parsed.
    """
    try:
        img = Image.open(image_path)
        # Pillow >= 6: use getexif(); older: _getexif()
        exif = getattr(img, "getexif", None)
        exif_data = exif() if callable(exif) else getattr(img, "_getexif", lambda: None)()
        if not exif_data:
            return None

        # GPSInfo tag id in EXIF is 34853
        gps_tag_id = None
        for tag_id, tag_name in ExifTags.TAGS.items():
            if tag_name == "GPSInfo":
                gps_tag_id = tag_id
                break
        if gps_tag_id is None or gps_tag_id not in exif_data:
            return None

        gps_info = exif_data[gps_tag_id]
        # gps_info can be a dict keyed by ints; translate keys using GPSTAGS names
        gps = {}
        for key, val in getattr(gps_info, "items", lambda: [])():
            name = ExifTags.GPSTAGS.get(key, key)
            gps[name] = val

        lat_ref = gps.get("GPSLatitudeRef")
        lat_dms = gps.get("GPSLatitude")
        lon_ref = gps.get("GPSLongitudeRef")
        lon_dms = gps.get("GPSLongitude")
        if not lat_ref or not lat_dms or not lon_ref or not lon_dms:
            return None

        lat = _dms_to_degrees(lat_dms, lat_ref)
        lon = _dms_to_degrees(lon_dms, lon_ref)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except Exception:
        # Any error leads to graceful fallback to None
        return None
