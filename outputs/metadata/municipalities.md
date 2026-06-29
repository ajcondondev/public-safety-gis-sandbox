# Metadata — Corridor Municipalities (Towns)

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Reference boundaries/centroids for the ten municipalities in the Concord–Manchester corridor.
- **Purpose:** Spatial backbone used to aggregate incidents, facilities, and shelters by town.
- **Theme keywords:** boundaries, administrative units
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.6126, 42.9956, -71.2767, 43.2081]
- **Geometry type:** Point
- **Feature count:** 10
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** 0 error(s), 0 warning(s) on the source (municipalities.csv) at last validation.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| town_id |
| town_name |
| county |
| population |
| area_sqmi |
| data_source |
| last_updated |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. No analytical transformation beyond cleaning.