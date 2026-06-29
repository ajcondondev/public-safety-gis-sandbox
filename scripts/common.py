"""
common.py — shared helpers for the Public Safety GIS pipeline.

GIS Solutions Engineer skills demonstrated here:
  * Automation / reusability — one place for config loading, paths, logging,
    distance math, and GeoJSON writing so every pipeline stage behaves the same.
  * Open-source first — GeoJSON is built with the standard-library `json`
    module and distances use a pure-Python haversine formula, so the pipeline
    runs with ONLY pandas + PyYAML. GeoPandas/Shapely are optional accelerators.

This module has NO heavy dependencies. Importing it will not fail if GeoPandas
is missing; HAS_GEOPANDAS simply reports whether the optional stack is present.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from datetime import datetime, timezone

import yaml

# --- Optional geospatial stack detection -------------------------------------
# The pipeline degrades gracefully: if GeoPandas/Shapely are installed we can do
# true point-in-polygon work; if not, we use lightweight pure-Python fallbacks.
try:
    import geopandas  # noqa: F401
    import shapely  # noqa: F401

    HAS_GEOPANDAS = True
except Exception:  # pragma: no cover - depends on environment
    HAS_GEOPANDAS = False


# --- Paths -------------------------------------------------------------------
# Resolve everything relative to the repository root (the parent of /scripts),
# so the pipeline works no matter which directory you launch it from.
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)


def repo_path(*parts: str) -> str:
    """Build an absolute path inside the repository."""
    return os.path.join(REPO_ROOT, *parts)


# --- Configuration -----------------------------------------------------------
def load_config() -> dict:
    """
    Load config/config.yml if present, else fall back to config.example.yml.
    Demonstrates configuration-driven workflows (no magic numbers in scripts).
    """
    local = repo_path("config", "config.yml")
    example = repo_path("config", "config.example.yml")
    path = local if os.path.exists(local) else example
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_config_path"] = path
    return cfg


def ensure_dirs(cfg: dict) -> None:
    """Create every output directory named in the config (idempotent)."""
    for key in ("simulated", "processed", "outputs", "geojson",
                "dashboard_tables", "reports", "maps"):
        rel = cfg["paths"].get(key)
        if rel:
            os.makedirs(repo_path(rel), exist_ok=True)


# --- Logging -----------------------------------------------------------------
def log(message: str) -> None:
    """Tiny timestamped console logger (keeps run output readable & auditable)."""
    stamp = now_iso(seconds=True)
    line = f"[{stamp}] {message}"
    try:
        print(line)
    except UnicodeEncodeError:
        # Windows consoles default to cp1252 and choke on emoji/unicode. Degrade
        # gracefully so a logging glyph never crashes the pipeline.
        enc = (sys.stdout.encoding or "ascii")
        print(line.encode(enc, errors="replace").decode(enc))


def now_iso(seconds: bool = False) -> str:
    """UTC ISO-8601 timestamp; used for log lines and `last_updated` stamps."""
    fmt = "%Y-%m-%dT%H:%M:%SZ" if seconds else "%Y-%m-%d"
    return datetime.now(timezone.utc).strftime(fmt)


# --- Distance / geometry math (pure Python) ----------------------------------
EARTH_RADIUS_MILES = 3958.7613


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance in miles between two WGS84 points.

    Used for incident -> facility proximity analysis without needing a
    projected CRS or GeoPandas. Accurate to well within the tolerance needed
    for regional emergency-planning distance rings.
    """
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_MILES * 2 * math.asin(math.sqrt(a))


def point_in_ring(lat: float, lon: float, ring: list) -> bool:
    """
    Ray-casting point-in-polygon test for a single GeoJSON linear ring.
    `ring` is a list of [lon, lat] pairs. Pure Python — no Shapely required.
    """
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        intersect = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def point_in_polygon_feature(lat: float, lon: float, feature: dict) -> bool:
    """
    Point-in-polygon against a GeoJSON Polygon/MultiPolygon feature, honoring
    holes (a point inside a hole is treated as outside).
    """
    geom = feature.get("geometry", {})
    gtype = geom.get("type")
    coords = geom.get("coordinates", [])
    polygons = coords if gtype == "MultiPolygon" else [coords]
    for poly in polygons:
        if not poly:
            continue
        if point_in_ring(lat, lon, poly[0]):  # outer ring
            in_hole = any(point_in_ring(lat, lon, hole) for hole in poly[1:])
            if not in_hole:
                return True
    return False


# --- GeoJSON writing (standard library only) ---------------------------------
def points_to_geojson(rows, lat_field="latitude", lon_field="longitude"):
    """
    Convert an iterable of dict-like rows into a GeoJSON FeatureCollection of
    Points. Rows missing/invalid coordinates are skipped (they are caught
    separately by the validation stage). Returns (geojson_dict, skipped_count).
    """
    features = []
    skipped = 0
    for row in rows:
        lat, lon = row.get(lat_field), row.get(lon_field)
        try:
            lat_f, lon_f = float(lat), float(lon)
            if math.isnan(lat_f) or math.isnan(lon_f):
                raise ValueError
        except (TypeError, ValueError):
            skipped += 1
            continue
        props = {k: _json_safe(v) for k, v in row.items()
                 if k not in (lat_field, lon_field)}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon_f, lat_f]},
            "properties": props,
        })
    return {"type": "FeatureCollection", "features": features}, skipped


def _json_safe(value):
    """Coerce pandas/NaN values into JSON-serializable primitives."""
    try:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
    except TypeError:
        pass
    return value


def write_geojson(geojson_dict: dict, path: str) -> None:
    """Write a GeoJSON dict to disk with stable, human-diffable formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(geojson_dict, fh, indent=2)


def read_geojson(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_csv(path: str, fieldnames, rows) -> None:
    """Write a list of dict rows to CSV (used for dashboard/summary tables)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
