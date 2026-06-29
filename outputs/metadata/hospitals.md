# Metadata — Hospitals / Acute-Care Sites

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Hospitals with trauma level and bed counts (simulated; names echo public facilities).
- **Purpose:** Locate definitive medical care for response planning.
- **Theme keywords:** structure, health
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.6, 42.989, -71.45, 43.2128]
- **Geometry type:** Point
- **Feature count:** 6
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** 0 error(s), 0 warning(s) on the source (hospitals.csv) at last validation.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| hospital_id |
| name |
| town |
| address |
| trauma_level |
| beds |
| operational_status |
| data_source |
| last_updated |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. No analytical transformation beyond cleaning.