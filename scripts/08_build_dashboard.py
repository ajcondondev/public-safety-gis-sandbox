"""
08_build_dashboard.py
=====================
Build a self-contained, browser-openable operational dashboard from the CSVs in
outputs/dashboard_tables/. No server, no dependencies beyond pandas — open
outputs/dashboard/index.html in any browser.

GIS Solutions Engineer mapping:
  * Dashboard readiness / visualization — the open-source equivalent of an
    ArcGIS Dashboard, proving the design in docs/dashboard_design.md actually
    renders. KPI tiles, charts, and an "act-now" incident list in one view.
  * Decision support — surfaces open high-severity incidents and coverage gaps,
    not just totals.

Charts are inline SVG (hand-built), so the page is fully self-contained and
prints/screenshots cleanly for a portfolio.

Run:  python scripts/08_build_dashboard.py   (after script 05)
"""

from __future__ import annotations

import os

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, now_iso

DISCLAIMER = ("Portfolio demonstration using public or simulated data — "
              "not an official emergency management product and not for "
              "operational decision-making.")
SEV_COLORS = {"Low": "#1a9850", "Moderate": "#fdae61",
              "High": "#e34a33", "Critical": "#b30000"}
PRIORITY_COLORS = {"P1 - Immediate": "#b30000", "P2 - Urgent": "#e34a33",
                   "P3 - Routine": "#fdae61", "P4 - Monitor": "#9aa0a6"}


def tbl(cfg, name):
    return pd.read_csv(repo_path(cfg["paths"]["dashboard_tables"], name))


def bar_chart_svg(labels, values, colors=None, width=420, height=220, unit=""):
    """Hand-built horizontal-ish vertical bar chart as inline SVG."""
    if not len(values):
        return "<svg></svg>"
    pad_l, pad_b, pad_t = 30, 60, 10
    plot_w, plot_h = width - pad_l - 10, height - pad_b - pad_t
    vmax = max(values) or 1
    n = len(values)
    bw = plot_w / n * 0.7
    gap = plot_w / n
    bars = []
    for i, (lab, val) in enumerate(zip(labels, values)):
        h = (val / vmax) * plot_h
        x = pad_l + i * gap + (gap - bw) / 2
        y = pad_t + (plot_h - h)
        color = (colors[i] if colors else "#2166ac")
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" '
            f'fill="{color}"><title>{lab}: {val}{unit}</title></rect>'
            f'<text x="{x + bw/2:.1f}" y="{y - 3:.1f}" font-size="10" '
            f'text-anchor="middle" fill="#333">{val}</text>'
            f'<text x="{x + bw/2:.1f}" y="{height - pad_b + 14:.1f}" font-size="9" '
            f'text-anchor="end" fill="#333" transform="rotate(-35 {x + bw/2:.1f} '
            f'{height - pad_b + 14:.1f})">{lab}</text>')
    axis = (f'<line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{width-10}" '
            f'y2="{pad_t + plot_h}" stroke="#999"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" role="img">{axis}{"".join(bars)}</svg>')


def kpi_card(label, value, accent="#2166ac"):
    return (f'<div class="kpi"><div class="kpi-val" style="color:{accent}">{value}</div>'
            f'<div class="kpi-lbl">{label}</div></div>')


def df_to_html_table(df, max_rows=15):
    df = df.head(max_rows)
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = ""
    for _, r in df.iterrows():
        rows += "<tr>" + "".join(
            f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in df.columns) + "</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


def main():
    cfg = load_config()
    ensure_dirs(cfg)

    incidents = pd.read_csv(repo_path(cfg["paths"]["processed"], "incidents.csv"))
    shelters = pd.read_csv(repo_path(cfg["paths"]["processed"], "shelters.csv"))
    facilities = pd.read_csv(repo_path(cfg["paths"]["processed"], "emergency_facilities.csv"))
    hospitals = pd.read_csv(repo_path(cfg["paths"]["processed"], "hospitals.csv"))

    by_town = tbl(cfg, "incidents_by_town.csv").sort_values("incident_count", ascending=False)
    by_sev = tbl(cfg, "incidents_by_severity.csv")
    by_type = tbl(cfg, "facilities_by_type.csv")
    shel_status = tbl(cfg, "shelters_by_status.csv")
    prox = tbl(cfg, "incident_facility_proximity.csv")
    qa = tbl(cfg, "qa_results.csv")
    town_summary = tbl(cfg, "town_readiness_summary.csv")

    open_high = incidents[incidents["status"].isin(["Open", "In Progress"]) &
                          incidents["severity"].isin(["High", "Critical"])]
    coverage_gaps = prox[(prox["priority_category"].isin(["P1 - Immediate", "P2 - Urgent"])) &
                         (prox["nearest_facility_miles"] > 3.0)]
    prio_counts = prox["priority_category"].value_counts()

    # --- KPI tiles ----------------------------------------------------------
    kpis = "".join([
        kpi_card("Total incidents", len(incidents)),
        kpi_card("Open high-severity", len(open_high), "#b30000"),
        kpi_card("Coverage gaps (P1/P2 >3mi)", len(coverage_gaps), "#e34a33"),
        kpi_card("Shelters open", f"{(shelters['status']=='Open').sum()}/{len(shelters)}", "#1a9850"),
        kpi_card("Shelter capacity", int(shelters["capacity"].sum()), "#1a9850"),
        kpi_card("Facilities", len(facilities)),
        kpi_card("Hospitals", len(hospitals), "#762a83"),
        kpi_card("Data-quality errors", int((qa["severity"] == "ERROR").sum()), "#cc4c02"),
    ])

    # --- Charts -------------------------------------------------------------
    sev_order = ["Low", "Moderate", "High", "Critical"]
    by_sev = by_sev.set_index("severity").reindex(sev_order).fillna(0).reset_index()
    chart_sev = bar_chart_svg(by_sev["severity"].tolist(),
                              [int(v) for v in by_sev["incident_count"]],
                              [SEV_COLORS[s] for s in by_sev["severity"]])
    chart_town = bar_chart_svg(by_town["town"].tolist(),
                               by_town["incident_count"].tolist(), width=520)
    chart_type = bar_chart_svg(by_type["facility_type"].tolist(),
                               by_type["facility_count"].tolist(), width=520)
    prio_labels = [p for p in PRIORITY_COLORS if p in prio_counts.index]
    chart_prio = bar_chart_svg(prio_labels, [int(prio_counts[p]) for p in prio_labels],
                               [PRIORITY_COLORS[p] for p in prio_labels])
    chart_shel = bar_chart_svg(shel_status["status"].tolist(),
                               shel_status["shelter_count"].tolist(),
                               ["#1a9850" if s == "Open" else "#f0a30a" if s == "Standby"
                                else "#9aa0a6" for s in shel_status["status"]])

    # --- Tables -------------------------------------------------------------
    open_high_tbl = df_to_html_table(
        open_high[["incident_id", "incident_type", "severity", "town", "status", "reported_at"]]
        .sort_values("severity"))
    gap_tbl = df_to_html_table(
        coverage_gaps[["incident_id", "town", "severity", "nearest_facility_miles",
                       "priority_category"]].sort_values("nearest_facility_miles", ascending=False))
    town_tbl = df_to_html_table(town_summary, max_rows=10)

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Concord-Manchester Public Safety GIS — Dashboard</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f4f6f8; color: #222; }}
  header {{ background: #1b3a5b; color: #fff; padding: 14px 22px; }}
  header h1 {{ margin: 0 0 2px; font-size: 20px; }}
  .disclaimer {{ background: #fde7e7; color: #8a1a1a; padding: 8px 22px; font-size: 13px;
                 border-bottom: 1px solid #f3c0c0; }}
  .wrap {{ padding: 18px 22px; max-width: 1200px; margin: 0 auto; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
           gap: 12px; margin-bottom: 20px; }}
  .kpi {{ background: #fff; border-radius: 8px; padding: 14px; text-align: center;
          box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
  .kpi-val {{ font-size: 26px; font-weight: 700; }}
  .kpi-lbl {{ font-size: 12px; color: #555; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .panel {{ background: #fff; border-radius: 8px; padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin-bottom: 18px; }}
  .panel h3 {{ margin: 0 0 10px; font-size: 15px; color: #1b3a5b; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
  th, td {{ border-bottom: 1px solid #eee; padding: 5px 7px; text-align: left; }}
  th {{ background: #f0f3f6; }}
  a.maplink {{ display: inline-block; margin-top: 6px; color: #2166ac; }}
  footer {{ text-align: center; color: #888; font-size: 12px; padding: 18px; }}
  @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style></head>
<body>
<header>
  <h1>Concord–Manchester Public Safety GIS Readiness Dashboard</h1>
  <div>Operational view · generated {now_iso(seconds=True)}</div>
</header>
<div class="disclaimer"><b>DEMO:</b> {DISCLAIMER}</div>
<div class="wrap">
  <div class="kpis">{kpis}</div>

  <div class="panel">
    <h3>Live map</h3>
    <p style="font-size:13px;color:#555;margin:0">
      Interactive map of incidents (by priority), facilities, shelters, hospitals, and hazard zones.</p>
    <a class="maplink" href="../maps/interactive_map.html" target="_blank">▶ Open interactive map</a>
  </div>

  <div class="grid">
    <div class="panel"><h3>Incidents by town</h3>{chart_town}</div>
    <div class="panel"><h3>Facilities by type</h3>{chart_type}</div>
    <div class="panel"><h3>Incidents by severity</h3>{chart_sev}</div>
    <div class="panel"><h3>Incident priority breakdown</h3>{chart_prio}</div>
  </div>

  <div class="panel"><h3>Shelters by status</h3>{chart_shel}</div>

  <div class="panel"><h3>Open high-severity incidents (act-now list)</h3>{open_high_tbl}</div>
  <div class="panel"><h3>Coverage gaps — high priority &gt; 3 mi from a facility</h3>{gap_tbl}</div>
  <div class="panel"><h3>Town readiness summary</h3>{town_tbl}</div>
</div>
<footer>Concord–Manchester Public Safety GIS · portfolio demonstration · simulated data</footer>
</body></html>"""

    out_path = repo_path(cfg["paths"]["outputs"], "dashboard", "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    log(f"Wrote HTML dashboard -> {os.path.relpath(out_path, repo_path())}")

    write_portal(cfg, len(incidents), len(facilities), len(shelters), len(hospitals))
    log("Dashboard complete. Open outputs/dashboard/index.html in a browser.")


def write_portal(cfg, n_incidents, n_facilities, n_shelters, n_hospitals):
    """
    Write outputs/index.html — a single landing page that links every artifact
    (map, dashboard, reports, metadata). Makes the outputs/ folder self-navigating
    and ready to serve as a one-click demo (e.g. via GitHub Pages).
    """
    cards = [
        ("🗺️ Interactive map", "maps/interactive_map.html",
         "Pan/zoom/click incidents, facilities, shelters, hospitals, and hazard zones."),
        ("📊 Operational dashboard", "dashboard/index.html",
         "KPI tiles, charts, act-now incident list, and town readiness."),
        ("🧾 QA/QC report", "reports/qa_qc_report.md",
         "Data-quality findings from the validation stage."),
        ("📈 Summary report", "reports/summary_report.md",
         "Plain-English headline indicators for stakeholders."),
        ("🗂️ Layer metadata", "metadata/metadata.json",
         "FGDC/ISO-style metadata: lineage, CRS, extent, fields."),
        ("🛰️ Regional map (PNG)", "maps/regional_overview.png",
         "Static map of response assets across the corridor."),
    ]
    card_html = "".join(
        f'<a class="card" href="{href}"><div class="card-t">{title}</div>'
        f'<div class="card-d">{desc}</div></a>' for title, href, desc in cards)

    portal = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Concord-Manchester Public Safety GIS — Outputs</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f4f6f8; color: #222; }}
  header {{ background: #1b3a5b; color: #fff; padding: 22px; text-align: center; }}
  header h1 {{ margin: 0 0 4px; font-size: 22px; }}
  .disclaimer {{ background: #fde7e7; color: #8a1a1a; padding: 8px 22px; font-size: 13px; text-align: center; }}
  .stats {{ text-align: center; color: #555; padding: 14px; font-size: 14px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
           gap: 16px; max-width: 1000px; margin: 0 auto; padding: 0 22px 30px; }}
  .card {{ background: #fff; border-radius: 10px; padding: 18px; text-decoration: none;
           color: #1b3a5b; box-shadow: 0 1px 4px rgba(0,0,0,0.12); transition: transform .08s; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 3px 10px rgba(0,0,0,0.18); }}
  .card-t {{ font-size: 17px; font-weight: 700; margin-bottom: 6px; }}
  .card-d {{ font-size: 13px; color: #555; }}
  footer {{ text-align: center; color: #888; font-size: 12px; padding: 18px; }}
</style></head>
<body>
<header>
  <h1>🛰️ Concord–Manchester Public Safety GIS Readiness Dashboard</h1>
  <div>Generated outputs · {now_iso(seconds=True)}</div>
</header>
<div class="disclaimer"><b>DEMO:</b> {DISCLAIMER}</div>
<div class="stats">{n_incidents} simulated incidents · {n_facilities} facilities ·
  {n_shelters} shelters · {n_hospitals} hospitals</div>
<div class="grid">{card_html}</div>
<footer>Portfolio demonstration · simulated data · not for operational use</footer>
</body></html>"""

    portal_path = repo_path(cfg["paths"]["outputs"], "index.html")
    with open(portal_path, "w", encoding="utf-8") as fh:
        fh.write(portal)
    log(f"Wrote outputs portal  -> {os.path.relpath(portal_path, repo_path())}")


if __name__ == "__main__":
    main()
