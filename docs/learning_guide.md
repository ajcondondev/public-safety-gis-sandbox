# Learning Guide

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

This guide turns the project into a **teaching tool**. It explains the GIS and
emergency-management concepts behind each pipeline stage, points to exactly where
each concept lives in the code, and gives a short "try this" exercise. If you are
studying for a public-safety GIS role, read this alongside the
[glossary](glossary.md) and run the pipeline as you go.

New to GIS? Start with the [glossary](glossary.md), then come back here.

---

## The big idea

> A GIS Solutions Engineer builds and maintains the mapping and data systems that
> let public-safety officials understand **where things are, what is happening,
> what areas may be affected, and how resources can be used** — during planning
> and during emergencies.

This project walks through that whole chain on a small, safe scale: messy data →
trustworthy data → analysis → a shared picture leaders can act on.

## Concept → where it lives in this repo

| GIS concept | Plain-English meaning | Where in this project |
|---|---|---|
| **Layers** | A themed set of map features (one "sheet"). | each file in `outputs/geojson/` |
| **Attribute table** | The spreadsheet behind a layer (one row per feature). | the CSVs in `data/processed/` |
| **Points / lines / polygons** | Feature shapes: a site, a route, an area. | facilities = points; hazard zones = polygons |
| **Coordinate system / projection** | Agreed numbering for locations; flattening the round earth. | WGS84 storage; project to NH State Plane for analysis (`docs/arcgis_workflow.md`) |
| **Geocoding** | Address → coordinates. | conceptually, the `latitude`/`longitude` on each record |
| **Data cleaning / standardization** | Fixing names, casing, types, duplicates. | `scripts/02_load_clean_data.py` |
| **Data quality / QA-QC** | Is the data complete, accurate, current, consistent? | `scripts/03_validate_gis_data.py`, `docs/qa_qc_plan.md` |
| **Metadata & data lineage** | Where data came from, when, and how it changed. | `scripts/09_generate_metadata.py`, `outputs/metadata/` |
| **Proximity analysis** | What is nearest to a point. | `scripts/04` nearest-facility distance |
| **Buffers / overlay / point-in-polygon** | Zones of effect; where layers intersect; is a point inside an area. | `scripts/04` hazard-exposure test (`common.point_in_polygon_feature`) |
| **Spatial join / aggregation** | Attach/count data by location or group. | `scripts/05` town rollups |
| **Symbology & popups** | Colors/icons and click-info that make a map readable. | `scripts/07` maps, `docs/arcade_examples.md` |
| **Web map / dashboard** | Interactive browser map; live indicator screen. | `outputs/maps/interactive_map.html`, `outputs/dashboard/index.html` |
| **GIS database** | The authoritative store every product reads from. | `outputs/public_safety_gis.sqlite`, `sql/` |
| **Common operating picture** | One shared, current view a whole team uses. | the dashboard + summary report together |

## Walk the pipeline (stage by stage)

### Stage 01 — generate (data preparation sandbox)
**Concept:** real projects rarely start with clean data. We create a realistic,
reproducible sandbox — and deliberately seed defects so QA has something to find.
**Code:** `scripts/01_create_project_structure.py`.
**Try this:** change `seed` in `config/config.example.yml` and re-run; note the
data changes but the *structure* stays identical (reproducibility).

### Stage 02 — clean (ETL / standardization)
**Concept:** standardize field names, trim whitespace, fix inconsistent town
casing, coerce coordinate types — without silently dropping bad records.
**Code:** `scripts/02_load_clean_data.py` (`normalize_town`, `coerce_coords`).
**Try this:** open a `data/simulated/*.csv`, hand-break a town name's casing, re-run
stage 02, and watch the cleaning log normalize it.

### Stage 03 — validate (data quality / trust)
**Concept:** a beautiful map on bad data is worse than no map — it looks
trustworthy while being wrong. Every check has an ID, a severity, and a rule.
**Code:** `scripts/03_validate_gis_data.py`; rules in `docs/qa_qc_plan.md`.
**Try this:** read `outputs/reports/qa_qc_report.md` — find the 7 seeded issues and
match each to a check (CHK-01…CHK-06).

### Stage 04 — analyze (spatial analysis / decision support)
**Concept:** turn locations into *answers*: nearest facility (proximity), is the
incident inside a hazard zone (point-in-polygon overlay), and a priority score
that ranks what to look at first.
**Code:** `scripts/04_generate_analysis_layers.py`.
**Try this:** change `proximity_radius_miles` in config and see how the rings and
coverage-gap list shift.

### Stage 05 — serve (database + dashboard tables)
**Concept:** separate the "serving layer" (aggregates + a database) from raw and
processed data — the same layering used in enterprise GIS (SDE / SQL Server).
**Code:** `scripts/05_export_dashboard_tables.py`, `sql/schema.sql`.
**Try this:** run `sql/summary_queries.sql` against the SQLite DB and compare the
numbers to `town_readiness_summary.csv` — same answers, SQL vs Python.

### Stage 06 — report (stakeholder communication)
**Concept:** translate analysis into plain English for non-technical leaders.
**Code:** `scripts/06_generate_summary_report.py`.
**Try this:** read `outputs/reports/summary_report.md` as if you were a town
manager — is the "act-now" list clear in 10 seconds?

### Stage 07–08 — present (maps + dashboard = common operating picture)
**Concept:** a shared, current visual picture is one of the most valuable things
GIS provides in an incident.
**Code:** `scripts/07_generate_maps.py`, `scripts/08_build_dashboard.py`.
**Try this:** open both HTML files in a browser; click an incident to read its popup.

### Stage 09 — metadata (standards / lineage)
**Concept:** authoritative data isn't publishable without metadata describing its
source, extent, fields, and limits.
**Code:** `scripts/09_generate_metadata.py`, `outputs/metadata/`.
**Try this:** open `outputs/metadata/incidents_analyzed.md` and trace its lineage.

## How this maps to the four phases of emergency management

Emergency management is usually described in four phases. GIS supports all four —
and so does this project.

| Phase | What it means | How this project supports it |
|---|---|---|
| **Preparedness** | Get ready before anything happens. | Facility/shelter/hospital layers + town readiness summary show coverage ahead of time. |
| **Mitigation** | Reduce risk over the long term. | Hazard-exposure analysis flags which assets sit inside hazard zones — guiding where to invest. |
| **Response** | Act during the emergency. | Incident priority + nearest-facility proximity + the live map/dashboard give a common operating picture. |
| **Recovery** | Return to normal afterward. | The QA + summary reports document what happened and what the data showed (after-action input). |

## The honesty principle (why this matters for hiring)

In public safety the cost of an error is measured in time and sometimes lives.
Hiring managers trust candidates who clearly say *what they know, what they
inferred, and what they could not verify*. This project models that: every
artifact carries the disclaimer, the QA report shows the data's flaws openly, and
the analysis documents its approximations (straight-line distance, simulated
hazards). Being honest about limitations is a strength, not a weakness.

## A self-study path that uses this repo

1. **Fundamentals** — read the [glossary](glossary.md); be able to define each term with a public-safety example.
2. **Data quality** — study `docs/qa_qc_plan.md`; run stage 03 and explain every finding.
3. **Analysis** — read `scripts/04`; explain proximity vs. overlay vs. priority scoring in plain English.
4. **Databases** — run the queries in `sql/`; learn `SELECT` / `JOIN` / `GROUP BY`.
5. **Web GIS & dashboards** — study how `scripts/07`/`08` build the map and dashboard; map them to ArcGIS Online / Dashboards in `docs/arcgis_workflow.md`.
6. **Esri tooling** — read `docs/arcgis_workflow.md`, `docs/arcade_examples.md`, `docs/survey123_design.md`; these are the manual Esri equivalents.
7. **Communication** — rewrite `docs/stakeholder_brief.md` in your own words for a different audience.
8. **Make it yours** — swap in real NH data (`docs/data_sources.md`) and re-run.

## Interview prompts you can answer with this project

- *"Walk me through how you'd build a public-safety dashboard."* → stages 02→08.
- *"How do you validate a dataset from a partner agency?"* → `docs/qa_qc_plan.md` + stage 03.
- *"What's the difference between proximity and overlay analysis?"* → `scripts/04`.
- *"How do you keep sensitive data out of a public product?"* → all-simulated design + disclaimer + `docs/data_sources.md` sensitivity notes.
- *"How would you automate a repetitive GIS workflow?"* → `scripts/run_pipeline.py` + CI.
