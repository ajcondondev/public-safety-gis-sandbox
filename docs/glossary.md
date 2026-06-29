# Glossary

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

Plain-English definitions of the GIS, data, and emergency-management terms used
in this project. Where useful, the last column points to where the concept shows
up here. Pair this with the [learning guide](learning_guide.md).

## GIS fundamentals

| Term | Plain-English meaning | In this project |
|---|---|---|
| **GIS** | Geographic Information System — software, data, and methods for storing, mapping, analyzing, and sharing information that has a location. | the whole pipeline |
| **Feature** | A single mapped thing (one hospital, one road, one town) with a location and attributes. | a row / a GeoJSON feature |
| **Layer** | A themed set of features you can show or hide. | each `outputs/geojson/*.geojson` |
| **Attribute** | A single fact about a feature, stored in a column. | CSV columns |
| **Attribute table** | The spreadsheet behind a layer (one row per feature). | `data/processed/*.csv` |
| **Point / line / polygon** | Feature shapes: a site; a long thin thing; a bounded area. | facilities = points; hazard zones = polygons |
| **Coordinate system** | The agreed numbering for describing locations on earth (e.g. latitude/longitude). | WGS84 (EPSG:4326) |
| **Projection** | The math that flattens the round earth onto a flat map; every projection distorts something. | project to NH State Plane (EPSG:3437) for measurement |
| **CRS / EPSG code** | "Coordinate Reference System"; EPSG codes are standard IDs for them (4326 = WGS84). | `config` `crs` |
| **Scale** | The ratio of map distance to real distance; how zoomed in you are. | street vs. corridor-wide maps |
| **Geocoding** | Turning an address into a map location. | the lat/long on each record |
| **Reverse geocoding** | Turning a location back into a nearest address. | (concept; not used here) |

## Spatial analysis

| Term | Plain-English meaning | In this project |
|---|---|---|
| **Spatial analysis** | Using location to answer questions, not just draw a picture. | `scripts/04` |
| **Buffer** | A zone drawn a set distance around a feature (e.g. 5 mi around a station). | proximity rings; hazard buffer (config) |
| **Proximity analysis** | Finding what is nearest to a point. | incident → nearest facility (haversine) |
| **Overlay** | Combining layers to see where they intersect. | incidents/assets vs. hazard zones |
| **Point-in-polygon** | Testing whether a point falls inside an area. | `common.point_in_polygon_feature` |
| **Spatial join** | Attaching data from one layer to another based on location. | town rollups in `scripts/05` |
| **Service area / drive time** | What can be reached within a distance or travel time. | (future work — straight-line used here) |
| **Hazard exposure** | Which people, roads, or assets sit inside a hazard. | `facility_hazard_exposure.csv` |
| **Choropleth** | A map that shades areas by a value (e.g. incidents per town). | town readiness map (ArcGIS workflow) |

## Data management & quality

| Term | Plain-English meaning | In this project |
|---|---|---|
| **ETL** | Extract, Transform, Load — pull data, clean/reshape it, load it where it's used. | `scripts/02` + optional NWS fetch |
| **Data cleaning / standardization** | Fixing names, casing, types, duplicates. | `scripts/02` |
| **Data quality** | How complete, accurate, current, and consistent data is. | `scripts/03`, `docs/qa_qc_plan.md` |
| **QA/QC** | Quality assurance / quality control — the checks that keep data trustworthy. | the 6 checks CHK-01…CHK-06 |
| **Metadata** | Data about the data: source, date, meaning, limits. | `outputs/metadata/` |
| **Data lineage** | The documented history of where data came from and how it changed. | metadata `lineage`, `data_source` fields |
| **Staging vs. production tables** | Load-as-is tables (may contain defects) vs. clean, constraint-enforced tables. | `sql/schema.sql` (staging by design) |
| **Topology** | Rules for how features connect without errors (gaps/overlaps). | (concept; relevant for real road/boundary data) |

## Formats & storage

| Term | Plain-English meaning | In this project |
|---|---|---|
| **GeoJSON** | A text-based, web-friendly format for geographic data. | `outputs/geojson/` |
| **Shapefile** | An older but common geographic file format. | (alternative export in ArcGIS) |
| **Feature class** | A stored collection of one feature type, usually in a geodatabase. | the ArcGIS equivalent of each layer |
| **Geodatabase** | An organized container for GIS data, tables, and rules. | the file/enterprise GDB you'd build in ArcGIS |
| **Enterprise geodatabase / SDE** | GIS data stored in a database (e.g. SQL Server) for multi-user access. | SQLite stands in for this here |

## Esri / web GIS tooling

| Term | Plain-English meaning |
|---|---|
| **ArcGIS Pro** | Desktop GIS for editing, analysis, geoprocessing, and map layouts. |
| **ArcGIS Online** | Esri's cloud platform for web maps, hosted layers, dashboards, and apps. |
| **ArcGIS Enterprise** | The self-hosted organizational version of the ArcGIS platform. |
| **ArcGIS Server** | Backend software that publishes GIS data as services. |
| **Hosted feature layer** | A layer published to ArcGIS Online/Enterprise that apps can query and edit. |
| **REST service** | A way for apps to read GIS data over the web via a URL endpoint. |
| **Map service vs. feature service** | A rendered map image vs. queryable/editable feature data. |
| **ArcPy** | Esri's Python package for automating ArcGIS tasks. |
| **ArcGIS API for Python** | A Python library for managing ArcGIS Online/Enterprise content. |
| **Arcade** | Esri's lightweight expression language for labels, popups, and symbology logic. |
| **Survey123** | Esri's form-based field data-collection tool. |
| **Dashboards** | Live screens combining maps, charts, lists, and counts. |
| **StoryMaps** | Map-based narratives for briefings and the public. |
| **PowerBI** | Microsoft's reporting tool for charts, KPIs, and trends. |

## Emergency-management concepts

| Term | Plain-English meaning |
|---|---|
| **Emergency service zone** | An area defining which agency responds there. |
| **Common operating picture** | A shared, single view of a situation used by the whole team. |
| **Situational awareness** | Understanding the current picture of an event: what, where, what's at risk. |
| **EOC (Emergency Operations Center)** | Where an emergency is coordinated; GIS feeds it its visual picture. |
| **Incident command** | The standard structure for running a large incident; GIS usually supports the planning function. |
| **Four phases** | Preparedness, Mitigation, Response, Recovery — the lifecycle GIS supports. |
| **RERP** | Radiological Emergency Response Plan — specialized map products/layers a state EM team maintains. |
| **Mutual aid** | Agreements where agencies help each other across boundaries; informed by coverage-gap analysis. |
| **After-action review** | Post-event review of what happened and what to improve. |

## Open-source equivalents (used or referenced here)

| Term | Plain-English meaning |
|---|---|
| **pandas** | Python library for tabular data (the project's core dependency). |
| **GeoPandas / Shapely** | Python libraries for spatial data/geometry (optional enhancement here). |
| **QGIS** | Free desktop GIS, an alternative to ArcGIS Pro. |
| **PostGIS** | Spatial extension for the PostgreSQL database. |
| **SQLite** | A lightweight, file-based database (SQL Server stand-in here). |
| **Leaflet** | A JavaScript library for interactive web maps (used by `scripts/07`). |
| **haversine** | A formula for great-circle distance between two lat/long points (used for proximity). |
