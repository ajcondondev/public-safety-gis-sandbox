"""
05_export_dashboard_tables.py
=============================
Build the "serving layer": (a) aggregated CSV tables ready to drop into ArcGIS
Dashboards or PowerBI, and (b) a SQLite database that stands in for SQL Server,
loaded from schema.sql plus the cleaned/analyzed data.

GIS Solutions Engineer mapping:
  * Dashboard readiness — every CSV here maps to a specific dashboard indicator
    (incidents by town, shelters by status, facilities by type, hazard-exposed
    assets) described in docs/dashboard_design.md.
  * SQL Server skills — SQLite is a zero-install stand-in. We execute the same
    schema.sql DDL and load relational tables, so the SQL queries in /sql run
    unchanged in spirit against a real SQL Server enterprise geodatabase.
  * Data architecture — separates raw -> processed -> serving, the same layering
    used in enterprise GIS / SDE environments.

Run:  python scripts/05_export_dashboard_tables.py
"""

from __future__ import annotations

import os
import sqlite3

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, write_csv


def load_processed(cfg: dict, fname: str) -> pd.DataFrame:
    return pd.read_csv(repo_path(cfg["paths"]["processed"], fname))


def load_table(cfg: dict, folder_key: str, fname: str) -> pd.DataFrame:
    return pd.read_csv(repo_path(cfg["paths"][folder_key], fname))


def df_to_rows(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def build_dashboard_tables(cfg: dict) -> dict:
    """Compute aggregate tables and write them as CSVs. Returns the DataFrames."""
    dash_dir = cfg["paths"]["dashboard_tables"]

    facilities = load_processed(cfg, "emergency_facilities.csv")
    shelters = load_processed(cfg, "shelters.csv")
    hospitals = load_processed(cfg, "hospitals.csv")
    incidents = load_processed(cfg, "incidents.csv")
    municipalities = load_processed(cfg, "municipalities.csv")
    proximity = load_table(cfg, "dashboard_tables", "incident_facility_proximity.csv")
    exposure = load_table(cfg, "dashboard_tables", "facility_hazard_exposure.csv")

    tables = {}

    # Incidents by town.
    t = incidents.groupby("town").size().reset_index(name="incident_count")
    tables["incidents_by_town.csv"] = t

    # Incidents by type.
    tables["incidents_by_type.csv"] = (
        incidents.groupby("incident_type").size()
        .reset_index(name="incident_count").sort_values("incident_count", ascending=False))

    # Incidents by severity.
    tables["incidents_by_severity.csv"] = (
        incidents.groupby("severity").size().reset_index(name="incident_count"))

    # Open high-severity incidents (key emergency-manager indicator).
    open_high = incidents[
        incidents["status"].isin(["Open", "In Progress"]) &
        incidents["severity"].isin(["High", "Critical"])]
    tables["open_high_severity_incidents.csv"] = open_high[
        ["incident_id", "incident_type", "severity", "town", "status",
         "latitude", "longitude", "reported_at"]]

    # Facilities by type.
    tables["facilities_by_type.csv"] = (
        facilities.groupby("facility_type").size()
        .reset_index(name="facility_count").sort_values("facility_count", ascending=False))

    # Shelters by status (+ capacity).
    shelter_status = shelters.groupby("status").agg(
        shelter_count=("shelter_id", "size"),
        total_capacity=("capacity", "sum")).reset_index()
    tables["shelters_by_status.csv"] = shelter_status

    # Hazard-exposed assets by class.
    exposed = exposure[exposure["hazard_exposed"] == "Y"]
    tables["hazard_exposed_assets.csv"] = (
        exposed.groupby("asset_class").size().reset_index(name="exposed_count"))

    # --- Town readiness summary (the flagship cross-layer table) -------------
    rows = []
    for _, town in municipalities.iterrows():
        name = town["town_name"]
        t_inc = incidents[incidents["town"] == name]
        t_open_high = t_inc[t_inc["status"].isin(["Open", "In Progress"]) &
                            t_inc["severity"].isin(["High", "Critical"])]
        t_fac = facilities[facilities["town"] == name]
        t_shel = shelters[shelters["town"] == name]
        t_hosp = hospitals[hospitals["town"] == name]
        t_exposed = exposure[(exposure["town"] == name) & (exposure["hazard_exposed"] == "Y")]
        rows.append({
            "town": name,
            "county": town["county"],
            "population": town["population"],
            "incident_count": len(t_inc),
            "open_high_severity": len(t_open_high),
            "facility_count": len(t_fac),
            "shelter_count": len(t_shel),
            "shelter_capacity": int(t_shel["capacity"].sum()) if len(t_shel) else 0,
            "hospital_count": len(t_hosp),
            "hazard_exposed_assets": len(t_exposed),
        })
    town_summary = pd.DataFrame(rows).sort_values("incident_count", ascending=False)
    tables["town_readiness_summary.csv"] = town_summary

    # Write every table.
    for fname, df in tables.items():
        path = repo_path(dash_dir, fname)
        df.to_csv(path, index=False)
        log(f"Wrote dashboard table {fname:34s} rows={len(df)}")

    return {
        "facilities": facilities, "shelters": shelters, "hospitals": hospitals,
        "incidents": incidents, "municipalities": municipalities,
        "proximity": proximity, "exposure": exposure,
        "town_summary": town_summary,
    }


def build_sqlite(cfg: dict, data: dict) -> None:
    """
    Create the SQLite database from sql/schema.sql and load the cleaned and
    analyzed tables. This is the SQL Server stand-in: the same relational model
    a GIS engineer would build in an enterprise geodatabase / SDE.
    """
    db_path = repo_path(cfg["paths"]["database"])
    if os.path.exists(db_path):
        os.remove(db_path)  # rebuild from scratch each run (reproducible)

    schema_sql = repo_path("sql", "schema.sql")
    with open(schema_sql, "r", encoding="utf-8") as fh:
        ddl = fh.read()

    qa = load_table(cfg, "dashboard_tables", "qa_results.csv")

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(ddl)
        # Load each DataFrame into its table (schema columns are a superset-safe
        # match; pandas writes matching columns).
        data["municipalities"].to_sql("towns", conn, if_exists="append", index=False)
        data["facilities"].to_sql("facilities", conn, if_exists="append", index=False)
        data["shelters"].to_sql("shelters", conn, if_exists="append", index=False)
        data["hospitals"].to_sql("hospitals", conn, if_exists="append", index=False)
        data["incidents"].to_sql("incidents", conn, if_exists="append", index=False)
        data["proximity"].to_sql("incident_proximity", conn, if_exists="append", index=False)
        data["exposure"].to_sql("hazard_exposure", conn, if_exists="append", index=False)
        qa.to_sql("qa_results", conn, if_exists="append", index=False)
        conn.commit()

        # Report row counts so the run log proves the load worked.
        for tbl in ("towns", "facilities", "shelters", "hospitals", "incidents",
                    "incident_proximity", "hazard_exposure", "qa_results"):
            n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            log(f"  SQLite table {tbl:20s} rows={n}")
    finally:
        conn.close()
    log(f"Built SQLite database -> {db_path}")


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)
    data = build_dashboard_tables(cfg)
    build_sqlite(cfg, data)
    log("Dashboard tables + database complete. Next: python scripts/06_generate_summary_report.py")


if __name__ == "__main__":
    main()
