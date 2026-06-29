"""
06_generate_summary_report.py
=============================
Roll the whole pipeline up into a single plain-English Markdown report with the
headline metrics an emergency manager or agency leader would want at a glance.

GIS Solutions Engineer mapping:
  * Stakeholder communication — "turn data layers into reports" and "explain
    technical information clearly." This script is the bridge from analysis to
    audience.
  * Decision support — surfaces the action items (open high-severity incidents,
    coverage gaps, hazard-exposed assets), not just raw counts.

Reads the processed data, the analysis tables, and the QA results, then writes
outputs/reports/summary_report.md.

Run:  python scripts/06_generate_summary_report.py
"""

from __future__ import annotations

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, now_iso

DISCLAIMER = ("> **This is a portfolio demonstration using public or simulated "
              "data. It is not an official emergency management product and "
              "should not be used for operational decision-making.**")


def tbl(cfg, fname):
    return pd.read_csv(repo_path(cfg["paths"]["dashboard_tables"], fname))


def df_to_md(df: pd.DataFrame) -> str:
    """Minimal DataFrame -> Markdown table (no external dependency)."""
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in cols) + " |")
    return "\n".join(out)


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)

    incidents = pd.read_csv(repo_path(cfg["paths"]["processed"], "incidents.csv"))
    facilities = pd.read_csv(repo_path(cfg["paths"]["processed"], "emergency_facilities.csv"))
    shelters = pd.read_csv(repo_path(cfg["paths"]["processed"], "shelters.csv"))
    hospitals = pd.read_csv(repo_path(cfg["paths"]["processed"], "hospitals.csv"))

    town_summary = tbl(cfg, "town_readiness_summary.csv")
    prox = tbl(cfg, "incident_facility_proximity.csv")
    qa = tbl(cfg, "qa_results.csv")
    exposure = tbl(cfg, "facility_hazard_exposure.csv")

    # Headline metrics.
    total_incidents = len(incidents)
    open_high = incidents[incidents["status"].isin(["Open", "In Progress"]) &
                          incidents["severity"].isin(["High", "Critical"])]
    open_shelters = shelters[shelters["status"] == "Open"]
    p1p2 = prox[prox["priority_category"].isin(["P1 - Immediate", "P2 - Urgent"])]
    coverage_gaps = prox[(prox["priority_category"].isin(["P1 - Immediate", "P2 - Urgent"])) &
                         (prox["nearest_facility_miles"] > 3.0)]
    exposed = exposure[exposure["hazard_exposed"] == "Y"]
    errors = len(qa[qa["severity"] == "ERROR"])
    warnings = len(qa[qa["severity"] == "WARNING"])

    L = []
    L.append("# Public-Safety GIS Sandbox — Summary Report")
    L.append("")
    L.append("_Concord–Manchester, New Hampshire corridor_")
    L.append("")
    L.append(DISCLAIMER)
    L.append("")
    L.append(f"_Generated: {now_iso(seconds=True)}_")
    L.append("")
    L.append("## At a glance")
    L.append("")
    L.append("| Indicator | Value |")
    L.append("|---|---:|")
    L.append(f"| Total incidents (simulated) | {total_incidents} |")
    L.append(f"| Open high-severity incidents | {len(open_high)} |")
    L.append(f"| Incidents flagged P1/P2 (priority) | {len(p1p2)} |")
    L.append(f"| Coverage-gap incidents (P1/P2 & >3 mi to facility) | {len(coverage_gaps)} |")
    L.append(f"| Emergency facilities | {len(facilities)} |")
    L.append(f"| Shelters (open now) | {len(open_shelters)} of {len(shelters)} |")
    L.append(f"| Total shelter capacity | {int(shelters['capacity'].sum())} |")
    L.append(f"| Hospitals | {len(hospitals)} |")
    L.append(f"| Hazard-exposed assets | {len(exposed)} |")
    L.append(f"| Data-quality issues (errors / warnings) | {errors} / {warnings} |")
    L.append("")

    L.append("## Town readiness")
    L.append("")
    L.append("Towns ranked by simulated incident load, with the local resources and "
             "hazard exposure that shape response planning.")
    L.append("")
    L.append(df_to_md(town_summary))
    L.append("")

    L.append("## Where to look first: open high-severity incidents")
    L.append("")
    if len(open_high):
        view = open_high[["incident_id", "incident_type", "severity", "town",
                          "status", "reported_at"]].sort_values("severity")
        L.append(df_to_md(view))
    else:
        L.append("_None in the current simulated dataset._")
    L.append("")

    L.append("## Coverage gaps for planning")
    L.append("")
    L.append(f"{len(coverage_gaps)} high-priority incident(s) sit more than 3 miles from the "
             "nearest operational facility. In a real deployment these are the locations a "
             "planner would examine for mutual-aid agreements, pre-positioning, or new "
             "station siting.")
    L.append("")
    if len(coverage_gaps):
        view = coverage_gaps[["incident_id", "town", "severity",
                              "nearest_facility_miles", "priority_category"]] \
            .sort_values("nearest_facility_miles", ascending=False).head(10)
        L.append(df_to_md(view))
        L.append("")

    L.append("## Data quality")
    L.append("")
    L.append(f"This run found **{errors} errors** and **{warnings} warnings** across the "
             "datasets. Full detail is in `outputs/reports/qa_qc_report.md`. Errors must be "
             "resolved before any of this data could be considered for operational use.")
    L.append("")

    L.append("## How this supports emergency planning & response")
    L.append("")
    L.append("- **Planning:** town-level rollups show where incident load is high relative "
             "to local facilities, shelter capacity, and hazard exposure.")
    L.append("- **Response:** the priority score ranks incidents so limited resources go to "
             "the most urgent first; proximity tells responders the nearest asset.")
    L.append("- **Situational awareness:** the GeoJSON layers drop straight into an ArcGIS "
             "Online web map or dashboard for a live operating picture.")
    L.append("- **Accountability:** the QA report documents exactly what is and isn't "
             "trustworthy in the data — essential before any decision is made on it.")
    L.append("")

    report_path = repo_path(cfg["paths"]["reports"], "summary_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    log(f"Wrote summary report -> {report_path}")
    log("Pipeline complete. ✅  Review outputs/ and docs/ next.")


if __name__ == "__main__":
    main()
