-- =============================================================================
-- schema.sql — relational model for the Public Safety GIS pipeline
-- -----------------------------------------------------------------------------
-- Written for SQLite (a zero-install stand-in for SQL Server). The column names
-- match the cleaned CSVs exactly so the Python loader (script 05) can append
-- DataFrames directly. The same model maps cleanly onto a SQL Server enterprise
-- geodatabase / SDE: each table below would become a feature class or table,
-- with latitude/longitude replaced by a geometry/geography column.
--
-- GIS Solutions Engineer skill: data architecture — a normalized model with
-- a town reference table that incident/facility/shelter records relate to,
-- plus derived "analysis" and "QA" tables for the serving layer.
--
-- STAGING vs PRODUCTION: these are intentionally STAGING tables — the id
-- columns are NOT declared as enforced PRIMARY KEYs. That is deliberate: the
-- pipeline loads pre-validated data that is *known* to contain defects (e.g. a
-- duplicate facility_id), so the SQL QA queries in qa_queries.sql can actually
-- find them. In production you would promote clean rows into a second set of
-- tables WITH enforced PRIMARY KEY / FOREIGN KEY / NOT NULL constraints once
-- QA passes. The intended keys are noted in comments below (-- PK).
--
-- SQL Server note: to port, change REAL/TEXT to FLOAT/NVARCHAR, promote the
-- "-- PK" columns to PRIMARY KEY, and add a geometry column, e.g.:
--   geom AS geometry::Point(longitude, latitude, 4326)
-- =============================================================================

DROP TABLE IF EXISTS towns;
DROP TABLE IF EXISTS facilities;
DROP TABLE IF EXISTS shelters;
DROP TABLE IF EXISTS hospitals;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS incident_proximity;
DROP TABLE IF EXISTS hazard_exposure;
DROP TABLE IF EXISTS qa_results;

-- Town / municipality reference table (the spatial backbone) -----------------
CREATE TABLE towns (
    town_id       TEXT,            -- PK (enforced in production)
    town_name     TEXT NOT NULL,
    county        TEXT,
    population    INTEGER,
    area_sqmi     REAL,
    latitude      REAL,
    longitude     REAL,
    data_source   TEXT,
    last_updated  TEXT
);

-- Fire / Police / EMS / EOC / Public Works facilities ------------------------
CREATE TABLE facilities (
    facility_id        TEXT,            -- PK (enforced in production)
    name               TEXT,
    facility_type      TEXT,
    town               TEXT,
    address            TEXT,
    latitude           REAL,
    longitude          REAL,
    operational_status TEXT,
    data_source        TEXT,
    last_updated       TEXT
);

-- Emergency shelters ----------------------------------------------------------
CREATE TABLE shelters (
    shelter_id        TEXT,            -- PK (enforced in production)
    name              TEXT,
    town              TEXT,
    address           TEXT,
    latitude          REAL,
    longitude         REAL,
    capacity          INTEGER,
    status            TEXT,
    pet_friendly      TEXT,
    generator_backup  TEXT,
    data_source       TEXT,
    last_updated      TEXT
);

-- Hospitals / acute-care sites ------------------------------------------------
CREATE TABLE hospitals (
    hospital_id        TEXT,            -- PK (enforced in production)
    name               TEXT,
    town               TEXT,
    address            TEXT,
    latitude           REAL,
    longitude          REAL,
    trauma_level       TEXT,
    beds               INTEGER,
    operational_status TEXT,
    data_source        TEXT,
    last_updated       TEXT
);

-- Simulated incident feed -----------------------------------------------------
CREATE TABLE incidents (
    incident_id     TEXT,            -- PK (enforced in production)
    incident_type   TEXT,
    severity        TEXT,
    town            TEXT,
    latitude        REAL,
    longitude       REAL,
    reported_at     TEXT,
    status          TEXT,
    simulated_flag  TEXT
);

-- Derived: incident -> nearest facility proximity + priority (script 04) ------
CREATE TABLE incident_proximity (
    incident_id            TEXT,
    incident_type          TEXT,
    severity               TEXT,
    status                 TEXT,
    town                   TEXT,
    nearest_facility_id    TEXT,
    nearest_facility_name  TEXT,
    nearest_facility_miles REAL,
    proximity_ring         TEXT,
    hazard_exposed         TEXT,
    priority_score         INTEGER,
    priority_category      TEXT
);

-- Derived: hazard-zone exposure for fixed assets (script 04) -------------------
CREATE TABLE hazard_exposure (
    asset_id        TEXT,
    asset_name      TEXT,
    asset_class     TEXT,
    town            TEXT,
    hazard_zone_id  TEXT,
    hazard_exposed  TEXT
);

-- QA/QC findings (script 03) --------------------------------------------------
CREATE TABLE qa_results (
    dataset     TEXT,
    check_id    TEXT,
    severity    TEXT,
    record_id   TEXT,
    field       TEXT,
    detail      TEXT
);

-- Helpful indexes (mirror what you'd add for performance in SQL Server) -------
CREATE INDEX idx_incidents_town ON incidents(town);
CREATE INDEX idx_incidents_sev  ON incidents(severity);
CREATE INDEX idx_facilities_town ON facilities(town);
CREATE INDEX idx_qa_severity ON qa_results(severity);
