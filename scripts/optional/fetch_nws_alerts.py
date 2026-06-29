"""
fetch_nws_alerts.py  (OPTIONAL — demonstrates authoritative public-data ETL)
============================================================================
Pull LIVE active weather alerts for New Hampshire from the National Weather
Service public API (https://api.weather.gov, no API key required) and convert
them into the project's hazard-zone GeoJSON schema.

WHY THIS MATTERS for the GIS Solutions Engineer role:
  * Real ETL from an authoritative source — the core pipeline runs on SIMULATED
    data on purpose (safety). This optional script shows the *other half* of the
    job: ingesting real, public, government data and mapping its fields into a
    standard internal schema (schema mapping / data integration).
  * Resilience — it degrades gracefully when offline (no crash, clear message),
    the way a scheduled production job should.
  * Standards — sets a proper User-Agent (required by NWS API policy) and records
    data lineage (data_source, last_updated) on every feature.

This script is NOT part of the core pipeline. It writes to data/raw/ so it never
overwrites the simulated demo data. To actually feed it into the pipeline you
would point scripts 02/04 at the resulting file (documented as future work).

Run:  python scripts/optional/fetch_nws_alerts.py
Requires: internet access. No third-party packages (uses urllib + json).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

# api.weather.gov requires a descriptive User-Agent identifying the caller.
NWS_URL = "https://api.weather.gov/alerts/active?area=NH"
USER_AGENT = "concord-manchester-public-safety-gis (portfolio demo; contact via GitHub)"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PATH = os.path.join(REPO_ROOT, "data", "raw", "nws_hazard_zones.geojson")

# Map NWS severity vocabulary onto this project's severity domain.
SEVERITY_MAP = {
    "Extreme": "Critical", "Severe": "High",
    "Moderate": "Moderate", "Minor": "Low", "Unknown": "Low",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_alerts() -> dict:
    req = urllib.request.Request(NWS_URL, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/geo+json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def transform(raw: dict) -> dict:
    """Map NWS alert features into the project's hazard-zone schema."""
    features = []
    with_geom = 0
    for i, feat in enumerate(raw.get("features", []), start=1):
        props = feat.get("properties", {})
        geom = feat.get("geometry")  # often null for zone-based alerts
        if geom is not None:
            with_geom += 1
        features.append({
            "type": "Feature",
            "geometry": geom,  # GeoJSON permits null geometry
            "properties": {
                "hazard_id": f"NWS{i:03d}",
                "hazard_type": props.get("event", "Weather Alert"),
                "severity": SEVERITY_MAP.get(props.get("severity", "Unknown"), "Low"),
                "town": props.get("areaDesc", ""),
                "description": props.get("headline") or props.get("event", ""),
                "nws_id": props.get("id", ""),
                "effective": props.get("effective", ""),
                "expires": props.get("expires", ""),
                "data_source": "NWS api.weather.gov (public, authoritative)",
                "last_updated": now_iso(),
            },
        })
    return {"type": "FeatureCollection", "features": features,
            "_meta": {"source": NWS_URL, "fetched": now_iso(),
                      "total": len(features), "with_geometry": with_geom}}


def main() -> int:
    print(f"[nws] requesting active NH alerts from {NWS_URL} ...")
    try:
        raw = fetch_alerts()
    except Exception as exc:  # offline / DNS / timeout / HTTP error
        print(f"[nws] could not reach the NWS API ({type(exc).__name__}: {exc}).")
        print("[nws] This is expected with no internet. The core pipeline does NOT")
        print("[nws] depend on this script — it runs entirely on simulated data.")
        return 0  # graceful: not a pipeline failure

    fc = transform(raw)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(fc, fh, indent=2)

    meta = fc["_meta"]
    print(f"[nws] fetched {meta['total']} active alert(s); "
          f"{meta['with_geometry']} had polygon geometry.")
    print(f"[nws] wrote -> {os.path.relpath(OUT_PATH, REPO_ROOT)}")
    if meta["total"] == 0:
        print("[nws] (No active NH alerts right now — that's normal on a calm day.)")
    print("[nws] NOTE: this is REAL public data (not simulated). Review before "
          "combining it with the simulated demo layers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
