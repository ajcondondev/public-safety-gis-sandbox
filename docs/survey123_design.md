# Survey123 Form Design

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Design for an **Esri Survey123** field form that lets responders report **shelter
status** and **road closures** from the field, feeding the same web map and
dashboard for near-real-time situational awareness.

---

## Form: "Corridor Shelter & Road Status Report"

**Purpose:** capture rapid field updates during drills or events.
**Submitters:** shelter managers, public-works crews, field liaisons.
**Geometry:** point (captured from device GPS or map tap).

### Fields

| Label | Field name | Type | Required | Choices / notes |
|---|---|---|---|---|
| Report type | `report_type` | single choice | ✓ | Shelter Status, Road Closure |
| Reporter name | `reporter_name` | text | ✓ | Free text |
| Reporter role | `reporter_role` | single choice | | Shelter Manager, Public Works, Fire/EMS, Police, EM Staff, Other |
| Town | `town` | single choice | ✓ | Concord, Bow, Pembroke, Allenstown, Hooksett, Dunbarton, Goffstown, Manchester, Auburn, Candia |
| Location | `geometry` | geopoint | ✓ | Auto GPS + manual adjust |
| **— Shelter fields** (show if report_type = Shelter Status) | | | | |
| Shelter name | `shelter_name` | text | conditional | Required when report_type = Shelter Status |
| Shelter status | `shelter_status` | single choice | conditional | Open, Standby, Closed |
| Current occupancy | `occupancy` | integer | | ≥ 0 |
| Capacity | `capacity` | integer | | ≥ 0 |
| Pet-friendly | `pet_friendly` | yes/no | | |
| Generator on backup power | `generator_backup` | yes/no | | |
| **— Road fields** (show if report_type = Road Closure) | | | | |
| Road / segment name | `road_name` | text | conditional | Required when report_type = Road Closure |
| Closure status | `closure_status` | single choice | conditional | Fully Closed, Partially Closed, Reopened |
| Cause | `closure_cause` | single choice | | Flooding, Downed Tree, Crash, Hazmat, Other |
| Estimated reopen | `eta_reopen` | dateTime | | |
| **— Common** | | | | |
| Severity | `severity` | single choice | ✓ | Low, Moderate, High, Critical |
| Notes | `notes` | multiline text | | |
| Photo | `photo` | image | | Optional attachment |
| Reported at | `reported_at` | dateTime | ✓ | Default = now |

### Validation rules (XLSForm `constraint`)

- `occupancy <= capacity` when both are provided.
- `eta_reopen` must be in the future when supplied.
- `town` constrained to the corridor choice list (mirrors CHK-05).
- `severity` constrained to the four-value domain (mirrors CHK-06).

### Logic

- **Relevant** expressions show shelter vs. road fields based on `report_type`.
- **Default** `reported_at = now()` and pull `town` from GPS where possible.
- Required-field enforcement mirrors the pipeline's CHK-01.

---

## How responses flow into the dashboard

```
Survey123 form  ──submit──▶  Hosted feature layer (AGOL)
                                   │
                                   ├──▶ Web map (live points, Arcade popups)
                                   ├──▶ ArcGIS Dashboard (shelter status / road closures update live)
                                   └──▶ (optional) export to data/raw/ to feed the Python pipeline
```

- The hosted layer shares the schema vocabulary used here (`town`, `severity`,
  `status`), so it joins cleanly to the rest of the project.
- For offline analysis, export the responses to `data/raw/` and the pipeline
  will validate and analyze them alongside the other layers.

## Why this matters for the role

Survey123 is a named preferred qualification for the target role. This form
demonstrates **field data collection design**: controlled vocabularies,
conditional logic, validation that mirrors the QA/QC plan, and a clear path from
field submission to a live operational dashboard.
