# StoryMap Outline

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

A blueprint for an **ArcGIS StoryMap** that presents this project as a narrative
to non-technical stakeholders. Build it in the ArcGIS StoryMaps builder using
the web map, dashboard, and screenshots from this project. Each section below is
one StoryMap block.

---

## Title block

- **Title:** Concord–Manchester Public Safety GIS Readiness Dashboard
- **Subtitle:** A portfolio demonstration of GIS for emergency planning
- **Cover:** a regional overview map screenshot.
- **Prominent disclaimer:** *"Portfolio demonstration using public or simulated data — not an official emergency management product."*

## 1. Purpose

One short paragraph: this project shows how a GIS Solutions Engineer turns raw
geospatial data into maps, dashboards, and reports that help emergency managers
plan and respond across the Concord–Manchester corridor.

## 2. The public-safety problem

Explain the need: emergency managers must quickly understand where response
assets are, what's happening, what's at risk, and where the gaps are — with data
they can trust. Use a sidecar with the regional overview map.

## 3. The data

- List the layers (towns, facilities, shelters, hospitals, incidents, hazard
  zones) and that all data here is **simulated**.
- Link to `docs/data_dictionary.md` and `docs/data_sources.md`.
- Note how real, authoritative public sources (NH GRANIT, FEMA NFHL, HIFLD)
  would slot in without code changes.

## 4. Methods (the workflow)

Walk through clean → validate → analyze → publish, with the workflow diagram
from the README. Emphasize automation (one command per stage) and QA/QC.

- **Embed:** a screenshot of a pipeline run log.
- **Callout:** the 7 data-quality issues the validator caught.

## 5. Maps & dashboard

Use a **sidecar** or **swipe** layout:

- Emergency facilities & shelters map.
- Hazard exposure map (zones + exposed assets).
- Incident priority map (P1–P4).
- Embed the live ArcGIS Dashboard (or a screenshot).

## 6. Findings

Summarize the headline numbers from `outputs/reports/summary_report.md`:

- Incident load concentrates in the larger towns (e.g. Manchester, Concord).
- A set of high-priority incidents sit far from the nearest facility (coverage gaps).
- Several fixed assets fall inside simulated hazard zones.
- Data quality: errors must be fixed before operational trust.

## 7. How it supports decision-making

- Planning: town readiness rollups guide resource positioning and mutual-aid.
- Response: priority + proximity direct units to the most urgent locations.
- Communication: dashboards and briefings keep leadership and the public informed.

## 8. Limitations

- Simulated data; straight-line (not drive-time) distance; illustrative hazard
  zones; not for operational use. Restate the disclaimer.

## 9. Future improvements

- Authoritative data, network analysis, scheduled automation, live AGOL
  publishing, PowerBI `.pbix`, SQL Server enterprise geodatabase.

## 10. About / credits

- Built as a portfolio project; tools used; link to the GitHub repository.

---

### Screenshots to capture for the StoryMap

1. Regional overview map (ArcGIS Pro or web map).
2. Facilities & shelters map with symbology.
3. Hazard exposure map.
4. Incident priority map.
5. The operational dashboard.
6. A pipeline run log (terminal).
7. The QA/QC report.
