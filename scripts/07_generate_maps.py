"""
07_generate_maps.py
===================
Produce VIEWABLE map deliverables from the GeoJSON layers:
  1. An interactive, self-contained Leaflet web map (outputs/maps/interactive_map.html)
     that opens in any browser with NO dependencies and NO server (data is
     embedded inline, so it works straight off the file system).
  2. Static PNG maps via matplotlib (regional overview + incident priority),
     ideal for portfolio screenshots, the StoryMap, and the mapbook.

GIS Solutions Engineer mapping:
  * Map production / cartography — symbolized, labeled, legibly composed maps,
    the most visible product of the role.
  * Web GIS — an interactive web map is what gets published to ArcGIS Online;
    this is the open-source equivalent a hiring manager can click immediately.
  * Open-source first — Leaflet (via CDN) + matplotlib; degrades gracefully to
    an SVG fallback if matplotlib is unavailable.

Run:  python scripts/07_generate_maps.py   (after scripts 02 & 04)
"""

from __future__ import annotations

import json
import os

from common import load_config, ensure_dirs, log, repo_path, read_geojson

# Symbology shared by both the web map and the static maps -------------------
PRIORITY_COLORS = {
    "P1 - Immediate": "#b30000", "P2 - Urgent": "#e34a33",
    "P3 - Routine": "#fdae61", "P4 - Monitor": "#9aa0a6",
}
FACILITY_COLORS = {
    "Fire Station": "#d7301f", "Police Station": "#2166ac",
    "EMS Station": "#1a9850", "Emergency Operations Center": "#762a83",
    "Public Works Garage": "#8c6d31",
}
SHELTER_COLORS = {"Open": "#1a9850", "Standby": "#f0a30a", "Closed": "#9aa0a6"}
DISCLAIMER = ("Portfolio demonstration using public or simulated data — "
              "not an official emergency management product.")


# =============================================================================
# 1) Interactive Leaflet map (self-contained HTML)
# =============================================================================
def build_leaflet_html(layers: dict) -> str:
    """Assemble a standalone Leaflet HTML page with inline GeoJSON data."""
    # Embed each layer's GeoJSON as a JS variable (avoids file:// fetch/CORS).
    data_js = "\n".join(
        f"const {name}_data = {json.dumps(gj)};" for name, gj in layers.items())

    # Plain (non-f) template so JS/CSS braces need no escaping; %s-style inject.
    template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Concord-Manchester Public Safety GIS — Interactive Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body { margin: 0; height: 100%; font-family: Segoe UI, Arial, sans-serif; }
  #map { height: 100vh; }
  .banner { position: absolute; z-index: 1000; top: 8px; left: 50px; right: 8px;
            background: rgba(255,255,255,0.92); padding: 6px 12px; border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-size: 13px; }
  .banner b { color: #b30000; }
  .legend { line-height: 1.5em; color: #333; }
  .legend i { width: 12px; height: 12px; display: inline-block; margin-right: 6px;
              border-radius: 50%; vertical-align: middle; }
  .legend h4 { margin: 4px 0; }
</style>
</head>
<body>
<div class="banner"><b>DEMO:</b> __DISCLAIMER__</div>
<div id="map"></div>
<script>
__DATA__

const map = L.map('map').setView([43.10, -71.49], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }).addTo(map);

const priorityColors = __PRIORITY__;
const facilityColors = __FACILITY__;
const shelterColors = __SHELTER__;

function popup(props) {
  return Object.keys(props).map(k => '<b>' + k + ':</b> ' + props[k]).join('<br>');
}
function circle(color, r) {
  return { radius: r, fillColor: color, color: '#222', weight: 1,
           opacity: 1, fillOpacity: 0.85 };
}

// Hazard zones (polygons, drawn beneath points)
const hazards = L.geoJSON(simulated_hazard_zones_data, {
  style: { color: '#cc4c02', weight: 1, fillColor: '#fe9929', fillOpacity: 0.25 },
  onEachFeature: (f, l) => l.bindPopup(popup(f.properties))
}).addTo(map);

// Incidents, colored by priority
const incidents = L.geoJSON(incidents_analyzed_data, {
  pointToLayer: (f, latlng) => L.circleMarker(latlng,
    circle(priorityColors[f.properties.priority_category] || '#888', 5)),
  onEachFeature: (f, l) => l.bindPopup(popup(f.properties))
}).addTo(map);

// Emergency facilities, colored by type
const facilities = L.geoJSON(emergency_facilities_data, {
  pointToLayer: (f, latlng) => L.circleMarker(latlng,
    circle(facilityColors[f.properties.facility_type] || '#555', 6)),
  onEachFeature: (f, l) => l.bindPopup(popup(f.properties))
}).addTo(map);

// Shelters, colored by status
const shelters = L.geoJSON(shelters_data, {
  pointToLayer: (f, latlng) => L.circleMarker(latlng,
    circle(shelterColors[f.properties.status] || '#555', 6)),
  onEachFeature: (f, l) => l.bindPopup(popup(f.properties))
}).addTo(map);

// Hospitals
const hospitals = L.geoJSON(hospitals_data, {
  pointToLayer: (f, latlng) => L.marker(latlng),
  onEachFeature: (f, l) => l.bindPopup(popup(f.properties))
}).addTo(map);

L.control.layers(null, {
  'Hazard zones': hazards,
  'Incidents (by priority)': incidents,
  'Emergency facilities': facilities,
  'Shelters': shelters,
  'Hospitals': hospitals
}, { collapsed: false }).addTo(map);

const legend = L.control({ position: 'bottomright' });
legend.onAdd = function () {
  const div = L.DomUtil.create('div', 'banner legend');
  let html = '<h4>Incident priority</h4>';
  for (const k in priorityColors)
    html += '<i style="background:' + priorityColors[k] + '"></i>' + k + '<br>';
  html += '<h4>Facility type</h4>';
  for (const k in facilityColors)
    html += '<i style="background:' + facilityColors[k] + '"></i>' + k + '<br>';
  div.innerHTML = html;
  return div;
};
legend.addTo(map);
</script>
</body>
</html>
"""
    return (template
            .replace("__DISCLAIMER__", DISCLAIMER)
            .replace("__DATA__", data_js)
            .replace("__PRIORITY__", json.dumps(PRIORITY_COLORS))
            .replace("__FACILITY__", json.dumps(FACILITY_COLORS))
            .replace("__SHELTER__", json.dumps(SHELTER_COLORS)))


# =============================================================================
# 2) Static PNG maps (matplotlib) with SVG fallback
# =============================================================================
def _points(gj):
    """Yield (lon, lat, properties) for point features."""
    for f in gj["features"]:
        if f["geometry"]["type"] == "Point":
            lon, lat = f["geometry"]["coordinates"]
            yield lon, lat, f["properties"]


def render_static_maps(cfg, layers):
    try:
        import matplotlib
        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MplPolygon
        from matplotlib.lines import Line2D
    except Exception:
        log("matplotlib not available — writing a simple SVG overview fallback.")
        _render_svg_fallback(cfg, layers)
        return

    maps_dir = cfg["paths"]["maps"]

    def draw_hazards(ax):
        for f in layers["simulated_hazard_zones"]["features"]:
            for ring in f["geometry"]["coordinates"]:
                ax.add_patch(MplPolygon(ring, closed=True, facecolor="#fe9929",
                                        edgecolor="#cc4c02", alpha=0.25, zorder=1))

    def label_towns(ax):
        for lon, lat, p in _points(layers["municipalities"]):
            ax.annotate(p.get("town_name", ""), (lon, lat), fontsize=7,
                        color="#333", ha="center", zorder=5)

    # --- Map 1: regional overview -------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 11))
    draw_hazards(ax)
    label_towns(ax)
    for lon, lat, p in _points(layers["emergency_facilities"]):
        ax.scatter(lon, lat, c=FACILITY_COLORS.get(p.get("facility_type"), "#555"),
                   s=28, edgecolors="k", linewidths=0.4, zorder=4)
    for lon, lat, p in _points(layers["shelters"]):
        ax.scatter(lon, lat, c=SHELTER_COLORS.get(p.get("status"), "#555"),
                   marker="s", s=26, edgecolors="k", linewidths=0.4, zorder=4)
    for lon, lat, p in _points(layers["hospitals"]):
        ax.scatter(lon, lat, c="#762a83", marker="P", s=70,
                   edgecolors="k", linewidths=0.5, zorder=6)
    legend_elems = [Line2D([0], [0], marker='o', color='w', label=k,
                           markerfacecolor=v, markersize=8)
                    for k, v in FACILITY_COLORS.items()]
    legend_elems.append(Line2D([0], [0], marker='P', color='w', label='Hospital',
                               markerfacecolor='#762a83', markersize=10))
    legend_elems.append(Line2D([0], [0], marker='s', color='w', label='Shelter (color=status)',
                               markerfacecolor='#1a9850', markersize=8))
    ax.legend(handles=legend_elems, loc="lower left", fontsize=7, framealpha=0.9)
    ax.set_title("Concord–Manchester Corridor — Emergency Response Assets\n"
                 "(simulated data — portfolio demonstration)", fontsize=11)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.figure.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=7, color="#b30000")
    ax.set_aspect(1.35)
    fig.savefig(repo_path(maps_dir, "regional_overview.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
    log("Wrote outputs/maps/regional_overview.png")

    # --- Map 2: incident priority -------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 11))
    draw_hazards(ax)
    label_towns(ax)
    for lon, lat, p in _points(layers["incidents_analyzed"]):
        cat = p.get("priority_category")
        ax.scatter(lon, lat, c=PRIORITY_COLORS.get(cat, "#888"),
                   s=20 + 8 * int(p.get("priority_score", 1)),
                   edgecolors="k", linewidths=0.3, alpha=0.85, zorder=4)
    legend_elems = [Line2D([0], [0], marker='o', color='w', label=k,
                           markerfacecolor=v, markersize=8)
                    for k, v in PRIORITY_COLORS.items()]
    ax.legend(handles=legend_elems, loc="lower left", title="Priority",
              fontsize=8, framealpha=0.9)
    ax.set_title("Concord–Manchester Corridor — Incident Priority\n"
                 "(simulated data — portfolio demonstration)", fontsize=11)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.figure.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=7, color="#b30000")
    ax.set_aspect(1.35)
    fig.savefig(repo_path(maps_dir, "incident_priority.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
    log("Wrote outputs/maps/incident_priority.png")


def _render_svg_fallback(cfg, layers):
    """Minimal pure-Python SVG overview if matplotlib is missing."""
    pts = list(_points(layers["incidents_analyzed"]))
    if not pts:
        return
    lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(lons), max(lons), min(lats), max(lats)
    W, H = 800, 1000

    def sx(lon): return (lon - minx) / (maxx - minx + 1e-9) * (W - 40) + 20
    def sy(lat): return H - ((lat - miny) / (maxy - miny + 1e-9) * (H - 40) + 20)

    circles = "".join(
        f'<circle cx="{sx(lo):.1f}" cy="{sy(la):.1f}" r="4" '
        f'fill="{PRIORITY_COLORS.get(pr.get("priority_category"), "#888")}" '
        f'stroke="#222" stroke-width="0.4"/>'
        for lo, la, pr in pts)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
           f'<rect width="{W}" height="{H}" fill="#eef"/>'
           f'<text x="10" y="20" font-size="12" fill="#b30000">{DISCLAIMER}</text>'
           f'{circles}</svg>')
    with open(repo_path(cfg["paths"]["maps"], "incident_priority.svg"), "w",
              encoding="utf-8") as fh:
        fh.write(svg)
    log("Wrote outputs/maps/incident_priority.svg (SVG fallback)")


def main():
    cfg = load_config()
    ensure_dirs(cfg)
    gj = cfg["paths"]["geojson"]
    layers = {
        "municipalities": read_geojson(repo_path(gj, "municipalities.geojson")),
        "emergency_facilities": read_geojson(repo_path(gj, "emergency_facilities.geojson")),
        "shelters": read_geojson(repo_path(gj, "shelters.geojson")),
        "hospitals": read_geojson(repo_path(gj, "hospitals.geojson")),
        "incidents_analyzed": read_geojson(repo_path(gj, "incidents_analyzed.geojson")),
        "simulated_hazard_zones": read_geojson(repo_path(gj, "simulated_hazard_zones.geojson")),
    }

    html = build_leaflet_html(layers)
    html_path = repo_path(cfg["paths"]["maps"], "interactive_map.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    log(f"Wrote interactive web map -> {os.path.relpath(html_path, repo_path())}")

    render_static_maps(cfg, layers)
    log("Maps complete. Open outputs/maps/interactive_map.html in a browser.")


if __name__ == "__main__":
    main()
