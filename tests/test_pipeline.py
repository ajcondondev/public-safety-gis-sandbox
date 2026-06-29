"""
test_pipeline.py — automated tests for the Public Safety GIS pipeline.

GIS Solutions Engineer mapping:
  * Engineering rigor / QA — automated tests prove the geometry math and the
    data-quality checks are correct, so the pipeline can be changed safely.
    This is the difference between a script that "ran once" and a maintainable
    system a government team could rely on.

Run (no extra dependencies needed):
    python -m unittest discover -s tests -v
or:
    python tests/test_pipeline.py
"""

import importlib.util
import os
import sys
import unittest

# Make scripts/ importable.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import common  # noqa: E402


def _load_module(filename, modname):
    """Import a script whose filename starts with a digit (not a valid identifier)."""
    spec = importlib.util.spec_from_file_location(modname, os.path.join(SCRIPTS, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestHaversine(unittest.TestCase):
    def test_zero_distance(self):
        self.assertAlmostEqual(common.haversine_miles(43.2, -71.5, 43.2, -71.5), 0.0, places=6)

    def test_known_distance_concord_manchester(self):
        # Concord (43.2081,-71.5376) to Manchester (42.9956,-71.4548) ~ 15-16 mi.
        d = common.haversine_miles(43.2081, -71.5376, 42.9956, -71.4548)
        self.assertTrue(14 < d < 18, f"expected ~15 mi, got {d:.2f}")

    def test_symmetric(self):
        a = common.haversine_miles(43.0, -71.4, 43.1, -71.5)
        b = common.haversine_miles(43.1, -71.5, 43.0, -71.4)
        self.assertAlmostEqual(a, b, places=9)


class TestPointInPolygon(unittest.TestCase):
    def setUp(self):
        # A square from (-71.56,43.18) to (-71.52,43.235).
        self.feature = {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-71.56, 43.18], [-71.52, 43.18],
                                 [-71.52, 43.235], [-71.56, 43.235], [-71.56, 43.18]]],
            }
        }

    def test_inside(self):
        self.assertTrue(common.point_in_polygon_feature(43.20, -71.54, self.feature))

    def test_outside(self):
        self.assertFalse(common.point_in_polygon_feature(43.00, -71.45, self.feature))

    def test_multipolygon(self):
        mp = {"geometry": {"type": "MultiPolygon",
              "coordinates": [self.feature["geometry"]["coordinates"]]}}
        self.assertTrue(common.point_in_polygon_feature(43.20, -71.54, mp))


class TestGeoJSON(unittest.TestCase):
    def test_points_to_geojson_skips_bad_coords(self):
        rows = [
            {"id": "A", "latitude": 43.2, "longitude": -71.5, "name": "ok"},
            {"id": "B", "latitude": None, "longitude": -71.5, "name": "missing lat"},
            {"id": "C", "latitude": "nope", "longitude": -71.5, "name": "bad lat"},
        ]
        gj, skipped = common.points_to_geojson(rows)
        self.assertEqual(len(gj["features"]), 1)
        self.assertEqual(skipped, 2)
        feat = gj["features"][0]
        self.assertEqual(feat["geometry"]["coordinates"], [-71.5, 43.2])  # [lon, lat] order
        self.assertEqual(feat["properties"]["id"], "A")
        self.assertNotIn("latitude", feat["properties"])  # coords moved to geometry


class TestValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = _load_module("03_validate_gis_data.py", "validate_mod")
        cls.cfg = common.load_config()

    def _run(self, fname, rows):
        import pandas as pd
        return self.v.validate_dataset(fname, pd.DataFrame(rows), self.cfg)

    def test_missing_required_field(self):
        rows = [{"facility_id": "F1", "name": "", "facility_type": "Fire Station",
                 "town": "Concord", "latitude": 43.2, "longitude": -71.5}]
        issues = self._run("emergency_facilities.csv", rows)
        self.assertTrue(any(i["check_id"] == "CHK-01" for i in issues))

    def test_duplicate_pk(self):
        rows = [{"facility_id": "F1", "name": "A", "facility_type": "Fire Station",
                 "town": "Concord", "latitude": 43.2, "longitude": -71.5},
                {"facility_id": "F1", "name": "B", "facility_type": "Fire Station",
                 "town": "Concord", "latitude": 43.2, "longitude": -71.5}]
        issues = self._run("emergency_facilities.csv", rows)
        self.assertTrue(any(i["check_id"] == "CHK-03" for i in issues))

    def test_out_of_range_coordinate(self):
        rows = [{"incident_id": "I1", "incident_type": "Flooding", "severity": "High",
                 "town": "Concord", "latitude": 99.9, "longitude": -71.5}]
        issues = self._run("incidents.csv", rows)
        self.assertTrue(any(i["check_id"] == "CHK-04" for i in issues))

    def test_missing_coordinate(self):
        rows = [{"incident_id": "I1", "incident_type": "Flooding", "severity": "High",
                 "town": "Concord", "latitude": None, "longitude": -71.5}]
        issues = self._run("incidents.csv", rows)
        self.assertTrue(any(i["check_id"] == "CHK-02" for i in issues))

    def test_clean_record_passes(self):
        rows = [{"incident_id": "I1", "incident_type": "Flooding", "severity": "High",
                 "town": "Concord", "latitude": 43.2, "longitude": -71.5,
                 "status": "Open"}]
        issues = self._run("incidents.csv", rows)
        self.assertEqual(len(issues), 0, f"expected no issues, got {issues}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
