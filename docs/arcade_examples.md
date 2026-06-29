# Arcade Expression Examples

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

[Arcade](https://developers.arcgis.com/arcade/) is Esri's lightweight expression
language for popups, labels, and symbology in ArcGIS Online / Pro. These
examples operate on the fields produced by this pipeline. Paste them into a web
map layer's **Popup → Arcade expression** (or label/symbology class).

---

## 1. Incident severity — popup color & emphasis

Returns an HTML-friendly colored label for use in a popup (Arcade popup
expressions can return text used inside a custom popup).

```js
// Field: $feature.severity
var s = Upper($feature.severity);
var color = When(
  s == "CRITICAL", "#b30000",
  s == "HIGH",     "#e34a33",
  s == "MODERATE", "#fdae61",
  s == "LOW",      "#1a9850",
  "#888888"
);
return `<span style="color:${color};font-weight:bold;">${Proper($feature.severity)}</span>`;
```

## 2. Status label — human-friendly text

```js
// Field: $feature.status
return When(
  $feature.status == "Open",        "🟥 Open — needs attention",
  $feature.status == "In Progress", "🟧 In Progress — units assigned",
  $feature.status == "Closed",      "🟩 Closed — resolved",
  "Unknown status"
);
```

## 3. Priority category — derived classification

If you ever need to recompute the priority category client-side (rather than
reading the precomputed `priority_category` field), this mirrors the Python
logic in `scripts/04`:

```js
// Recreate the priority score from raw fields.
var sevW = When(
  $feature.severity == "Critical", 4,
  $feature.severity == "High",     3,
  $feature.severity == "Moderate", 2,
  $feature.severity == "Low",      1, 1);
var openW = IIf(Includes(["Open","In Progress"], $feature.status), 2, 0);
var hazW  = IIf($feature.hazard_exposed == "Y", 2, 0);
var farW  = IIf($feature.nearest_facility_miles > 5, 1, 0);
var score = sevW + openW + hazW + farW;

return When(
  score >= 7, "P1 - Immediate",
  score >= 5, "P2 - Urgent",
  score >= 3, "P3 - Routine",
  "P4 - Monitor"
);
```

## 4. Nearest-facility summary — popup sentence

```js
// Combines analysis fields into a readable sentence for an incident popup.
return `Nearest facility: ${$feature.nearest_facility_name} ` +
       `(${Round($feature.nearest_facility_miles, 1)} mi, ${$feature.proximity_ring}). ` +
       IIf($feature.hazard_exposed == "Y",
           "⚠️ Inside a hazard zone.", "Not in a hazard zone.");
```

## 5. Shelter availability — label expression

```js
// Field: status + capacity. Use as a layer LABEL expression.
return $feature.name + TextFormatting.NewLine +
       $feature.status + " (" + Text($feature.capacity) + " cap)";
```

## 6. Facility operational status — symbology / filter helper

```js
// Returns a simple class used to drive Unique Value symbology or a filter.
return When(
  $feature.operational_status == "Operational",   "Available",
  $feature.operational_status == "Limited",        "Degraded",
  $feature.operational_status == "Out of Service", "Unavailable",
  "Unknown"
);
```

---

### Notes

- Arcade runs **in the map**, so these compute live as data updates (e.g. when a
  Survey123 response changes a shelter's `status`).
- The pipeline already precomputes `priority_category`, `proximity_ring`, and
  `hazard_exposed`, so popups can simply read those fields; example 3 is shown to
  demonstrate the equivalent logic in Arcade for portfolio purposes.
