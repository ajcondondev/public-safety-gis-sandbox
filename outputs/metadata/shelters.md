# Metadata — Emergency Shelters

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Emergency shelters with status, capacity, pet-friendliness, and backup power (simulated).
- **Purpose:** Track shelter availability and capacity for mass-care planning.
- **Theme keywords:** structure, emergency management
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.62161, 42.98317, -71.26892, 43.22482]
- **Geometry type:** Point
- **Feature count:** 14
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** 0 error(s), 0 warning(s) on the source (shelters.csv) at last validation.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| shelter_id |
| name |
| town |
| address |
| capacity |
| status |
| pet_friendly |
| generator_backup |
| data_source |
| last_updated |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. No analytical transformation beyond cleaning.