# Design Notes & Lessons Learned

> **This is a personal learning / portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

This is the "why" behind the project — the decisions I made while building it, the
trade-offs I hit, and what I took away. I find a project teaches you the most when
you write down *why* it looks the way it does, not just *what* it does. (It's also
a living document — a place to add my own takeaways as I keep learning.)

---

## Why all the data is simulated

The first decision was the most important one: **use only simulated data, and
label it everywhere.** Public-safety data is genuinely sensitive — real 911
records, private resident details, and exact critical-infrastructure locations
can cause privacy or security harm if mishandled. Building the whole project on
clearly-labeled simulated data let me exercise the full workflow without ever
touching anything I shouldn't.

**What it taught me:** the *ethics* of the field are part of the engineering, not
a footnote. Deciding "what is safe to publish vs. keep internal" is a real,
recurring design question in public-safety GIS — so the disclaimer and the
`simulated_flag` aren't decoration, they're practice for a habit the work requires.

## Why open-source first (pandas + standard library)

The core pipeline runs on `pandas` + `PyYAML` only — GeoJSON is written with the
standard-library `json` module, distances use a hand-written haversine function,
and point-in-polygon is a pure-Python ray-casting test. No GeoPandas, no Esri
license required.

**Why:** I wanted anyone (including future me on a fresh machine) to be able to
clone it and run it in seconds, and I wanted to actually understand the geometry
rather than calling a black box.
**What it taught me:** how much of "GIS" is really just careful data handling plus
a few well-understood formulas. Writing haversine and ray-casting myself made
concepts like CRS choice and great-circle distance concrete. The
[architecture doc](architecture.md) maps each open-source piece to its
ArcGIS/enterprise equivalent, which is how I connected the two worlds.

## Why I deliberately broke the data

`scripts/01` injects real defects on purpose — a missing coordinate, a duplicate
ID, a sign-flipped longitude, a blank required field. The validator
(`scripts/03`) is then expected to catch all seven.

**Why:** a QA demo that finds zero problems proves nothing. The interesting part
of data quality is catching the things that are *wrong but plausible*.
**What it taught me:** good validation is specific and honest — every finding has
a check ID, a severity, and a written rule, so the result is defensible rather
than "trust me, it's clean."

## Why the database tables are "staging" (no enforced keys)

The SQLite schema loads data *as-is*, including the duplicate ID, instead of
enforcing primary keys at load time.

**Why:** if the database rejected the duplicate on insert, the SQL QA query that's
supposed to *find* duplicates would have nothing to find. So the loaded tables are
a staging layer; the "production" model (with enforced keys) is documented in
`sql/schema.sql` as the next step.
**What it taught me:** the difference between a *staging* layer (accept everything,
then inspect) and a *trusted* layer (only clean, constrained data) — a pattern
that shows up all over enterprise data work.

## Why straight-line distance (and why that's a limitation)

Proximity uses great-circle distance, not drive time.

**Why:** it needs no road network and no routing engine, so the demo stays
self-contained.
**The honest limit:** in a real response, 3 miles "as the crow flies" can be 8
minutes or 25 depending on roads, rivers, and closures. I called this out in the
README and reports rather than hiding it, because overstating accuracy is exactly
the failure mode public-safety GIS warns against. **What I'd try next:** swap in a
real road network (OSRM, or ArcGIS Network Analyst) for drive-time service areas.

## Why WGS84 for storage but State Plane for analysis

Everything is stored in WGS84 (EPSG:4326) because that's the lingua franca of
GeoJSON and web maps. But the docs note that real measurement work should project
to NH State Plane (EPSG:3437, US feet).

**What it taught me:** there isn't one "right" coordinate system — you pick the one
that fits the job (web display vs. accurate distance/area), and the bugs come from
*mixing* them without realizing it.

## The priority score is a heuristic, on purpose

The incident priority (P1–P4) combines severity, open status, hazard exposure, and
distance with simple weights. It is a **transparent heuristic**, not a validated
model.

**Why I kept it simple:** I wanted the logic to be readable and explainable in one
sentence to a non-technical stakeholder — which matters more here than statistical
sophistication. **What I'd be careful about:** a real prioritization model would
need to be validated against outcomes and reviewed with the people who'd act on it.

## A few things that surprised me

- How much of the job is **communication**: the summary report and stakeholder
  brief took as much thought as the analysis, and they're what a decision-maker
  actually reads.
- How valuable **metadata** is — writing the lineage for each layer forced me to be
  honest about where every number came from.
- How naturally the work splits into **layers** (source → processed → analysis →
  serving → presentation), the same shape as a real enterprise GIS stack.

## What I'm curious to explore next

- Swap a simulated layer for **authoritative NH data** (NH GRANIT boundaries, FEMA
  flood zones, HIFLD facilities) through the existing `data/raw/` hook.
- **Drive-time** service areas instead of straight-line rings.
- Publish the layers to **ArcGIS Online** and build the real dashboard / StoryMap
  the docs describe.
- A **scheduled** run that refreshes the live NWS feed and re-builds the outputs.
- Promote the SQLite staging model to a real **SQL Server** geodatabase with a
  geometry column.

---

*These are my own notes and takeaways from building a learning project. The data is
simulated and the project is not an operational tool.*
