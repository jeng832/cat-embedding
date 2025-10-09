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
        # exifread 라이브러리 사용 (더 안정적)
        import exifread
        
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=True)
        
        # GPS 정보 추출
        gps_latitude = tags.get('GPS GPSLatitude')
        gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
        gps_longitude = tags.get('GPS GPSLongitude')
        gps_longitude_ref = tags.get('GPS GPSLongitudeRef')
        
        if not gps_latitude or not gps_longitude:
            return None
        
        # DMS를 십진도로 변환
        def dms_to_decimal(dms_str):
            if dms_str:
                parts = str(dms_str).strip('[]').split(', ')
                if len(parts) == 3:
                    degrees = float(parts[0])
                    minutes = float(parts[1])
                    
                    # 초 단위 처리 (분수 포함)
                    seconds_str = parts[2]
                    if '/' in seconds_str:
                        numerator, denominator = seconds_str.split('/')
                        seconds = float(numerator) / float(denominator)
                    else:
                        seconds = float(seconds_str)
                    
                    return degrees + (minutes / 60.0) + (seconds / 3600.0)
            return None
        
        lat_decimal = dms_to_decimal(gps_latitude)
        lon_decimal = dms_to_decimal(gps_longitude)
        
        if lat_decimal and lon_decimal:
            # 남위/서경 처리
            if str(gps_latitude_ref) == 'S':
                lat_decimal = -lat_decimal
            if str(gps_longitude_ref) == 'W':
                lon_decimal = -lon_decimal
            
            return float(lat_decimal), float(lon_decimal)
        else:
            return None
            
    except Exception as e:
        # Any error leads to graceful fallback to None
        return None
