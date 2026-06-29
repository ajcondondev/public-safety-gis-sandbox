# QA/QC Plan

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Ensuring GIS data is **accurate, reliable, and usable** is a core responsibility
of the GIS Solutions Engineer role. This plan defines the data-quality checks
applied to every dataset, how they are run, how results are reported, and how
issues are resolved.

## Objectives

1. Catch structural defects (missing keys, missing geometry, duplicates) **before** publishing.
2. Catch geographic defects (coordinates outside the study area, sign errors).
3. Catch domain defects (status/severity values outside the allowed set).
4. Produce **auditable** results: every finding has a check ID, severity, the offending record, and a plain-English explanation.

## Checks

| ID | Check | Severity | Rule |
|---|---|---|---|
| **CHK-01** | Missing required field | ERROR | A field marked required in `docs/data_dictionary.md` is blank or absent. |
| **CHK-02** | Missing coordinates | ERROR | `latitude` or `longitude` is null/blank on a record that needs geometry. |
| **CHK-03** | Duplicate primary key | ERROR | The same id value appears on more than one record. |
| **CHK-04** | Coordinate out of range | ERROR | `latitude`/`longitude` falls outside the corridor bounding box in `config`. |
| **CHK-05** | Unknown town | WARNING | `town` value is not in the corridor reference list (typo or legitimate neighbor). |
| **CHK-06** | Value outside domain | WARNING | A controlled field (status, severity, operational_status) holds an unlisted value. |

**ERROR** = blocks publishing; must be fixed at the source. **WARNING** =
reviewed case-by-case.

## How checks are run

```bash
python scripts/03_validate_gis_data.py
```

The validator reads the cleaned data in `data/processed/`, runs every check, and
writes two outputs:

- **`outputs/dashboard_tables/qa_results.csv`** — machine-readable; loaded into
  the SQLite `qa_results` table and consumable by a dashboard or PowerBI to
  trend data quality over time.
- **`outputs/reports/qa_qc_report.md`** — human-readable report with summary
  counts, a per-dataset breakdown, a per-check breakdown, and a detailed
  findings table.

The SQL equivalents live in `sql/qa_queries.sql` (run them against the database
to cross-check the same issues directly in SQL).

## Seeded defects (why the demo "fails" on purpose)

To prove the validation actually works, `scripts/01` deliberately injects defects
into the simulated data. The validator is expected to find **7 issues**:

| Seeded defect | Caught by |
|---|---|
| Facility with blank latitude & longitude | CHK-02 |
| Duplicate `facility_id` | CHK-03 |
| Facility with blank `name` | CHK-01 |
| Incident longitude with wrong sign (`71.45` instead of `-71.45`) | CHK-04 |
| Incident with impossible latitude (`99.9`) | CHK-04 |
| Incident with missing latitude | CHK-02 |
| Messy town casing/whitespace (`"  manchester "`) | *fixed* by cleaning (script 02); reported in its run log |

The messy town name is **repaired** during cleaning (normalized to
`Manchester`), demonstrating that some issues are fixed automatically while
structural defects are surfaced for human resolution.

## Resolution workflow

1. **Triage errors first.** Open `qa_qc_report.md`; every ERROR has a record id.
2. **Fix at the source.** Correct the coordinate sign, supply the missing
   location, or resolve the duplicate id in the source/raw data — not in the
   derived outputs.
3. **Re-run the pipeline** from `scripts/02` so the fix propagates.
4. **Confirm zero errors** before treating any layer as publish-ready.
5. **Review warnings.** An "unknown town" may be a legitimate neighboring
   municipality (add it to the reference list) or a typo (correct it).

## Extending the plan for real data

- Add **geometry validity** checks (self-intersections, null geometry) once
  GeoPandas/Shapely or ArcGIS is in the loop.
- Add **completeness thresholds** (e.g. ≥ 95% of facilities must have an
  address) and fail the build if not met.
- Add **temporal checks** (e.g. `last_updated` not older than N days).
- Track QA metrics over time in a dashboard to show data quality trending up.
