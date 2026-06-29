"""
04_generate_analysis_layers.py
==============================
Derive the analytical layers that turn raw locations into decision-support:
  1. Incident -> nearest emergency facility proximity (distance + ring).
  2. Hazard exposure flags (which facilities/shelters/incidents fall inside a
     simulated hazard zone).
  3. An incident PRIORITY score combining severity, open status, and hazard
     exposure, with a plain-English priority category.

GIS Solutions Engineer mapping:
  * Geospatial analysis — distance/proximity and point-in-polygon overlay are
    the bread-and-butter of "use data layers to support response planning."
  * Decision support — the priority category is the kind of derived indicator an
    emergency manager actually acts on (which incident to look at first).
  * Open-source first — uses the pure-Python haversine + ray-casting helpers in
    common.py, so it runs without GeoPandas. If GeoPandas IS installed the same
    logic still holds; see docs for how this maps to ArcGIS Pro Near/Buffer.

Outputs (outputs/geojson + outputs/dashboard_tables):
  * incidents_analyzed.geojson      — incidents enriched with nearest-facility,
                                       hazard flag, priority score & category.
  * incident_facility_proximity.csv — one row per valid incident.
  * facility_hazard_exposure.csv    — facilities/shelters/hospitals + hazard flag.

Run:  python scripts/04_generate_analysis_layers.py
"""

from __future__ import annotations

import pandas as pd

from common import (load_config, ensure_dirs, log, repo_path, haversine_miles,
                    points_to_geojson, write_geojson, read_geojson, write_csv)

SEVERITY_WEIGHT = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}


def load_processed(cfg: dict, fname: str) -> pd.DataFrame:
    return pd.read_csv(repo_path(cfg["paths"]["processed"], fname))


def valid_points(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Keep only rows whose coordinates are present AND within the study-area
    bounds from config. Records that fail coordinate validation (missing or
    out-of-range) are excluded from analysis so they cannot pollute the derived
    layers or maps — QA (script 03) reports them separately. This mirrors the
    rule "don't analyze data that failed validation."
    """
    v = cfg["validation"]
    df = df.copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    in_range = (df["latitude"].between(v["lat_min"], v["lat_max"]) &
                df["longitude"].between(v["lon_min"], v["lon_max"]))
    return df[in_range]


def nearest_facility(lat, lon, facilities: pd.DataFrame):
    """Return (facility_row, distance_miles) of the closest operational facility."""
    best, best_d = None, float("inf")
    for _, f in facilities.iterrows():
        d = haversine_miles(lat, lon, f["latitude"], f["longitude"])
        if d < best_d:
            best, best_d = f, d
    return best, best_d


def proximity_ring(distance: float, rings: list) -> str:
    """Bucket a distance into the configured analysis rings."""
    for r in sorted(rings):
        if distance <= r:
            return f"<= {r:g} mi"
    return f"> {max(rings):g} mi"


def hazard_exposed(lat, lon, hazard_features: list) -> str | None:
    """Return the hazard_id of the first zone containing the point, else None."""
    from common import point_in_polygon_feature
    for feat in hazard_features:
        if point_in_polygon_feature(lat, lon, feat):
            return feat["properties"].get("hazard_id")
    return None


def priority_category(score: int) -> str:
    """Translate a numeric priority score into an action-oriented category."""
    if score >= 7:
        return "P1 - Immediate"
    if score >= 5:
        return "P2 - Urgent"
    if score >= 3:
        return "P3 - Routine"
    return "P4 - Monitor"


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)
    rings = cfg["analysis"]["proximity_radius_miles"]

    facilities = valid_points(load_processed(cfg, "emergency_facilities.csv"), cfg)
    # Only route to facilities that can actually respond.
    if "operational_status" in facilities.columns:
        operational = facilities[facilities["operational_status"] == "Operational"]
        facilities_for_routing = operational if len(operational) else facilities
    else:
        facilities_for_routing = facilities

    incidents = valid_points(load_processed(cfg, "incidents.csv"), cfg)
    hazards = read_geojson(repo_path(cfg["paths"]["geojson"],
                                     "simulated_hazard_zones.geojson"))["features"]

    # --- Incident analysis: proximity + hazard + priority --------------------
    enriched_rows = []
    proximity_rows = []
    for _, inc in incidents.iterrows():
        lat, lon = inc["latitude"], inc["longitude"]
        fac, dist = nearest_facility(lat, lon, facilities_for_routing)
        ring = proximity_ring(dist, rings)
        haz = hazard_exposed(lat, lon, hazards)

        sev_w = SEVERITY_WEIGHT.get(inc.get("severity"), 1)
        open_w = 2 if inc.get("status") in ("Open", "In Progress") else 0
        haz_w = 2 if haz else 0
        far_w = 1 if dist > max(rings) else 0  # poor facility coverage adds urgency
        score = sev_w + open_w + haz_w + far_w
        category = priority_category(score)

        record = inc.to_dict()
        record.update({
            "nearest_facility_id": fac["facility_id"] if fac is not None else None,
            "nearest_facility_name": fac["name"] if fac is not None else None,
            "nearest_facility_type": fac["facility_type"] if fac is not None else None,
            "nearest_facility_miles": round(dist, 2),
            "proximity_ring": ring,
            "hazard_zone_id": haz,
            "hazard_exposed": "Y" if haz else "N",
            "priority_score": score,
            "priority_category": category,
        })
        enriched_rows.append(record)
        proximity_rows.append({
            "incident_id": inc["incident_id"],
            "incident_type": inc.get("incident_type"),
            "severity": inc.get("severity"),
            "status": inc.get("status"),
            "town": inc.get("town"),
            "nearest_facility_id": record["nearest_facility_id"],
            "nearest_facility_name": record["nearest_facility_name"],
            "nearest_facility_miles": record["nearest_facility_miles"],
            "proximity_ring": ring,
            "hazard_exposed": record["hazard_exposed"],
            "priority_score": score,
            "priority_category": category,
        })

    # Write enriched incident GeoJSON (the headline analytical layer).
    geojson, skipped = points_to_geojson(enriched_rows)
    write_geojson(geojson, repo_path(cfg["paths"]["geojson"], "incidents_analyzed.geojson"))
    log(f"Wrote incidents_analyzed.geojson  features={len(geojson['features'])}")

    # Write proximity table (feeds dashboard + SQL).
    prox_path = repo_path(cfg["paths"]["dashboard_tables"], "incident_facility_proximity.csv")
    write_csv(prox_path, list(proximity_rows[0].keys()), proximity_rows)
    log(f"Wrote incident_facility_proximity.csv  rows={len(proximity_rows)}")

    # --- Hazard exposure for fixed assets (facilities/shelters/hospitals) ----
    exposure_rows = []
    for fname, id_field, type_label in [
        ("emergency_facilities.csv", "facility_id", "Emergency Facility"),
        ("shelters.csv", "shelter_id", "Shelter"),
        ("hospitals.csv", "hospital_id", "Hospital"),
    ]:
        df = valid_points(load_processed(cfg, fname), cfg)
        for _, row in df.iterrows():
            haz = hazard_exposed(row["latitude"], row["longitude"], hazards)
            exposure_rows.append({
                "asset_id": row[id_field],
                "asset_name": row.get("name"),
                "asset_class": type_label,
                "town": row.get("town"),
                "hazard_zone_id": haz,
                "hazard_exposed": "Y" if haz else "N",
            })
    exp_path = repo_path(cfg["paths"]["dashboard_tables"], "facility_hazard_exposure.csv")
    write_csv(exp_path, list(exposure_rows[0].keys()), exposure_rows)
    exposed_n = sum(1 for r in exposure_rows if r["hazard_exposed"] == "Y")
    log(f"Wrote facility_hazard_exposure.csv  rows={len(exposure_rows)}  exposed={exposed_n}")

    # Quick priority breakdown to the console (sanity check for the analyst).
    cats = {}
    for r in proximity_rows:
        cats[r["priority_category"]] = cats.get(r["priority_category"], 0) + 1
    log("Incident priority breakdown: " +
        ", ".join(f"{k}={v}" for k, v in sorted(cats.items())))
    log("Analysis complete. Next: python scripts/05_export_dashboard_tables.py")


if __name__ == "__main__":
    main()
