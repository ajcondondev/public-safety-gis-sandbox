"""
09_generate_metadata.py
=======================
Generate FGDC/ISO-style metadata for every published layer: a Markdown metadata
sheet per layer plus a combined machine-readable metadata.json.

GIS Solutions Engineer mapping:
  * Metadata & standards compliance — the posting calls out "compliance with
    state and federal standards" and metadata explicitly. Authoritative GIS data
    is not publishable without metadata describing its lineage, accuracy, extent,
    CRS, attributes, and use constraints. This script produces exactly that.
  * Data lineage — records the processing chain (source -> clean -> validate ->
    analyze) and the data-quality result for each layer.

Run:  python scripts/09_generate_metadata.py   (after scripts 02-05)
"""

from __future__ import annotations

import json
import os

import pandas as pd

from common import load_config, ensure_dirs, log, repo_path, read_geojson, now_iso

# Per-layer descriptive metadata (the human-authored part of a metadata record).
LAYER_INFO = {
    "municipalities": {
        "title": "Corridor Municipalities (Towns)",
        "geojson": "municipalities.geojson",
        "abstract": "Reference boundaries/centroids for the ten municipalities in the Concord–Manchester corridor.",
        "purpose": "Spatial backbone used to aggregate incidents, facilities, and shelters by town.",
        "theme": ["boundaries", "administrative units"],
    },
    "emergency_facilities": {
        "title": "Emergency Response Facilities",
        "geojson": "emergency_facilities.geojson",
        "abstract": "Fire, police, EMS, emergency operations center, and public-works facilities (simulated).",
        "purpose": "Locate response assets and compute incident-to-facility proximity and coverage.",
        "theme": ["structure", "emergency response", "critical infrastructure"],
    },
    "shelters": {
        "title": "Emergency Shelters",
        "geojson": "shelters.geojson",
        "abstract": "Emergency shelters with status, capacity, pet-friendliness, and backup power (simulated).",
        "purpose": "Track shelter availability and capacity for mass-care planning.",
        "theme": ["structure", "emergency management"],
    },
    "hospitals": {
        "title": "Hospitals / Acute-Care Sites",
        "geojson": "hospitals.geojson",
        "abstract": "Hospitals with trauma level and bed counts (simulated; names echo public facilities).",
        "purpose": "Locate definitive medical care for response planning.",
        "theme": ["structure", "health"],
    },
    "incidents_analyzed": {
        "title": "Analyzed Incidents (priority + proximity + hazard)",
        "geojson": "incidents_analyzed.geojson",
        "abstract": "Simulated incident feed enriched with nearest-facility distance, hazard exposure, and a priority score/category.",
        "purpose": "Situational awareness and resource prioritization.",
        "theme": ["emergency response", "events"],
    },
    "simulated_hazard_zones": {
        "title": "Simulated Hazard Zones",
        "geojson": "simulated_hazard_zones.geojson",
        "abstract": "Illustrative floodplain and severe-weather polygons (simulated; NOT from FEMA/NWS).",
        "purpose": "Demonstrate hazard-exposure overlay analysis.",
        "theme": ["environment", "hazards"],
    },
}

USE_CONSTRAINTS = ("Portfolio demonstration using public or simulated data. Not an "
                   "official emergency management product; not for operational "
                   "decision-making. Distances are straight-line approximations. "
                   "Hazard zones are illustrative and not derived from any official source.")


def bbox_of(geojson: dict):
    """Compute [minx, miny, maxx, maxy] over all coordinates in a FeatureCollection."""
    xs, ys = [], []

    def walk(coords):
        if isinstance(coords, (list, tuple)):
            if coords and isinstance(coords[0], (int, float)):
                xs.append(coords[0]); ys.append(coords[1])
            else:
                for c in coords:
                    walk(c)

    for f in geojson["features"]:
        walk(f["geometry"]["coordinates"])
    if not xs:
        return None
    return [round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5)]


def field_list(geojson: dict):
    """Collect the union of property field names from the features."""
    fields = []
    for f in geojson["features"]:
        for k in f["properties"].keys():
            if k not in fields:
                fields.append(k)
    return fields


def main():
    cfg = load_config()
    ensure_dirs(cfg)
    meta_dir = repo_path(cfg["paths"]["outputs"], "metadata")
    os.makedirs(meta_dir, exist_ok=True)

    # QA results give a per-dataset data-quality statement (lineage/accuracy).
    qa = pd.read_csv(repo_path(cfg["paths"]["dashboard_tables"], "qa_results.csv"))
    qa_by_source = {
        "emergency_facilities": "emergency_facilities.csv",
        "incidents_analyzed": "incidents.csv",
        "shelters": "shelters.csv",
        "hospitals": "hospitals.csv",
        "municipalities": "municipalities.csv",
    }

    combined = {
        "metadata_standard": "FGDC-CSDGM / ISO 19115 (simplified, portfolio demo)",
        "generated": now_iso(seconds=True),
        "spatial_reference": cfg["project"]["crs"],
        "use_constraints": USE_CONSTRAINTS,
        "layers": {},
    }

    for key, info in LAYER_INFO.items():
        gj = read_geojson(repo_path(cfg["paths"]["geojson"], info["geojson"]))
        bbox = bbox_of(gj)
        fields = field_list(gj)
        feat_n = len(gj["features"])

        # Data-quality statement for this layer.
        src = qa_by_source.get(key)
        if src is not None:
            errs = int(((qa["dataset"] == src) & (qa["severity"] == "ERROR")).sum())
            warns = int(((qa["dataset"] == src) & (qa["severity"] == "WARNING")).sum())
            dq = f"{errs} error(s), {warns} warning(s) on the source ({src}) at last validation."
        else:
            dq = "Derived/illustrative layer; not independently validated."

        record = {
            "title": info["title"],
            "abstract": info["abstract"],
            "purpose": info["purpose"],
            "theme_keywords": info["theme"],
            "place_keywords": ["New Hampshire", "Concord", "Manchester", "Merrimack County",
                               "Hillsborough County", "Rockingham County"],
            "spatial_reference": cfg["project"]["crs"],
            "bounding_box": bbox,
            "feature_count": feat_n,
            "geometry_type": gj["features"][0]["geometry"]["type"] if feat_n else "n/a",
            "attributes": fields,
            "lineage": [
                "Source: data/raw (authoritative) or data/simulated (demo) — see data_sources.md",
                "Standardized & cleaned: scripts/02_load_clean_data.py",
                "Validated (QA/QC): scripts/03_validate_gis_data.py",
                "Analysis (proximity/hazard/priority): scripts/04_generate_analysis_layers.py"
                if key in ("incidents_analyzed",) else
                "No analytical transformation beyond cleaning.",
            ],
            "data_quality": dq,
            "distribution_format": "GeoJSON (EPSG:4326)",
            "update_frequency": "On pipeline run (manual / scheduled).",
            "use_constraints": USE_CONSTRAINTS,
            "contact": "Portfolio author (demonstration project).",
        }
        combined["layers"][key] = record

        # Write a per-layer Markdown metadata sheet.
        md = [f"# Metadata — {record['title']}", "",
              f"> **{USE_CONSTRAINTS}**", "",
              f"- **Abstract:** {record['abstract']}",
              f"- **Purpose:** {record['purpose']}",
              f"- **Theme keywords:** {', '.join(record['theme_keywords'])}",
              f"- **Place keywords:** {', '.join(record['place_keywords'])}",
              f"- **Spatial reference:** {record['spatial_reference']}",
              f"- **Bounding box [minx, miny, maxx, maxy]:** {record['bounding_box']}",
              f"- **Geometry type:** {record['geometry_type']}",
              f"- **Feature count:** {record['feature_count']}",
              f"- **Distribution format:** {record['distribution_format']}",
              f"- **Update frequency:** {record['update_frequency']}",
              f"- **Data quality:** {record['data_quality']}",
              f"- **Contact:** {record['contact']}", "",
              "## Attributes", "",
              "| Field |", "|---|"]
        md += [f"| {f} |" for f in record["attributes"]]
        md += ["", "## Lineage", ""]
        md += [f"{i+1}. {step}" for i, step in enumerate(record["lineage"])]
        md_path = os.path.join(meta_dir, f"{key}.md")
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(md))
        log(f"Wrote metadata {key:24s} features={feat_n:4d} bbox={bbox}")

    # Combined machine-readable record.
    json_path = os.path.join(meta_dir, "metadata.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(combined, fh, indent=2)
    log(f"Wrote combined metadata -> {os.path.relpath(json_path, repo_path())}")
    log("Metadata complete.")


if __name__ == "__main__":
    main()
