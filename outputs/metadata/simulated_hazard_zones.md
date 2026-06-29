# Metadata — Simulated Hazard Zones

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Illustrative floodplain and severe-weather polygons (simulated; NOT from FEMA/NWS).
- **Purpose:** Demonstrate hazard-exposure overlay analysis.
- **Theme keywords:** environment, hazards
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.56, 42.97, -71.42, 43.235]
- **Geometry type:** Polygon
- **Feature count:** 3
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** Derived/illustrative layer; not independently validated.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| hazard_id |
| hazard_type |
| severity |
| town |
| description |
| data_source |
| last_updated |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. No analytical transformation beyond cleaning.