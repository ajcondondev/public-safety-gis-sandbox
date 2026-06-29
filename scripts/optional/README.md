# Optional scripts

These scripts are **not** part of the core pipeline (`scripts/01`–`09`). The core
pipeline runs with no internet and no Esri software, on `pandas` + `PyYAML` only.
These optional extras demonstrate two real-world capabilities for the GIS
Solutions Engineer role that the safe, simulated core can't show directly.

| Script | What it demonstrates | Requirements |
|---|---|---|
| `fetch_nws_alerts.py` | **Authoritative public-data ETL** — pulls live National Weather Service active alerts for NH from `api.weather.gov` (no API key) and maps them into the project's hazard-zone schema, with graceful offline fallback and recorded data lineage. | Internet access (standard library only) |
| `arcpy_publish_mapbook.py` | **Esri / ArcPy automation** — imports the pipeline's GeoJSON into a geodatabase, applies symbology, and exports a multi-layout PDF mapbook. | ArcGIS Pro (ships `arcpy`; not pip-installable) |

## Notes

- `fetch_nws_alerts.py` writes to `data/raw/nws_hazard_zones.geojson`. That path
  is **git-ignored** (it's live, changing, real data), so it is never committed.
  It also never overwrites the simulated demo data.
- This is **real** public data, not simulated. Review it before combining it with
  the simulated demo layers; the README disclaimer about operational use still
  applies to anything derived here.
- `arcpy_publish_mapbook.py` is a portfolio artifact and starting point — adapt
  the paths to a real `.aprx`. It is safe to read on any machine; it only does
  work when `arcpy` is importable.

```bash
# Live ETL (needs internet):
python scripts/optional/fetch_nws_alerts.py

# ArcPy mapbook (only inside the ArcGIS Pro Python environment):
propy scripts/optional/arcpy_publish_mapbook.py --aprx C:/path/to/PublicSafety.aprx
```
