"""
01_create_project_structure.py
================================
Create output folders and generate the SIMULATED starter datasets for the
Concord <-> Manchester, NH public-safety corridor.

WHY THIS EXISTS (GIS Solutions Engineer mapping):
  * Data preparation — a GIS engineer rarely starts with clean data. This
    script stands up a realistic, *reproducible* sandbox so the rest of the
    pipeline (clean -> validate -> analyze -> publish) has something to chew on.
  * Safety / ethics — ALL data here is SIMULATED. No real 911, no private
    resident data. Every record carries a data_source of "Simulated (portfolio
    demo)" and incidents carry simulated_flag = "Y". See README disclaimer.
  * Realistic QA/QC — the generator deliberately injects a handful of data-
    quality DEFECTS (missing coordinates, a duplicate ID, an out-of-range
    coordinate, messy town-name casing, a blank required field). Script 03 is
    designed to catch exactly these, which is what makes the demo credible.

Run:  python scripts/01_create_project_structure.py
Idempotent: re-running regenerates identical files (fixed random seed).
"""

from __future__ import annotations

import os
import random

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, now_iso, write_geojson

# -----------------------------------------------------------------------------
# Corridor reference geography.
# Approximate town centroids (WGS84) for the I-93 / NH-3 corridor between
# Concord and Manchester. Used as anchors to scatter simulated facilities.
# These are public, town-level coordinates — nothing sensitive.
# -----------------------------------------------------------------------------
TOWNS = [
    # town_name,  county,        pop,    area_sqmi, lat,      lon
    ("Concord",    "Merrimack",  43976,  64.3, 43.2081, -71.5376),
    ("Bow",        "Merrimack",   7519,  28.0, 43.1376, -71.5440),
    ("Pembroke",   "Merrimack",   7115,  23.0, 43.1434, -71.4595),
    ("Allenstown", "Merrimack",   4774,  20.6, 43.1487, -71.4012),
    ("Hooksett",   "Merrimack",  14871,  36.5, 43.0959, -71.4651),
    ("Dunbarton",  "Merrimack",   2758,  31.3, 43.1009, -71.6126),
    ("Goffstown",  "Hillsborough",18579, 36.8, 43.0212, -71.6009),
    ("Manchester", "Hillsborough",115644,33.1, 42.9956, -71.4548),
    ("Auburn",     "Rockingham",   5891, 26.2, 43.0048, -71.3486),
    ("Candia",     "Rockingham",   4019, 30.9, 43.0762, -71.2767),
]

FACILITY_TYPES = ["Fire Station", "Police Station", "EMS Station",
                  "Emergency Operations Center", "Public Works Garage"]
INCIDENT_TYPES = ["Structure Fire", "Motor Vehicle Crash", "Flooding",
                  "Hazmat Spill", "Power Outage", "Severe Weather",
                  "Medical Emergency", "Downed Tree"]
SEVERITIES = ["Low", "Moderate", "High", "Critical"]


def jitter(rng: random.Random, value: float, spread: float) -> float:
    """Offset a centroid by a small random amount to place a feature near a town."""
    return round(value + rng.uniform(-spread, spread), 6)


def build_municipalities() -> pd.DataFrame:
    """Town reference table (one row per municipality in the corridor)."""
    rows = []
    for i, (name, county, pop, area, lat, lon) in enumerate(TOWNS, start=1):
        rows.append({
            "town_id": f"T{i:03d}",
            "town_name": name,
            "county": county,
            "population": pop,
            "area_sqmi": area,
            "latitude": lat,
            "longitude": lon,
            "data_source": "Simulated (portfolio demo)",
            "last_updated": now_iso(),
        })
    return pd.DataFrame(rows)


def build_facilities(rng: random.Random) -> pd.DataFrame:
    """Fire/Police/EMS/EOC/Public Works facilities scattered across towns."""
    rows = []
    fid = 1
    for name, county, pop, area, lat, lon in TOWNS:
        # Bigger towns get more facilities (rough proxy for service demand).
        n = 2 if pop < 8000 else (3 if pop < 50000 else 5)
        for _ in range(n):
            ftype = rng.choice(FACILITY_TYPES)
            rows.append({
                "facility_id": f"F{fid:04d}",
                "name": f"{name} {ftype}",
                "facility_type": ftype,
                "town": name,
                "address": f"{rng.randint(1, 999)} {rng.choice(['Main', 'Pleasant', 'Hall', 'River', 'Manchester', 'School'])} St, {name}, NH",
                "latitude": jitter(rng, lat, 0.02),
                "longitude": jitter(rng, lon, 0.02),
                "operational_status": rng.choices(
                    ["Operational", "Limited", "Out of Service"],
                    weights=[88, 9, 3])[0],
                "data_source": "Simulated (portfolio demo)",
                "last_updated": now_iso(),
            })
            fid += 1
    return pd.DataFrame(rows)


def build_shelters(rng: random.Random) -> pd.DataFrame:
    """Emergency shelters (e.g. schools / community centers) by town."""
    rows = []
    sid = 1
    for name, county, pop, area, lat, lon in TOWNS:
        n = 1 if pop < 8000 else 2
        for _ in range(n):
            cap = rng.choice([50, 75, 100, 150, 200, 300])
            rows.append({
                "shelter_id": f"S{sid:04d}",
                "name": f"{name} {rng.choice(['High School', 'Middle School', 'Community Center', 'Recreation Center'])}",
                "town": name,
                "address": f"{rng.randint(1, 999)} {rng.choice(['School', 'Church', 'Center', 'Union'])} St, {name}, NH",
                "latitude": jitter(rng, lat, 0.018),
                "longitude": jitter(rng, lon, 0.018),
                "capacity": cap,
                "status": rng.choices(
                    ["Open", "Standby", "Closed"], weights=[20, 35, 45])[0],
                "pet_friendly": rng.choice(["Y", "N"]),
                "generator_backup": rng.choices(["Y", "N"], weights=[70, 30])[0],
                "data_source": "Simulated (portfolio demo)",
                "last_updated": now_iso(),
            })
            sid += 1
    return pd.DataFrame(rows)


def build_hospitals(rng: random.Random) -> pd.DataFrame:
    """
    Hospitals / acute-care sites along the corridor. Names echo well-known
    public facilities but coordinates are approximate and flagged simulated.
    """
    seeds = [
        ("Concord Area Medical Center", "Concord", 43.2128, -71.5295, "Level III", 295),
        ("Riverbend Acute Care", "Concord", 43.2003, -71.5410, "Level IV", 60),
        ("Hooksett Regional Hospital", "Hooksett", 43.0980, -71.4665, "Level IV", 40),
        ("Manchester General Hospital", "Manchester", 42.9890, -71.4630, "Level II", 330),
        ("Queen City Medical Center", "Manchester", 43.0050, -71.4500, "Level III", 210),
        ("Goffstown Community Hospital", "Goffstown", 43.0220, -71.6000, "Level IV", 35),
    ]
    rows = []
    for i, (nm, town, lat, lon, trauma, beds) in enumerate(seeds, start=1):
        rows.append({
            "hospital_id": f"H{i:03d}",
            "name": nm,
            "town": town,
            "address": f"{rng.randint(1, 999)} Hospital Dr, {town}, NH",
            "latitude": lat,
            "longitude": lon,
            "trauma_level": trauma,
            "beds": beds,
            "operational_status": "Operational",
            "data_source": "Simulated (portfolio demo)",
            "last_updated": now_iso(),
        })
    return pd.DataFrame(rows)


def build_incidents(rng: random.Random, n: int = 120) -> pd.DataFrame:
    """Simulated incident feed (the 'what is happening right now' layer)."""
    rows = []
    # Weight incidents toward bigger towns.
    weights = [pop for _, _, pop, _, _, _ in TOWNS]
    for i in range(1, n + 1):
        name, county, pop, area, lat, lon = rng.choices(TOWNS, weights=weights)[0]
        sev = rng.choices(SEVERITIES, weights=[40, 32, 20, 8])[0]
        day = rng.randint(1, 27)
        hour = rng.randint(0, 23)
        rows.append({
            "incident_id": f"INC{i:05d}",
            "incident_type": rng.choice(INCIDENT_TYPES),
            "severity": sev,
            "town": name,
            "latitude": jitter(rng, lat, 0.03),
            "longitude": jitter(rng, lon, 0.03),
            "reported_at": f"2026-06-{day:02d}T{hour:02d}:{rng.randint(0,59):02d}:00Z",
            "status": rng.choices(
                ["Open", "In Progress", "Closed"], weights=[25, 20, 55])[0],
            "simulated_flag": "Y",
        })
    return pd.DataFrame(rows)


def build_hazard_zones() -> dict:
    """
    Simulated hazard zones as GeoJSON polygons (e.g. floodplain, severe-weather
    band). Hand-drawn rough rectangles near the river corridor — clearly
    illustrative, not derived from any official hazard layer.
    """
    def rect(lon0, lat0, lon1, lat1):
        return [[[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]]

    features = [
        {
            "type": "Feature",
            "properties": {
                "hazard_id": "HZ001", "hazard_type": "Floodplain (simulated)",
                "severity": "High", "town": "Concord",
                "description": "Simulated Merrimack River floodplain band near Concord.",
                "data_source": "Simulated (portfolio demo)", "last_updated": now_iso(),
            },
            "geometry": {"type": "Polygon",
                         "coordinates": rect(-71.560, 43.180, -71.520, 43.235)},
        },
        {
            "type": "Feature",
            "properties": {
                "hazard_id": "HZ002", "hazard_type": "Floodplain (simulated)",
                "severity": "Moderate", "town": "Hooksett",
                "description": "Simulated floodplain band near Hooksett village.",
                "data_source": "Simulated (portfolio demo)", "last_updated": now_iso(),
            },
            "geometry": {"type": "Polygon",
                         "coordinates": rect(-71.485, 43.080, -71.445, 43.120)},
        },
        {
            "type": "Feature",
            "properties": {
                "hazard_id": "HZ003", "hazard_type": "Severe Weather Band (simulated)",
                "severity": "High", "town": "Manchester",
                "description": "Simulated severe-thunderstorm impact band over Manchester.",
                "data_source": "Simulated (portfolio demo)", "last_updated": now_iso(),
            },
            "geometry": {"type": "Polygon",
                         "coordinates": rect(-71.490, 42.970, -71.420, 43.030)},
        },
    ]
    return {"type": "FeatureCollection", "features": features}


def inject_quality_issues(facilities: pd.DataFrame,
                          incidents: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Deliberately corrupt a few records so the validation stage (script 03) has
    real defects to find and report. A clean demo that finds zero issues is not
    a convincing QA/QC demo. Each defect below maps to a documented check.
    """
    fac = facilities.copy()
    inc = incidents.copy()

    # 1) Missing coordinates on a facility (blank lat & lon).
    fac.loc[2, "latitude"] = None
    fac.loc[2, "longitude"] = None

    # 2) Duplicate facility_id (collide row 5's id onto row 6).
    fac.loc[5, "facility_id"] = fac.loc[4, "facility_id"]

    # 3) Blank required field (name) on a facility.
    fac.loc[7, "name"] = ""

    # 4) Inconsistent town-name formatting (casing + stray whitespace).
    fac.loc[9, "town"] = "  manchester "

    # 5) Out-of-range coordinate on an incident (longitude > 0 is impossible
    #    in NH; should be negative). Also an out-of-range latitude elsewhere.
    inc.loc[3, "longitude"] = 71.45  # sign error (should be -71.45)
    inc.loc[8, "latitude"] = 99.9    # impossible latitude

    # 6) Missing coordinate on an incident.
    inc.loc[12, "latitude"] = None

    return fac, inc


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)
    log(f"Using config: {cfg['_config_path']}")

    seed = cfg.get("seed", 42)
    rng = random.Random(seed)
    sim_dir = cfg["paths"]["simulated"]

    # Build clean datasets.
    municipalities = build_municipalities()
    facilities = build_facilities(rng)
    shelters = build_shelters(rng)
    hospitals = build_hospitals(rng)
    incidents = build_incidents(rng)

    # Inject documented data-quality defects into the two layers we validate.
    facilities, incidents = inject_quality_issues(facilities, incidents)

    # Write CSVs.
    outputs = {
        "municipalities.csv": municipalities,
        "emergency_facilities.csv": facilities,
        "shelters.csv": shelters,
        "hospitals.csv": hospitals,
        "incidents.csv": incidents,
    }
    for fname, df in outputs.items():
        path = repo_path(sim_dir, fname)
        df.to_csv(path, index=False)
        log(f"Wrote {fname:28s} ({len(df):4d} rows) -> {os.path.relpath(path, repo_path())}")

    # Write hazard zones GeoJSON.
    hz_path = repo_path(sim_dir, "simulated_hazard_zones.geojson")
    write_geojson(build_hazard_zones(), hz_path)
    log(f"Wrote simulated_hazard_zones.geojson           -> {os.path.relpath(hz_path, repo_path())}")

    log("Simulated data generation complete. Next: python scripts/02_load_clean_data.py")


if __name__ == "__main__":
    main()
