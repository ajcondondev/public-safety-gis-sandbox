# QA/QC Validation Report

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

_Generated: 2026-06-29T20:19:18Z_  
_Config: `config\config.example.yml`_

## Summary

- **Datasets validated:** 5
- **Total records checked:** 176
- **Errors:** 7
- **Warnings:** 0

### Records & issues per dataset

| Dataset | Records | Errors | Warnings |
|---|---:|---:|---:|
| municipalities.csv | 10 | 0 | 0 |
| emergency_facilities.csv | 26 | 4 | 0 |
| shelters.csv | 14 | 0 | 0 |
| hospitals.csv | 6 | 0 | 0 |
| incidents.csv | 120 | 3 | 0 |

### Issues by check

| Check | Description | Count |
|---|---|---:|
| CHK-01 | Missing required field | 1 |
| CHK-02 | Missing coordinates | 2 |
| CHK-03 | Duplicate primary key | 2 |
| CHK-04 | Coordinate out of range | 2 |
| CHK-05 | Unknown town | 0 |
| CHK-06 | Value outside allowed domain | 0 |

## Detailed findings

| Dataset | Check | Severity | Record | Field | Detail |
|---|---|---|---|---|---|
| emergency_facilities.csv | CHK-01 | ERROR | F0008 | name | Required field is blank |
| emergency_facilities.csv | CHK-03 | ERROR | F0005 | facility_id | Duplicate primary key value |
| emergency_facilities.csv | CHK-03 | ERROR | F0005 | facility_id | Duplicate primary key value |
| emergency_facilities.csv | CHK-02 | ERROR | F0003 | latitude/longitude | Missing coordinate |
| incidents.csv | CHK-04 | ERROR | INC00004 | longitude | Longitude 71.45 outside [-72.2, -71.0] |
| incidents.csv | CHK-04 | ERROR | INC00009 | latitude | Latitude 99.9 outside [42.5, 43.6] |
| incidents.csv | CHK-02 | ERROR | INC00013 | latitude/longitude | Missing coordinate |

## What a GIS engineer would do next

- **Errors** block publishing: fix the source record (correct the coordinate sign, supply the missing location, resolve the duplicate ID) and re-run the pipeline.
- **Warnings** are reviewed case-by-case: an unknown town may be a legitimate neighbor outside the study corridor, or a typo to correct.
- Results are also written to `outputs/dashboard_tables/qa_results.csv` so they can be tracked over time in a dashboard or PowerBI report.
