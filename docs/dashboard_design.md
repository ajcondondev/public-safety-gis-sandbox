# Dashboard Design

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Design notes for an **ArcGIS Dashboard** (operational view) and a **PowerBI
report** (executive/analytical view), both driven by the CSVs in
`outputs/dashboard_tables/` and the GeoJSON in `outputs/geojson/`.

---

## Audience & purpose

| View | Audience | Question it answers |
|---|---|---|
| ArcGIS Dashboard | Emergency managers, EOC staff | "What's happening right now and where?" |
| PowerBI report | Agency leadership | "How ready are we, by town, over time?" |

## Source tables → indicators

| Indicator | Source | Visual |
|---|---|---|
| **Total incidents** | `incidents_by_town.csv` (sum) | Indicator/number tile |
| **Open high-severity incidents** | `open_high_severity_incidents.csv` (count) | Indicator tile, red |
| **Incidents by town** | `incidents_by_town.csv` | Bar chart |
| **Incidents by type** | `incidents_by_type.csv` | Bar/pie chart |
| **Incidents by severity** | `incidents_by_severity.csv` | Donut, color-coded |
| **Shelters by status** | `shelters_by_status.csv` | Stacked bar + capacity |
| **Facilities by type** | `facilities_by_type.csv` | Bar chart |
| **Facilities/assets near hazard zones** | `hazard_exposed_assets.csv` | Indicator + list |
| **Incident priority breakdown** | `incident_facility_proximity.csv` | Category chart (P1–P4) |
| **Coverage gaps** | `incident_facility_proximity.csv` (filter) | List/table |
| **Town readiness** | `town_readiness_summary.csv` | Map choropleth + table |
| **Live incident map** | `incidents_analyzed.geojson` | Map element (center) |
| **Data quality** | `qa_results.csv` | Indicator (error/warning counts) |

## ArcGIS Dashboard layout

```
┌───────────────────────────── Header: title + disclaimer + last-updated ─────────────────────────────┐
├──────────────┬──────────────────────────────────────────────────────────┬───────────────────────────┤
│  KPI column  │                    Map (incidents_analyzed)              │   Side panel (selectable) │
│  ──────────  │   symbolized by priority_category; hazard zones beneath  │  ───────────────────────  │
│  Total inc.  │   facilities / shelters / hospitals toggleable           │  Open high-severity list  │
│  Open hi-sev │                                                          │  (incident_id, town,      │
│  P1 count    │                                                          │   type, status)           │
│  Shelters    │                                                          │                           │
│  open / cap  │                                                          │  Coverage-gap list        │
│  Hazard-exp. │                                                          │                           │
├──────────────┴───────────────────────┬──────────────────────────────────┴───────────────────────────┤
│   Incidents by town (bar)             │   Incidents by severity (donut)   │  Shelters by status (bar) │
└───────────────────────────────────────┴───────────────────────────────────┴───────────────────────────┘
```

**Interactivity:** category selectors for town and severity drive the map and
lists; a "P1/P2 only" filter button isolates urgent incidents.

## PowerBI report design (using the same CSVs)

1. **Get Data → Text/CSV** for each file in `outputs/dashboard_tables/`.
2. Model relationships on `town` (link `town_readiness_summary`,
   `incidents_by_town`, etc.) to a town dimension.
3. Pages:
   - **Readiness Overview** — town readiness table + map (lat/long from
     `municipalities`), KPI cards (total incidents, open high-severity).
   - **Incidents** — by town / type / severity, with a slicer on status.
   - **Resources** — facilities by type, shelters by status & capacity.
   - **Hazard Exposure** — hazard-exposed assets by class and town.
   - **Data Quality** — `qa_results` error/warning counts by dataset/check.
4. Suggested DAX measures:
   - `Open High Severity = CALCULATE(COUNTROWS(incidents), incidents[status] IN {"Open","In Progress"}, incidents[severity] IN {"High","Critical"})`
   - `Total Shelter Capacity = SUM(shelters[capacity])`

## Color & accessibility

- Severity ramp: Low `#1a9850` → Moderate `#fdae61` → High `#e34a33` → Critical `#b30000`.
- Keep a colorblind-safe palette; don't rely on color alone — pair with labels.
- Always show the **disclaimer** and a **last-updated** timestamp on the canvas.

## Refresh / automation

- The CSVs regenerate by re-running `scripts/01`–`06`.
- In production, schedule the pipeline (Task Scheduler / cron), publish hosted
  layers via the ArcGIS API for Python, and let the dashboard read the live
  feature service — so the dashboard updates without manual steps.
