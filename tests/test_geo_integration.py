import numpy as np
import os
import sys
from types import ModuleType
from PIL import Image
import pytest

from cat_embedding.schema import CatMeta
from cat_embedding.geo import extract_gps_from_image


def _with_stubbed_sklearn_import_gallery(monkeypatch):
    """Import cat_embedding.gallery with a stubbed sklearn.metrics.pairwise.

    This avoids installing scikit-learn on Python 3.13 where wheels may be unavailable.
    """
    # Build stub hierarchy: sklearn -> sklearn.metrics -> sklearn.metrics.pairwise
    sklearn_stub = ModuleType("sklearn")
    metrics_stub = ModuleType("sklearn.metrics")
    pairwise_stub = ModuleType("sklearn.metrics.pairwise")

    def cosine_similarity(X, Y):
        X = np.asarray(X)
        Y = np.asarray(Y)
        # Very simple cosine sim (not used in these tests)
        x = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
        y = Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)
        return x @ y.T

    pairwise_stub.cosine_similarity = cosine_similarity
    metrics_stub.pairwise = pairwise_stub

    monkeypatch.setitem(sys.modules, "sklearn", sklearn_stub)
    monkeypatch.setitem(sys.modules, "sklearn.metrics", metrics_stub)
    monkeypatch.setitem(sys.modules, "sklearn.metrics.pairwise", pairwise_stub)

    import importlib
    return importlib.import_module("cat_embedding.gallery")


def _make_temp_image(path: str, size=(10, 10), color=(128, 128, 128)):
    img = Image.new("RGB", size, color)
    img.save(path)


def test_extract_gps_from_image_returns_none_without_exif(tmp_path):
    img_path = os.path.join(tmp_path, "no_exif.jpg")
    _make_temp_image(img_path)
    assert extract_gps_from_image(img_path) is None


def test_build_vector_uses_exif_when_latlon_missing(monkeypatch, tmp_path):
    # Arrange: image file
    img_path = os.path.join(tmp_path, "img.jpg")
    _make_temp_image(img_path)

    gallery = _with_stubbed_sklearn_import_gallery(monkeypatch)

    # Stub image_embedding to a small fixed vector to keep test light
    monkeypatch.setattr(gallery, "image_embedding", lambda p: np.ones(8, dtype=float))

    # Capture lat/lon sent into normalize_latlon
    captured = {}

    def fake_normalize(lat, lon, bounds=None):
        captured["lat"], captured["lon"], captured["bounds"] = lat, lon, bounds
        return np.array([0.5, 0.5], dtype=float)

    monkeypatch.setattr(gallery, "normalize_latlon", fake_normalize)

    # Provide EXIF GPS via stub (we are testing integration behavior, not EXIF parsing here)
    monkeypatch.setattr(gallery, "extract_gps_from_image", lambda p: (37.1, 127.2))

    meta = CatMeta(image_path=img_path)

    # Act
    vec = gallery.build_vector(meta, bounds=(36.0, 38.0, 126.0, 128.0))

    # Assert: normalize_latlon should have received EXIF-derived values
    assert captured["lat"] == 37.1 and captured["lon"] == 127.2
    # Vector should be non-empty and normalized
    assert isinstance(vec, np.ndarray) and vec.size > 0
    # Final vector should be L2-normalized (approximately 1)
    norm = float(np.linalg.norm(vec))
    assert 0.99 <= norm <= 1.01


def test_build_vector_uses_provided_latlon_when_present(monkeypatch, tmp_path):
    img_path = os.path.join(tmp_path, "img2.jpg")
    _make_temp_image(img_path)

    gallery = _with_stubbed_sklearn_import_gallery(monkeypatch)

    monkeypatch.setattr(gallery, "image_embedding", lambda p: np.ones(8, dtype=float))

    # Make EXIF extraction raise if called; it must NOT be called when lat/lon provided
    def exif_should_not_be_called(_):
        raise AssertionError("extract_gps_from_image should not be called when lat/lon provided")

    monkeypatch.setattr(gallery, "extract_gps_from_image", exif_should_not_be_called)

    captured = {}

    def fake_normalize(lat, lon, bounds=None):
        captured["lat"], captured["lon"], captured["bounds"] = lat, lon, bounds
        return np.array([0.25, 0.75], dtype=float)

    monkeypatch.setattr(gallery, "normalize_latlon", fake_normalize)

    meta = CatMeta(image_path=img_path, lat=35.5, lon=127.7)

    vec = gallery.build_vector(meta, bounds=(30.0, 40.0, 120.0, 130.0))

    assert captured["lat"] == 35.5 and captured["lon"] == 127.7
    assert isinstance(vec, np.ndarray) and vec.size > 0
    norm = float(np.linalg.norm(vec))
    assert 0.99 <= norm <= 1.01
