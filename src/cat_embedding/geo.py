# src/cat_embedding/geo.py
import numpy as np
from typing import Optional, Tuple

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
