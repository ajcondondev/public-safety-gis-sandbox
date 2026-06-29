# Metadata — Emergency Response Facilities

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Fire, police, EMS, emergency operations center, and public-works facilities (simulated).
- **Purpose:** Locate response assets and compute incident-to-facility proximity and coverage.
- **Theme keywords:** structure, emergency response, critical infrastructure
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.62381, 42.99249, -71.26343, 43.20498]
- **Geometry type:** Point
- **Feature count:** 25
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** 4 error(s), 0 warning(s) on the source (emergency_facilities.csv) at last validation.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| facility_id |
| name |
| facility_type |
| town |
| address |
| operational_status |
| data_source |
| last_updated |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. No analytical transformation beyond cleaning.