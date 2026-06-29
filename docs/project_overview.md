# Project Overview

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

## Purpose

The **Concord–Manchester Public Safety GIS Readiness Dashboard** is a portfolio
project that demonstrates the end-to-end work of a **GIS Solutions Engineer**
supporting emergency management and public safety. It takes geospatial data from
raw inputs through cleaning, validation, analysis, and publication-ready outputs,
with documentation aimed at both technical and non-technical audiences.

## The public-safety problem

Emergency managers in a multi-town corridor need a single, trustworthy picture of
readiness: where the response assets are, what is happening, what is at risk, and
where the gaps are. That picture has to be **current**, **quality-checked**, and
**explainable** to decision-makers who are not GIS specialists. Building and
maintaining that picture — reliably and repeatably — is the core of this role.

## Study area

The I-93 / NH-3 corridor from **Concord** to **Manchester, NH**, covering ten
municipalities: Concord, Bow, Pembroke, Allenstown, Hooksett, Dunbarton,
Goffstown, Manchester, Auburn, and Candia.

## Deliverables and how each maps to GIS Solutions Engineer responsibilities

| Deliverable | Artifact | Responsibility demonstrated |
|---|---|---|
| Reproducible data pipeline | `scripts/01`–`06`, `config/` | **Automation** of repetitive GIS data processing |
| Simulated data model | `data/simulated/`, `docs/data_dictionary.md` | **Data architecture** & schema design |
| Cleaning / standardization | `scripts/02` | **Data preparation / ETL** |
| Quality validation | `scripts/03`, `docs/qa_qc_plan.md`, `outputs/reports/qa_qc_report.md` | **QA/QC** and GIS data accuracy |
| Spatial analysis | `scripts/04` | **Geospatial analysis** for decision support |
| Relational database | `sql/`, `outputs/public_safety_gis.sqlite` | **SQL Server**-style data management |
| Dashboard tables | `scripts/05`, `docs/dashboard_design.md` | **Dashboard readiness** / visualization |
| Map production guide | `docs/arcgis_workflow.md` | **Map production** in ArcGIS Pro |
| Field form design | `docs/survey123_design.md` | **Survey123** field data collection |
| Narrative product | `docs/storymap_outline.md` | **StoryMaps** / public information |
| Executive briefing | `docs/stakeholder_brief.md`, `outputs/reports/summary_report.md` | **Stakeholder communication** |

## Architecture (layered, enterprise-style)

1. **Source layer** — `data/raw/` (authoritative data you supply) or
   `data/simulated/` (generated demo data). Mirrors how a real pipeline swaps
   demo data for source data without code changes.
2. **Processed layer** — `data/processed/` cleaned, standardized CSVs +
   `outputs/geojson/` map-ready layers.
3. **Analysis layer** — derived proximity, hazard-exposure, and priority outputs.
4. **Serving layer** — aggregate dashboard tables + the SQLite database +
   Markdown reports for humans.

This raw → processed → analysis → serving layering is the same pattern used in
enterprise GIS environments (e.g. an ArcGIS Enterprise / SDE / SQL Server stack).

## Design principles

- **Open-source first.** The pipeline runs on `pandas` + `PyYAML` only, so it
  works without an Esri license or a heavy geospatial stack. Esri tools are
  documented as manual workflows and optional ArcPy hooks.
- **Honest about quality.** The generator seeds real data defects and the
  validator finds and reports them. A QA demo that finds nothing proves nothing.
- **Reproducible.** A fixed random seed makes every run identical and auditable.
- **Safe.** All data is simulated and clearly labeled; nothing sensitive is used.

## How it supports emergency planning and response

- **Planning:** town-level readiness rollups highlight where incident load is high
  relative to facilities, shelter capacity, and hazard exposure.
- **Response:** incident priority scoring and nearest-facility proximity help
  direct limited resources to the most urgent locations first.
- **Situational awareness:** GeoJSON layers drop straight into a web map or
  dashboard for a live operating picture.
- **Accountability:** the QA report documents what is and isn't trustworthy
  before any decision is made on the data.
