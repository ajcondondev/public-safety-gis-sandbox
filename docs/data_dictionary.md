# Data Dictionary

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Defines every dataset, field, type, and allowed values in the project. Field
names are standardized to `lower_snake_case` by `scripts/02_load_clean_data.py`.
Coordinates are **WGS84 (EPSG:4326)** decimal degrees.

Legend — **Req**: required (validated by CHK-01). **PK**: primary key (CHK-03).

---

## `municipalities.csv` → table `towns`

The spatial backbone; one row per municipality in the corridor.

| Field | Type | Req | Notes |
|---|---|---|---|
| `town_id` | text | ✓ (PK) | e.g. `T001` |
| `town_name` | text | ✓ | Canonical town name |
| `county` | text | | Merrimack / Hillsborough / Rockingham |
| `population` | integer | | Approximate residents |
| `area_sqmi` | float | | Land area, square miles |
| `latitude` | float | | Town centroid (WGS84) |
| `longitude` | float | | Town centroid (WGS84) |
| `data_source` | text | | `Simulated (portfolio demo)` |
| `last_updated` | date | | ISO `YYYY-MM-DD` |

## `emergency_facilities.csv` → table `facilities`

Fire, police, EMS, EOC, and public-works response assets.

| Field | Type | Req | Notes / domain |
|---|---|---|---|
| `facility_id` | text | ✓ (PK) | e.g. `F0001` |
| `name` | text | ✓ | Facility name |
| `facility_type` | text | ✓ | Fire Station, Police Station, EMS Station, Emergency Operations Center, Public Works Garage |
| `town` | text | ✓ | Must match a `towns.town_name` (CHK-05) |
| `address` | text | | Street address |
| `latitude` | float | | WGS84; validated to corridor bounds (CHK-04) |
| `longitude` | float | | WGS84; validated to corridor bounds (CHK-04) |
| `operational_status` | text | | **Operational** \| Limited \| Out of Service (CHK-06) |
| `data_source` | text | | Provenance |
| `last_updated` | date | | ISO date |

## `shelters.csv` → table `shelters`

Emergency shelters (schools / community centers).

| Field | Type | Req | Notes / domain |
|---|---|---|---|
| `shelter_id` | text | ✓ (PK) | e.g. `S0001` |
| `name` | text | ✓ | Shelter name |
| `town` | text | ✓ | Must match a town |
| `address` | text | | Street address |
| `latitude` | float | | WGS84 |
| `longitude` | float | | WGS84 |
| `capacity` | integer | | Persons |
| `status` | text | | **Open** \| Standby \| Closed (CHK-06) |
| `pet_friendly` | text | | Y \| N |
| `generator_backup` | text | | Y \| N |
| `data_source` | text | | Provenance |
| `last_updated` | date | | ISO date |

## `hospitals.csv` → table `hospitals`

Hospitals / acute-care sites.

| Field | Type | Req | Notes |
|---|---|---|---|
| `hospital_id` | text | ✓ (PK) | e.g. `H001` |
| `name` | text | ✓ | Simulated, echoes public facility names |
| `town` | text | ✓ | Must match a town |
| `address` | text | | Street address |
| `latitude` | float | | WGS84 |
| `longitude` | float | | WGS84 |
| `trauma_level` | text | | Level I–IV (illustrative) |
| `beds` | integer | | Staffed beds (approx.) |
| `operational_status` | text | | Operational |
| `data_source` | text | | Provenance |
| `last_updated` | date | | ISO date |

## `incidents.csv` → table `incidents`

Simulated incident feed — the "what is happening now" layer.

| Field | Type | Req | Notes / domain |
|---|---|---|---|
| `incident_id` | text | ✓ (PK) | e.g. `INC00001` |
| `incident_type` | text | ✓ | Structure Fire, Motor Vehicle Crash, Flooding, Hazmat Spill, Power Outage, Severe Weather, Medical Emergency, Downed Tree |
| `severity` | text | ✓ | **Low \| Moderate \| High \| Critical** (CHK-06) |
| `town` | text | ✓ | Must match a town |
| `latitude` | float | | WGS84; CHK-02/CHK-04 |
| `longitude` | float | | WGS84; CHK-02/CHK-04 |
| `reported_at` | datetime | | ISO `YYYY-MM-DDThh:mm:ssZ` |
| `status` | text | | **Open \| In Progress \| Closed** (CHK-06) |
| `simulated_flag` | text | | Always `Y` (safety marker) |

## `simulated_hazard_zones.geojson`

Polygon hazard zones (GeoJSON FeatureCollection).

| Property | Type | Notes |
|---|---|---|
| `hazard_id` | text | e.g. `HZ001` |
| `hazard_type` | text | Floodplain (simulated) / Severe Weather Band (simulated) |
| `severity` | text | Low / Moderate / High |
| `town` | text | Primary town affected |
| `description` | text | Plain-English description |
| `data_source` | text | `Simulated (portfolio demo)` |
| `last_updated` | date | ISO date |

---

## Derived / analysis tables (script 04)

### `incident_facility_proximity.csv` → table `incident_proximity`

| Field | Type | Notes |
|---|---|---|
| `incident_id` | text | FK → incidents |
| `incident_type`, `severity`, `status`, `town` | text | Copied for convenience |
| `nearest_facility_id` | text | FK → facilities (operational only) |
| `nearest_facility_name` | text | |
| `nearest_facility_miles` | float | Great-circle distance |
| `proximity_ring` | text | `<= 1 mi` / `<= 3 mi` / `<= 5 mi` / `> 5 mi` (config-driven) |
| `hazard_exposed` | text | Y/N — incident inside a hazard zone |
| `priority_score` | integer | severity + open + hazard + coverage weights |
| `priority_category` | text | P1 - Immediate / P2 - Urgent / P3 - Routine / P4 - Monitor |

### `facility_hazard_exposure.csv` → table `hazard_exposure`

| Field | Type | Notes |
|---|---|---|
| `asset_id` | text | facility/shelter/hospital id |
| `asset_name` | text | |
| `asset_class` | text | Emergency Facility / Shelter / Hospital |
| `town` | text | |
| `hazard_zone_id` | text | hazard zone containing the asset, or blank |
| `hazard_exposed` | text | Y/N |

### `qa_results.csv` → table `qa_results`

| Field | Type | Notes |
|---|---|---|
| `dataset` | text | Source file |
| `check_id` | text | CHK-01 … CHK-06 |
| `severity` | text | ERROR / WARNING |
| `record_id` | text | Primary key of the offending record |
| `field` | text | Field involved |
| `detail` | text | Human-readable explanation |

## Priority scoring model (script 04)

`priority_score = severity_weight + open_weight + hazard_weight + coverage_weight`

- severity_weight: Low=1, Moderate=2, High=3, Critical=4
- open_weight: +2 if status is Open or In Progress
- hazard_weight: +2 if the incident is inside a hazard zone
- coverage_weight: +1 if the nearest facility is farther than the largest ring

| Score | Category |
|---|---|
| ≥ 7 | P1 - Immediate |
| 5–6 | P2 - Urgent |
| 3–4 | P3 - Routine |
| < 3 | P4 - Monitor |
