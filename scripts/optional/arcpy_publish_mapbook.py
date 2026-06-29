"""
arcpy_publish_mapbook.py  (OPTIONAL — ArcGIS Pro / ArcPy automation)
====================================================================
A tangible example of the kind of ArcPy automation a GIS Solutions Engineer
writes to remove repetitive desktop work: import the pipeline's GeoJSON layers
into a geodatabase, apply symbology, and export every layout to a single PDF
mapbook.

IMPORTANT: this script requires ArcGIS Pro. `arcpy` ships ONLY inside the
ArcGIS Pro Python (conda) environment and CANNOT be installed with pip. The
script is intentionally NOT part of the core pipeline (which runs with no Esri
software). It is included as a portfolio artifact and a starting point you would
adapt to a real .aprx project.

The open-source pipeline already performs the equivalent ANALYSIS:
  * scripts/04 proximity   ~= arcpy.analysis.GenerateNearTable
  * scripts/04 hazard test ~= arcpy.analysis.Buffer + arcpy.management.SelectLayerByLocation
  * scripts/07 maps        ~= an ArcGIS Pro layout / map series

Usage (inside the ArcGIS Pro Python environment):
    propy arcpy_publish_mapbook.py  --aprx C:/path/to/PublicSafety.aprx
"""

from __future__ import annotations

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEOJSON_DIR = os.path.join(REPO_ROOT, "outputs", "geojson")
MAPS_DIR = os.path.join(REPO_ROOT, "outputs", "maps")

# Layer -> the field you'd drive Unique Value symbology from (documentation aid).
SYMBOLOGY = {
    "incidents_analyzed": "priority_category",
    "emergency_facilities": "facility_type",
    "shelters": "status",
    "simulated_hazard_zones": "severity",
}


def require_arcpy():
    try:
        import arcpy  # noqa: F401
        return True
    except Exception:
        print("ERROR: `arcpy` is not available. Run this inside the ArcGIS Pro "
              "Python environment (it cannot be pip-installed).")
        print("The core pipeline does NOT need this script — see README.")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an emergency mapbook with ArcPy.")
    parser.add_argument("--aprx", required=True, help="Path to the ArcGIS Pro project (.aprx).")
    parser.add_argument("--out", default=os.path.join(MAPS_DIR, "emergency_mapbook.pdf"),
                        help="Output PDF path.")
    args = parser.parse_args()

    if not require_arcpy():
        return 1

    import arcpy
    arcpy.env.overwriteOutput = True

    aprx = arcpy.mp.ArcGISProject(args.aprx)
    gdb = aprx.defaultGeodatabase
    m = aprx.listMaps()[0]

    # 1) Import each GeoJSON layer into the project geodatabase as a feature class.
    for fname in sorted(os.listdir(GEOJSON_DIR)):
        if not fname.endswith(".geojson"):
            continue
        name = os.path.splitext(fname)[0]
        out_fc = os.path.join(gdb, name)
        print(f"[arcpy] JSONToFeatures {fname} -> {name}")
        arcpy.conversion.JSONToFeatures(os.path.join(GEOJSON_DIR, fname), out_fc)
        m.addDataFromPath(out_fc)
        if name in SYMBOLOGY:
            print(f"        (symbolize {name} by '{SYMBOLOGY[name]}' — apply a "
                  f"Unique Values renderer / .lyrx here)")

    # 2) Export every layout to a combined PDF mapbook.
    out_pdf = args.out
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    pdf = arcpy.mp.PDFDocumentCreate(out_pdf)
    tmp = os.path.join(MAPS_DIR, "_layout_tmp.pdf")
    for layout in aprx.listLayouts():
        print(f"[arcpy] exporting layout: {layout.name}")
        layout.exportToPDF(tmp)
        pdf.appendPages(tmp)
    pdf.saveAndClose()
    if os.path.exists(tmp):
        os.remove(tmp)
    aprx.save()
    print(f"[arcpy] mapbook written -> {out_pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
