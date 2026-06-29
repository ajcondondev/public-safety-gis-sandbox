# Architecture

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Diagrams of how the project is put together. (GitHub renders the Mermaid blocks
below as diagrams.)

## Pipeline & data flow

A layered design — sources → processed → analysis → serving → presentation —
mirroring an enterprise GIS stack (e.g. ArcGIS Enterprise / SDE / SQL Server).

```mermaid
flowchart TD
    subgraph SRC[1 - Source layer]
        RAW[data/raw/<br/>authoritative data you supply]
        SIM[data/simulated/<br/>generated demo data - script 01]
    end
    subgraph PROC[2 - Processed layer]
        CLEAN[data/processed/<br/>standardized CSVs - script 02]
        GEO[outputs/geojson/<br/>map-ready layers - script 02]
    end
    subgraph QA[Quality gate]
        VAL[script 03 - validate<br/>qa_qc_report.md + qa_results.csv]
    end
    subgraph ANA[3 - Analysis layer]
        PROX[script 04 - proximity / hazard / priority<br/>incidents_analyzed.geojson]
    end
    subgraph SERVE[4 - Serving layer]
        TBL[script 05 - dashboard tables]
        DB[(SQLite DB<br/>SQL Server stand-in)]
        REP[script 06 - summary_report.md]
        META[script 09 - FGDC/ISO metadata]
    end
    subgraph PRES[5 - Presentation layer]
        MAP[script 07 - Leaflet map + PNG maps]
        DASH[script 08 - HTML dashboard]
        ESRI[ArcGIS Pro / AGOL / Dashboards / StoryMaps<br/>manual - see docs]
    end

    RAW --> CLEAN
    SIM --> CLEAN
    CLEAN --> GEO
    CLEAN --> VAL
    GEO --> PROX
    VAL -. errors block publishing .-> CLEAN
    PROX --> TBL
    PROX --> MAP
    TBL --> DB
    TBL --> REP
    TBL --> DASH
    GEO --> META
    GEO --> MAP
    GEO --> ESRI
    DB --> DASH
```

## Data model (relational schema)

The SQLite schema (`sql/schema.sql`) loaded by script 05. A town reference table
is the spatial backbone; incidents/facilities/shelters/hospitals relate to it by
town name; derived analysis and QA tables hang off the operational tables.

```mermaid
erDiagram
    TOWNS ||--o{ FACILITIES : "located in"
    TOWNS ||--o{ SHELTERS : "located in"
    TOWNS ||--o{ HOSPITALS : "located in"
    TOWNS ||--o{ INCIDENTS : "occur in"
    INCIDENTS ||--|| INCIDENT_PROXIMITY : "analyzed as"
    FACILITIES ||--o{ INCIDENT_PROXIMITY : "nearest to"
    FACILITIES ||--o{ HAZARD_EXPOSURE : "assessed in"

    TOWNS {
        text town_id PK
        text town_name
        text county
        int  population
        real latitude
        real longitude
    }
    FACILITIES {
        text facility_id PK
        text facility_type
        text town FK
        text operational_status
        real latitude
        real longitude
    }
    SHELTERS {
        text shelter_id PK
        text town FK
        int  capacity
        text status
    }
    HOSPITALS {
        text hospital_id PK
        text town FK
        text trauma_level
        int  beds
    }
    INCIDENTS {
        text incident_id PK
        text incident_type
        text severity
        text town FK
        text status
    }
    INCIDENT_PROXIMITY {
        text incident_id FK
        text nearest_facility_id FK
        real nearest_facility_miles
        text hazard_exposed
        int  priority_score
        text priority_category
    }
    HAZARD_EXPOSURE {
        text asset_id
        text asset_class
        text town FK
        text hazard_exposed
    }
    QA_RESULTS {
        text dataset
        text check_id
        text severity
        text record_id
    }
```

## Pipeline stages at a glance

```mermaid
flowchart LR
    S1[01 generate] --> S2[02 clean] --> S3[03 validate] --> S4[04 analyze]
    S4 --> S5[05 tables + DB] --> S6[06 report] --> S7[07 maps] --> S8[08 dashboard] --> S9[09 metadata]
    style S3 fill:#fde7e7,stroke:#b30000
    style S7 fill:#e7f0fd,stroke:#1b3a5b
    style S8 fill:#e7f0fd,stroke:#1b3a5b
```

## How this maps to the Esri / enterprise stack

| This project (open-source) | Enterprise equivalent |
|---|---|
| `data/processed/` + `outputs/geojson/` | ArcGIS feature classes in a file/enterprise geodatabase |
| SQLite (`outputs/public_safety_gis.sqlite`) | SQL Server enterprise geodatabase (SDE) |
| `scripts/04` proximity / overlay | ArcGIS Pro `GenerateNearTable`, `Buffer`, `SelectLayerByLocation` |
| `outputs/maps/interactive_map.html` | ArcGIS Online web map + hosted feature layers |
| `outputs/dashboard/index.html` | ArcGIS Dashboards |
| `scripts/01`–`09` orchestration | ArcPy / ArcGIS Python API + scheduled tasks |
| `outputs/metadata/` | ArcGIS metadata (FGDC/ISO 19115) |
