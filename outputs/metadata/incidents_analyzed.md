# Metadata — Analyzed Incidents (priority + proximity + hazard)

> **Portfolio demonstration using public or simulated data. Not an official emergency management product; not for operational decision-making. Distances are straight-line approximations. Hazard zones are illustrative and not derived from any official source.**

- **Abstract:** Simulated incident feed enriched with nearest-facility distance, hazard exposure, and a priority score/category.
- **Purpose:** Situational awareness and resource prioritization.
- **Theme keywords:** emergency response, events
- **Place keywords:** New Hampshire, Concord, Manchester, Merrimack County, Hillsborough County, Rockingham County
- **Spatial reference:** EPSG:4326
- **Bounding box [minx, miny, maxx, maxy]:** [-71.62868, 42.96702, -71.26891, 43.2351]
- **Geometry type:** Point
- **Feature count:** 117
- **Distribution format:** GeoJSON (EPSG:4326)
- **Update frequency:** On pipeline run (manual / scheduled).
- **Data quality:** 3 error(s), 0 warning(s) on the source (incidents.csv) at last validation.
- **Contact:** Portfolio author (demonstration project).

## Attributes

| Field |
|---|
| incident_id |
| incident_type |
| severity |
| town |
| reported_at |
| status |
| simulated_flag |
| nearest_facility_id |
| nearest_facility_name |
| nearest_facility_type |
| nearest_facility_miles |
| proximity_ring |
| hazard_zone_id |
| hazard_exposed |
| priority_score |
| priority_category |

## Lineage

1. Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md
2. Standardized & cleaned: scripts/02_load_clean_data.py
3. Validated (QA/QC): scripts/03_validate_gis_data.py
4. Analysis (proximity/hazard/priority): scripts/04_generate_analysis_layers.py