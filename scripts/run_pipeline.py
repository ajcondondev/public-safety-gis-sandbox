"""
run_pipeline.py — run the entire pipeline end-to-end with one command.

GIS Solutions Engineer mapping:
  * Automation / orchestration — a single, repeatable entry point that runs every
    stage in order, times it, and fails fast with a clear summary. This is what
    you would hand to a scheduler (Task Scheduler / cron) for unattended runs.

Usage:
    python scripts/run_pipeline.py            # run stages 01-09
    python scripts/run_pipeline.py --tests    # also run the test suite first
    python scripts/run_pipeline.py --quick    # data + analysis only (skip maps/dashboard/metadata)
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")

STAGES = [
    ("01", "01_create_project_structure.py", "generate simulated data"),
    ("02", "02_load_clean_data.py", "clean & standardize -> GeoJSON"),
    ("03", "03_validate_gis_data.py", "QA/QC validation"),
    ("04", "04_generate_analysis_layers.py", "proximity / hazard / priority"),
    ("05", "05_export_dashboard_tables.py", "dashboard tables + SQLite"),
    ("06", "06_generate_summary_report.py", "summary report"),
    ("07", "07_generate_maps.py", "interactive + static maps"),
    ("08", "08_build_dashboard.py", "HTML operational dashboard"),
    ("09", "09_generate_metadata.py", "layer metadata"),
]
QUICK = {"01", "02", "03", "04", "05", "06"}


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def main():
    args = set(sys.argv[1:])
    quick = "--quick" in args
    stages = [s for s in STAGES if (s[0] in QUICK or not quick)]

    print("=" * 70)
    print(" Public-Safety GIS Sandbox (Concord–Manchester, NH) — pipeline run")
    print("=" * 70)

    if "--tests" in args:
        print("\n[tests] running unittest suite ...")
        t = run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
        sys.stdout.write(t.stdout)
        sys.stderr.write(t.stderr)
        if t.returncode != 0:
            print("\nTESTS FAILED — aborting pipeline.")
            return 1
        print("[tests] passed.\n")

    results = []
    total0 = time.perf_counter()
    for num, fname, desc in stages:
        print(f"[{num}] {desc} ...", flush=True)
        t0 = time.perf_counter()
        proc = run([sys.executable, os.path.join(SCRIPTS, fname)])
        dt = time.perf_counter() - t0
        ok = proc.returncode == 0
        results.append((num, desc, ok, dt))
        if not ok:
            print(proc.stdout)
            print(proc.stderr)
            print(f"\nSTAGE {num} FAILED after {dt:.1f}s — aborting.")
            return 1
        # Show the final log line from each stage as a progress cue.
        last = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
        if last:
            print("     " + last[-1])

    total = time.perf_counter() - total0
    print("\n" + "=" * 70)
    print(" Summary")
    print("=" * 70)
    for num, desc, ok, dt in results:
        print(f"  [{num}] {'OK ' if ok else 'FAIL'}  {dt:5.1f}s  {desc}")
    print(f"  Total: {total:.1f}s")
    print("\nArtifacts:")
    print("  outputs/index.html                  (START HERE — links everything)")
    print("  outputs/maps/interactive_map.html   (open in a browser)")
    print("  outputs/dashboard/index.html        (open in a browser)")
    print("  outputs/reports/                    (qa_qc_report.md, summary_report.md)")
    print("  outputs/public_safety_gis.sqlite    (query with sql/*.sql)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
