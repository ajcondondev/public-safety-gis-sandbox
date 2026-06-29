"""
02_load_clean_data.py
=====================
Load the raw/simulated datasets, STANDARDIZE them into a consistent schema, and
emit cleaned CSVs (data/processed) plus map-ready GeoJSON (outputs/geojson).

GIS Solutions Engineer mapping:
  * Data preparation / ETL — standardize field names, trim whitespace, fix
    inconsistent town-name casing, coerce coordinate types. This is the daily
    bread of keeping "GIS server data accurate, reliable, and usable."
  * Schema mapping — raw column names get normalized (lower_snake_case) so the
    rest of the pipeline and the SQL layer can rely on stable field names.
  * Format conversion — CSV -> GeoJSON, the interchange format for ArcGIS
    Online hosted layers and web maps.

IMPORTANT: cleaning here is *non-destructive about content*. We fix formatting
(casing, whitespace, types) but we DO NOT silently drop records with structural
problems (missing coordinates, duplicate IDs, out-of-range values). Those are
left in place so script 03 can detect and report them honestly. Hiding bad
records would defeat the purpose of a data-quality demo.

Run:  python scripts/02_load_clean_data.py
"""

from __future__ import annotations

import os

import pandas as pd

from common import (load_config, ensure_dirs, log, repo_path,
                    points_to_geojson, write_geojson, read_geojson)

# Point datasets: filename -> (id_field). Used to drive cleaning + GeoJSON export.
POINT_DATASETS = {
    "municipalities.csv": "town_id",
    "emergency_facilities.csv": "facility_id",
    "shelters.csv": "shelter_id",
    "hospitals.csv": "hospital_id",
    "incidents.csv": "incident_id",
}

# Canonical town names (used to normalize messy casing/whitespace).
CANONICAL_TOWNS = ["Concord", "Bow", "Pembroke", "Allenstown", "Hooksett",
                   "Dunbarton", "Goffstown", "Manchester", "Auburn", "Candia"]
_TOWN_LOOKUP = {t.lower(): t for t in CANONICAL_TOWNS}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to lower_snake_case and strip surrounding spaces."""
    df = df.copy()
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"\s+", "_", regex=True))
    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace on all string/object columns."""
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
    return df


def normalize_town(df: pd.DataFrame, changes: list) -> pd.DataFrame:
    """
    Fix inconsistent town-name casing/whitespace against the canonical list.
    Records the corrections so the run log is auditable (data lineage).
    """
    if "town" not in df.columns:
        return df
    df = df.copy()
    for idx, val in df["town"].items():
        if not isinstance(val, str):
            continue
        canon = _TOWN_LOOKUP.get(val.strip().lower())
        if canon and canon != val:
            changes.append((idx, val, canon))
            df.at[idx, "town"] = canon
    return df


def coerce_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Force latitude/longitude to numeric (bad strings become NaN, caught in 03)."""
    df = df.copy()
    for col in ("latitude", "longitude"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def pick_source_path(cfg: dict, fname: str) -> str | None:
    """
    Prefer a real file in data/raw/ if you have supplied one; otherwise use the
    simulated copy. This mirrors how a real pipeline would swap demo data for
    authoritative source data without code changes.
    """
    raw = repo_path(cfg["paths"]["raw"], fname)
    sim = repo_path(cfg["paths"]["simulated"], fname)
    if os.path.exists(raw):
        return raw
    if os.path.exists(sim):
        return sim
    return None


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)
    processed_dir = cfg["paths"]["processed"]
    geojson_dir = cfg["paths"]["geojson"]

    total_town_fixes = 0
    for fname, id_field in POINT_DATASETS.items():
        src = pick_source_path(cfg, fname)
        if not src:
            log(f"SKIP {fname}: not found in raw/ or simulated/. Run script 01 first.")
            continue

        df = pd.read_csv(src)
        df = standardize_columns(df)
        df = clean_text_columns(df)
        df = coerce_coords(df)

        town_changes: list = []
        df = normalize_town(df, town_changes)
        total_town_fixes += len(town_changes)
        for idx, old, new in town_changes:
            log(f"  town normalized in {fname}: '{old}' -> '{new}' (row {idx})")

        # Write cleaned CSV.
        out_csv = repo_path(processed_dir, fname)
        df.to_csv(out_csv, index=False)

        # Write GeoJSON points (rows with bad coords are skipped + counted).
        geojson, skipped = points_to_geojson(df.to_dict(orient="records"))
        out_geojson = repo_path(geojson_dir, fname.replace(".csv", ".geojson"))
        write_geojson(geojson, out_geojson)

        log(f"Cleaned {fname:28s} rows={len(df):4d}  geojson_features={len(geojson['features']):4d}"
            f"  skipped_bad_coords={skipped}")

    # Pass the hazard-zone polygons through to outputs/geojson unchanged
    # (they are already clean GeoJSON; copying keeps all map layers in one place).
    hz_src = repo_path(cfg["paths"]["simulated"], "simulated_hazard_zones.geojson")
    if os.path.exists(hz_src):
        write_geojson(read_geojson(hz_src),
                      repo_path(geojson_dir, "simulated_hazard_zones.geojson"))
        log("Copied simulated_hazard_zones.geojson -> outputs/geojson/")

    log(f"Cleaning complete. Town-name corrections applied: {total_town_fixes}.")
    log("Next: python scripts/03_validate_gis_data.py")


if __name__ == "__main__":
    main()
