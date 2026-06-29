-- =============================================================================
-- summary_queries.sql — analytical / dashboard queries
-- -----------------------------------------------------------------------------
-- Run against outputs/public_safety_gis.sqlite, e.g.:
--   sqlite3 -header -column outputs/public_safety_gis.sqlite ".read sql/summary_queries.sql"
-- These produce the numbers behind the dashboard indicators in
-- docs/dashboard_design.md, computed in SQL (the SQL Server skill) rather than
-- in Python — same answers, different engine.
-- =============================================================================

-- 1) Incident counts by town -------------------------------------------------
SELECT town, COUNT(*) AS incident_count
FROM incidents
GROUP BY town
ORDER BY incident_count DESC;

-- 2) Facility counts by type -------------------------------------------------
SELECT facility_type, COUNT(*) AS facility_count
FROM facilities
GROUP BY facility_type
ORDER BY facility_count DESC;

-- 3) Open high-severity incidents (the "act now" list) -----------------------
SELECT incident_id, incident_type, severity, town, status, reported_at
FROM incidents
WHERE status IN ('Open', 'In Progress')
  AND severity IN ('High', 'Critical')
ORDER BY severity DESC, reported_at;

-- 4) Shelters by status, with available capacity -----------------------------
SELECT status,
       COUNT(*)        AS shelter_count,
       SUM(capacity)   AS total_capacity
FROM shelters
GROUP BY status
ORDER BY status;

-- 5) Town readiness summary (cross-layer rollup) -----------------------------
--    Correlated subqueries avoid the row fan-out you'd get from joining
--    several one-to-many tables at once, so every count is exact.
SELECT t.town_name,
       t.county,
       t.population,
       (SELECT COUNT(*) FROM incidents  i WHERE i.town = t.town_name) AS incident_count,
       (SELECT COUNT(*) FROM incidents  i WHERE i.town = t.town_name
              AND i.status IN ('Open','In Progress')
              AND i.severity IN ('High','Critical'))                  AS open_high_severity,
       (SELECT COUNT(*) FROM facilities f WHERE f.town = t.town_name) AS facility_count,
       (SELECT COUNT(*) FROM shelters   s WHERE s.town = t.town_name) AS shelter_count,
       (SELECT COALESCE(SUM(capacity),0) FROM shelters s WHERE s.town = t.town_name) AS shelter_capacity,
       (SELECT COUNT(*) FROM hospitals  h WHERE h.town = t.town_name) AS hospital_count
FROM towns t
ORDER BY incident_count DESC;

-- 6) High-priority incidents from the analysis layer -------------------------
SELECT priority_category,
       COUNT(*) AS incident_count,
       ROUND(AVG(nearest_facility_miles), 2) AS avg_miles_to_facility
FROM incident_proximity
GROUP BY priority_category
ORDER BY priority_category;

-- 7) Facilities near hazard zones (exposure) ---------------------------------
SELECT asset_class,
       COUNT(*) AS exposed_assets
FROM hazard_exposure
WHERE hazard_exposed = 'Y'
GROUP BY asset_class
ORDER BY exposed_assets DESC;

-- 8) Incidents that are BOTH high priority AND far from a facility -----------
--    (coverage-gap candidates for planning)
SELECT incident_id, town, severity, nearest_facility_miles, priority_category
FROM incident_proximity
WHERE priority_category IN ('P1 - Immediate', 'P2 - Urgent')
  AND nearest_facility_miles > 3.0
ORDER BY nearest_facility_miles DESC;
