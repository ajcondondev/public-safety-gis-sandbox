"""
03_validate_gis_data.py
=======================
Run data-quality checks on the cleaned datasets and produce (a) a machine-
readable QA results table and (b) a human-readable Markdown QA/QC report.

GIS Solutions Engineer mapping:
  * Data quality / QA-QC — "ensure GIS server data is accurate, reliable, and
    usable." This is the validation workflow a hiring manager wants to see.
  * Compliance mindset — each check has an ID, a severity, and a written rule
    so results are defensible and repeatable (see docs/qa_qc_plan.md).
  * Communication — results are emitted BOTH as CSV (loads into SQLite /
    PowerBI / a dashboard) and as Markdown (a stakeholder can read it).

Checks implemented:
  CHK-01 Missing required field      (ERROR)
  CHK-02 Missing coordinates         (ERROR)
  CHK-03 Duplicate primary key       (ERROR)
  CHK-04 Coordinate out of range     (ERROR)
  CHK-05 Unknown town (not in corridor reference list)  (WARNING)
  CHK-06 Value outside allowed domain (e.g. status)     (WARNING)

Run:  python scripts/03_validate_gis_data.py
"""

from __future__ import annotations

import math

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, write_csv, now_iso

# Required fields per dataset (CHK-01) and the primary-key field (CHK-03).
REQUIRED = {
    "municipalities.csv": (["town_id", "town_name"], "town_id"),
    "emergency_facilities.csv": (["facility_id", "name", "facility_type", "town"], "facility_id"),
    "shelters.csv": (["shelter_id", "name", "town"], "shelter_id"),
    "hospitals.csv": (["hospital_id", "name", "town"], "hospital_id"),
    "incidents.csv": (["incident_id", "incident_type", "severity", "town"], "incident_id"),
}

# Allowed value domains (CHK-06). Anything else is flagged as a WARNING.
DOMAINS = {
    "incidents.csv": {
        "severity": {"Low", "Moderate", "High", "Critical"},
        "status": {"Open", "In Progress", "Closed"},
    },
    "shelters.csv": {"status": {"Open", "Standby", "Closed"}},
    "emergency_facilities.csv": {
        "operational_status": {"Operational", "Limited", "Out of Service"}},
}

CANONICAL_TOWNS = {"Concord", "Bow", "Pembroke", "Allenstown", "Hooksett",
                   "Dunbarton", "Goffstown", "Manchester", "Auburn", "Candia"}


def _is_blank(v) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def validate_dataset(fname: str, df: pd.DataFrame, cfg: dict) -> list[dict]:
    """Run every check against one dataset; return a list of issue records."""
    issues: list[dict] = []
    req_fields, pk = REQUIRED[fname]
    v = cfg["validation"]

    def add(check, severity, record_id, field, detail):
        issues.append({
            "dataset": fname, "check_id": check, "severity": severity,
            "record_id": record_id, "field": field, "detail": detail,
        })

    # CHK-01 missing required fields.
    for field in req_fields:
        if field not in df.columns:
            add("CHK-01", "ERROR", "(schema)", field, "Required column missing entirely")
            continue
        for idx, val in df[field].items():
            if _is_blank(val):
                rid = df.at[idx, pk] if pk in df.columns and not _is_blank(df.at[idx, pk]) else f"row {idx}"
                add("CHK-01", "ERROR", rid, field, "Required field is blank")

    # CHK-03 duplicate primary keys.
    if pk in df.columns:
        dupes = df[pk][df[pk].duplicated(keep=False) & df[pk].notna()]
        for idx, val in dupes.items():
            add("CHK-03", "ERROR", val, pk, "Duplicate primary key value")

    # Coordinate checks (CHK-02 / CHK-04) only for datasets that have coords.
    if {"latitude", "longitude"}.issubset(df.columns):
        for idx, row in df.iterrows():
            rid = row[pk] if pk in df.columns and not _is_blank(row[pk]) else f"row {idx}"
            lat, lon = row["latitude"], row["longitude"]
            if _is_blank(lat) or _is_blank(lon):
                add("CHK-02", "ERROR", rid, "latitude/longitude", "Missing coordinate")
                continue
            if not (v["lat_min"] <= lat <= v["lat_max"]):
                add("CHK-04", "ERROR", rid, "latitude",
                    f"Latitude {lat} outside [{v['lat_min']}, {v['lat_max']}]")
            if not (v["lon_min"] <= lon <= v["lon_max"]):
                add("CHK-04", "ERROR", rid, "longitude",
                    f"Longitude {lon} outside [{v['lon_min']}, {v['lon_max']}]")

    # CHK-05 unknown town.
    if "town" in df.columns:
        for idx, val in df["town"].items():
            if isinstance(val, str) and val and val not in CANONICAL_TOWNS:
                rid = df.at[idx, pk] if pk in df.columns and not _is_blank(df.at[idx, pk]) else f"row {idx}"
                add("CHK-05", "WARNING", rid, "town", f"Town '{val}' not in corridor reference list")

    # CHK-06 domain checks.
    for field, allowed in DOMAINS.get(fname, {}).items():
        if field in df.columns:
            for idx, val in df[field].items():
                if isinstance(val, str) and val and val not in allowed:
                    rid = df.at[idx, pk] if pk in df.columns and not _is_blank(df.at[idx, pk]) else f"row {idx}"
                    add("CHK-06", "WARNING", rid, field, f"Value '{val}' outside allowed domain")

    return issues


def write_markdown_report(all_issues: list[dict], stats: list[dict], cfg: dict) -> str:
    """Render the QA/QC report as Markdown for stakeholders."""
    lines = []
    lines.append("# QA/QC Validation Report")
    lines.append("")
    lines.append("> **This is a portfolio demonstration using public or simulated data. "
                 "It is not an official emergency management product and should not be used "
                 "for operational decision-making.**")
    lines.append("")
    lines.append(f"_Generated: {now_iso(seconds=True)}_  ")
    lines.append(f"_Config: `{cfg['_config_path'].split('GIS_Project')[-1].lstrip(chr(92))}`_")
    lines.append("")

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Datasets validated:** {len(stats)}")
    lines.append(f"- **Total records checked:** {sum(s['records'] for s in stats)}")
    lines.append(f"- **Errors:** {len(errors)}")
    lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append("")

    lines.append("### Records & issues per dataset")
    lines.append("")
    lines.append("| Dataset | Records | Errors | Warnings |")
    lines.append("|---|---:|---:|---:|")
    for s in stats:
        e = len([i for i in all_issues if i["dataset"] == s["dataset"] and i["severity"] == "ERROR"])
        w = len([i for i in all_issues if i["dataset"] == s["dataset"] and i["severity"] == "WARNING"])
        lines.append(f"| {s['dataset']} | {s['records']} | {e} | {w} |")
    lines.append("")

    lines.append("### Issues by check")
    lines.append("")
    descriptions = {
        "CHK-01": "Missing required field",
        "CHK-02": "Missing coordinates",
        "CHK-03": "Duplicate primary key",
        "CHK-04": "Coordinate out of range",
        "CHK-05": "Unknown town",
        "CHK-06": "Value outside allowed domain",
    }
    counts = {}
    for i in all_issues:
        counts[i["check_id"]] = counts.get(i["check_id"], 0) + 1
    lines.append("| Check | Description | Count |")
    lines.append("|---|---|---:|")
    for cid in sorted(descriptions):
        lines.append(f"| {cid} | {descriptions[cid]} | {counts.get(cid, 0)} |")
    lines.append("")

    if all_issues:
        lines.append("## Detailed findings")
        lines.append("")
        lines.append("| Dataset | Check | Severity | Record | Field | Detail |")
        lines.append("|---|---|---|---|---|---|")
        for i in all_issues:
            lines.append(f"| {i['dataset']} | {i['check_id']} | {i['severity']} | "
                         f"{i['record_id']} | {i['field']} | {i['detail']} |")
        lines.append("")
    else:
        lines.append("No issues found. ✅")
        lines.append("")

    lines.append("## What a GIS engineer would do next")
    lines.append("")
    lines.append("- **Errors** block publishing: fix the source record (correct the "
                 "coordinate sign, supply the missing location, resolve the duplicate ID) "
                 "and re-run the pipeline.")
    lines.append("- **Warnings** are reviewed case-by-case: an unknown town may be a "
                 "legitimate neighbor outside the study corridor, or a typo to correct.")
    lines.append("- Results are also written to `outputs/dashboard_tables/qa_results.csv` "
                 "so they can be tracked over time in a dashboard or PowerBI report.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)
    processed_dir = cfg["paths"]["processed"]

    all_issues: list[dict] = []
    stats: list[dict] = []

    for fname in REQUIRED:
        path = repo_path(processed_dir, fname)
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            log(f"SKIP {fname}: not found in processed/. Run script 02 first.")
            continue
        issues = validate_dataset(fname, df, cfg)
        all_issues.extend(issues)
        stats.append({"dataset": fname, "records": len(df)})
        e = len([i for i in issues if i["severity"] == "ERROR"])
        w = len([i for i in issues if i["severity"] == "WARNING"])
        log(f"Validated {fname:28s} records={len(df):4d}  errors={e}  warnings={w}")

    # Machine-readable results (feeds SQLite / dashboard / PowerBI).
    qa_csv = repo_path(cfg["paths"]["dashboard_tables"], "qa_results.csv")
    write_csv(qa_csv,
              ["dataset", "check_id", "severity", "record_id", "field", "detail"],
              all_issues)
    log(f"Wrote QA results table -> {qa_csv}")

    # Human-readable Markdown report.
    report = write_markdown_report(all_issues, stats, cfg)
    report_path = repo_path(cfg["paths"]["reports"], "qa_qc_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    log(f"Wrote QA/QC report -> {report_path}")

    errors = len([i for i in all_issues if i["severity"] == "ERROR"])
    warnings = len([i for i in all_issues if i["severity"] == "WARNING"])
    log(f"Validation complete: {errors} errors, {warnings} warnings. "
        f"Next: python scripts/04_generate_analysis_layers.py")


if __name__ == "__main__":
    main()
