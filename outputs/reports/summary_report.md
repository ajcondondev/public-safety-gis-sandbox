# Concord–Manchester Public Safety GIS — Summary Report

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

_Generated: 2026-06-29T20:19:19Z_

## At a glance

| Indicator | Value |
|---|---:|
| Total incidents (simulated) | 120 |
| Open high-severity incidents | 13 |
| Incidents flagged P1/P2 (priority) | 58 |
| Coverage-gap incidents (P1/P2 & >3 mi to facility) | 0 |
| Emergency facilities | 26 |
| Shelters (open now) | 4 of 14 |
| Total shelter capacity | 1850 |
| Hospitals | 6 |
| Hazard-exposed assets | 21 |
| Data-quality issues (errors / warnings) | 7 / 0 |

## Town readiness

Towns ranked by simulated incident load, with the local resources and hazard exposure that shape response planning.

| town | county | population | incident_count | open_high_severity | facility_count | shelter_count | shelter_capacity | hospital_count | hazard_exposed_assets |
|---|---|---|---|---|---|---|---|---|---|
| Manchester | Hillsborough | 115644 | 63 | 5 | 6 | 2 | 200 | 2 | 10 |
| Concord | Merrimack | 43976 | 26 | 3 | 3 | 2 | 200 | 2 | 6 |
| Goffstown | Hillsborough | 18579 | 9 | 2 | 3 | 2 | 350 | 1 | 0 |
| Hooksett | Merrimack | 14871 | 8 | 1 | 2 | 2 | 450 | 1 | 5 |
| Auburn | Rockingham | 5891 | 4 | 0 | 2 | 1 | 50 | 0 | 0 |
| Pembroke | Merrimack | 7115 | 3 | 0 | 2 | 1 | 50 | 0 | 0 |
| Bow | Merrimack | 7519 | 2 | 1 | 2 | 1 | 150 | 0 | 0 |
| Dunbarton | Merrimack | 2758 | 2 | 0 | 2 | 1 | 150 | 0 | 0 |
| Candia | Rockingham | 4019 | 2 | 1 | 2 | 1 | 150 | 0 | 0 |
| Allenstown | Merrimack | 4774 | 1 | 0 | 2 | 1 | 100 | 0 | 0 |

## Where to look first: open high-severity incidents

| incident_id | incident_type | severity | town | status | reported_at |
|---|---|---|---|---|---|
| INC00031 | Hazmat Spill | Critical | Manchester | Open | 2026-06-14T17:31:00Z |
| INC00056 | Hazmat Spill | Critical | Concord | Open | 2026-06-04T06:15:00Z |
| INC00078 | Downed Tree | Critical | Manchester | Open | 2026-06-21T22:04:00Z |
| INC00110 | Motor Vehicle Crash | Critical | Concord | In Progress | 2026-06-18T10:48:00Z |
| INC00113 | Structure Fire | Critical | Manchester | In Progress | 2026-06-27T19:44:00Z |
| INC00003 | Power Outage | High | Candia | Open | 2026-06-17T00:56:00Z |
| INC00019 | Hazmat Spill | High | Goffstown | In Progress | 2026-06-10T09:41:00Z |
| INC00021 | Power Outage | High | Hooksett | Open | 2026-06-25T07:01:00Z |
| INC00035 | Structure Fire | High | Goffstown | Open | 2026-06-16T00:41:00Z |
| INC00040 | Structure Fire | High | Manchester | Open | 2026-06-20T03:23:00Z |
| INC00100 | Hazmat Spill | High | Bow | Open | 2026-06-18T06:49:00Z |
| INC00103 | Severe Weather | High | Manchester | Open | 2026-06-16T14:32:00Z |
| INC00115 | Hazmat Spill | High | Concord | In Progress | 2026-06-01T02:10:00Z |

## Coverage gaps for planning

0 high-priority incident(s) sit more than 3 miles from the nearest operational facility. In a real deployment these are the locations a planner would examine for mutual-aid agreements, pre-positioning, or new station siting.

## Data quality

This run found **7 errors** and **0 warnings** across the datasets. Full detail is in `outputs/reports/qa_qc_report.md`. Errors must be resolved before any of this data could be considered for operational use.

## How this supports emergency planning & response

- **Planning:** town-level rollups show where incident load is high relative to local facilities, shelter capacity, and hazard exposure.
- **Response:** the priority score ranks incidents so limited resources go to the most urgent first; proximity tells responders the nearest asset.
- **Situational awareness:** the GeoJSON layers drop straight into an ArcGIS Online web map or dashboard for a live operating picture.
- **Accountability:** the QA report documents exactly what is and isn't trustworthy in the data — essential before any decision is made on it.
