# ArcGIS Pro & ArcGIS Online Workflow

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

This guide describes the **manual** Esri workflow that complements the automated
Python pipeline. You do **not** need ArcGIS installed to complete the project —
the pipeline already produces map-ready GeoJSON and tables. These steps show
what a GIS Solutions Engineer would do in ArcGIS Pro / ArcGIS Online with the
generated outputs, and include optional **ArcPy** automation.

---

## Part A — ArcGIS Pro (desktop map production)

### A1. Start the project & import data

1. Create a new **ArcGIS Pro** project (`Map` template).
2. **Map → Add Data**, browse to `outputs/geojson/`, and add:
   - `municipalities.geojson`
   - `emergency_facilities.geojson`
   - `shelters.geojson`
   - `hospitals.geojson`
   - `incidents_analyzed.geojson`
   - `simulated_hazard_zones.geojson`
   *(ArcGIS Pro reads GeoJSON directly; or use the JSON→Features GP tool.)*
3. To use the tabular CSVs, **Add Data → XY Table To Point** (X = `longitude`,
   Y = `latitude`, CRS = WGS84).

### A2. Set coordinate systems

- The GeoJSON is **WGS84 (EPSG:4326)**.
- For accurate distance/area work, set the **Map's** coordinate system to
  **NAD 1983 StatePlane New Hampshire FIPS 2800 (US Feet)** — EPSG:3437. ArcGIS
  projects layers on the fly; project permanently with **Project** (GP tool) if
  you will do measurement-heavy analysis.

### A3. Symbology

| Layer | Symbology | Notes |
|---|---|---|
| `municipalities` | Polygon, hollow fill, gray outline; label `town_name` | Reference frame |
| `simulated_hazard_zones` | Polygon, 35% transparent, color by `severity` (yellow→red) | Draw beneath points |
| `emergency_facilities` | Unique values on `facility_type`; distinct icons (fire/police/EMS/EOC/PW) | Use Esri Emergency symbols |
| `shelters` | Unique values on `status` (Open=green, Standby=amber, Closed=gray) | Size by `capacity` (graduated) |
| `hospitals` | Single H symbol; label `name` | Larger marker |
| `incidents_analyzed` | Graduated/unique on `priority_category` (P1 red → P4 gray) | Size by `priority_score` |

### A4. Suggested mapbook layouts

Build five **Layouts**, then combine via a **Map Series** for a PDF mapbook:

1. **Regional Overview** — towns, roads, all asset types; orientation map.
2. **Emergency Facilities & Shelters** — facilities by type + shelters by status with capacity labels.
3. **Hazard Exposure** — hazard zones + facilities/incidents that fall inside them.
4. **Incident Priority** — `incidents_analyzed` symbolized by priority category.
5. **Town Readiness Summary** — choropleth of towns by `incident_count` (join `town_readiness_summary.csv`), with a summary table element.

Each layout: add **title, legend, north arrow, scale bar, date, data-source
note, and the portfolio disclaimer** as a text element.

### A5. (Optional) ArcPy automation

If ArcGIS Pro is available, automate the import + export of the mapbook. This is
a **placeholder** showing the approach — it runs only inside the ArcGIS Pro
Python environment (`arcpy` is not pip-installable).

```python
# OPTIONAL — runs only with an ArcGIS Pro license (arcpy available).
# Demonstrates the automation a GIS Solutions Engineer would write to remove
# repetitive map production. Pseudocode-level; adapt paths to your project.
import arcpy, os

GEOJSON_DIR = r"outputs/geojson"
PROJECT = r"C:/path/to/PublicSafety.aprx"

aprx = arcpy.mp.ArcGISProject(PROJECT)
m = aprx.listMaps("Map")[0]

# Import each GeoJSON as a feature class into the project geodatabase.
for fname in os.listdir(GEOJSON_DIR):
    if fname.endswith(".geojson"):
        out_fc = os.path.join(aprx.defaultGeodatabase,
                              os.path.splitext(fname)[0])
        arcpy.conversion.JSONToFeatures(os.path.join(GEOJSON_DIR, fname), out_fc)
        m.addDataFromPath(out_fc)

# Export every layout to a single PDF mapbook.
pdf = arcpy.mp.PDFDocumentCreate(r"outputs/maps/emergency_mapbook.pdf")
for layout in aprx.listLayouts():
    layout.exportToPDF(r"outputs/maps/_tmp.pdf")
    pdf.appendPages(r"outputs/maps/_tmp.pdf")
pdf.saveAndClose()
aprx.save()
```

Equivalent open-source analysis already performed by `scripts/04`:
**Near/Generate Near Table** ≈ haversine proximity; **Select By Location /
buffer overlay** ≈ point-in-polygon hazard exposure.

---

## Part B — ArcGIS Online (web GIS)

### B1. Publish hosted feature layers

1. Sign in to **ArcGIS Online** (or ArcGIS Enterprise).
2. **Content → New item → Your device**, upload each `outputs/geojson/*.geojson`,
   and **Publish** as a hosted feature layer. (Alternatively publish directly
   from ArcGIS Pro: **Share → Web Layer**.)
3. Set item **metadata**: title, summary, the data-source note, and the
   portfolio disclaimer; set sharing appropriately (keep simulated data clearly
   labeled).

### B2. Configure a web map

1. **Map Viewer → Add layers** (the hosted layers above).
2. Apply the same symbology as Part A (style by `priority_category`,
   `facility_type`, shelter `status`).
3. Configure **popups** per layer (see Arcade examples below).
4. Set visibility ranges and save the web map.

### B3. Popups & Arcade

Configure each layer's popup, using **Arcade** for derived display values.
See [`docs/arcade_examples.md`](arcade_examples.md) for ready-to-paste
expressions (incident severity color, status label, priority category).

### B4. Operational dashboard

Build an **ArcGIS Dashboard** on the web map. Recommended indicators and the
full layout are in [`docs/dashboard_design.md`](dashboard_design.md):
total incidents, open high-severity, shelters by status, facilities by type,
incidents by town, facilities near hazard zones.

### B5. Field reporting → dashboard

Stand up a **Survey123** form (shelter status / road closure) whose hosted
layer feeds the same web map and dashboard for near-real-time updates. See
[`docs/survey123_design.md`](survey123_design.md).

### B6. (Optional) ArcGIS API for Python

The ArcGIS API for Python (`arcgis`, conda-installable) can automate publishing:

```python
# OPTIONAL — requires the ArcGIS API for Python and an AGOL/Enterprise login.
from arcgis.gis import GIS
gis = GIS("home")  # or GIS(url, username, password)
for path in ["outputs/geojson/incidents_analyzed.geojson",
             "outputs/geojson/emergency_facilities.geojson"]:
    item = gis.content.add({"type": "GeoJson", "title": path.split("/")[-1]},
                           data=path)
    item.publish()
```
