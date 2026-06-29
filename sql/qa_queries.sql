-- =============================================================================
-- qa_queries.sql — data-quality queries against the Public Safety GIS database
-- -----------------------------------------------------------------------------
-- Run against outputs/public_safety_gis.sqlite, e.g.:
--   sqlite3 outputs/public_safety_gis.sqlite ".read sql/qa_queries.sql"
-- These mirror the kind of QA monitoring a GIS engineer runs on GIS server data
-- to keep it "accurate, reliable, and usable."
-- =============================================================================

-- 1) Issue counts by severity (headline data-quality KPI) ---------------------
SELECT severity, COUNT(*) AS issue_count
FROM qa_results
GROUP BY severity
ORDER BY severity;

-- 2) Issue counts by check type ----------------------------------------------
SELECT check_id, severity, COUNT(*) AS issue_count
FROM qa_results
GROUP BY check_id, severity
ORDER BY check_id;

-- 3) Issues by dataset (where is the data dirtiest?) -------------------------
SELECT dataset,
       SUM(CASE WHEN severity = 'ERROR'   THEN 1 ELSE 0 END) AS errors,
       SUM(CASE WHEN severity = 'WARNING' THEN 1 ELSE 0 END) AS warnings
FROM qa_results
GROUP BY dataset
ORDER BY errors DESC, warnings DESC;

-- 4) Every blocking error, ready to triage -----------------------------------
SELECT dataset, check_id, record_id, field, detail
FROM qa_results
WHERE severity = 'ERROR'
ORDER BY dataset, check_id;

-- 5) Cross-check in the live tables: facilities missing coordinates ----------
SELECT facility_id, name, town
FROM facilities
WHERE latitude IS NULL OR longitude IS NULL;

-- 6) Cross-check: incidents with impossible coordinates ----------------------
--    (NH longitude must be negative; latitude must be ~42-44)
SELECT incident_id, town, latitude, longitude
FROM incidents
WHERE longitude > 0
   OR latitude  NOT BETWEEN 42.0 AND 44.0
   OR latitude IS NULL OR longitude IS NULL;

-- 7) Duplicate facility primary keys -----------------------------------------
SELECT facility_id, COUNT(*) AS n
FROM facilities
GROUP BY facility_id
HAVING COUNT(*) > 1;

-- 8) Referential check: incident towns not present in the towns table --------
SELECT DISTINCT i.town
FROM incidents i
LEFT JOIN towns t ON i.town = t.town_name
WHERE t.town_name IS NULL;
