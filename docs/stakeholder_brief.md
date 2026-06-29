# Stakeholder Brief

> **This is a portfolio demonstration using public or simulated data. It is not an official emergency management product and should not be used for operational decision-making.**

**To:** Emergency management leadership, public-safety officials, agency partners
**From:** GIS Solutions (portfolio demonstration)
**Re:** Concord–Manchester Public Safety GIS Readiness Dashboard
**Length:** ~1–2 pages, plain English

---

## What this is

A demonstration of how geographic information system (GIS) tools can give
emergency managers a clear, trustworthy, at-a-glance picture of readiness across
the Concord-to-Manchester corridor — the ten towns along the I-93 / NH-3 route.
It pulls together the locations of fire, EMS, and police stations, emergency
operations centers, shelters, and hospitals; layers in where incidents are
happening and where hazards exist; and turns all of that into maps, a dashboard,
and a short readiness report.

**Important:** every number and location in this demonstration is simulated. It
is built to show *capability*, not to report real conditions, and it is not for
operational use.

## Why it matters

During planning and especially during an emergency, decision-makers need to
answer a few questions fast:

- Where are our response resources, and which shelters are open?
- What is happening right now, and how serious is it?
- What is at risk from flooding or severe weather?
- Where are the gaps — urgent situations far from the nearest help?

Answering those quickly, from data you can trust, is exactly what this system is
designed to do.

## What it shows (from the simulated data)

- **120 simulated incidents** across the corridor, automatically ranked by
  priority (P1 *Immediate* through P4 *Monitor*) using severity, whether the
  incident is still open, hazard exposure, and distance to the nearest facility.
- A live list of **open, high-severity incidents** — the "look here first" list.
- **Coverage gaps:** high-priority incidents located more than three miles from
  the nearest operational facility — candidates for mutual-aid planning or
  resource pre-positioning.
- **Shelters** summarized by status (open / standby / closed) and total capacity.
- **Hazard exposure:** which facilities, shelters, and hospitals fall inside
  simulated floodplain or severe-weather zones.
- **A town-by-town readiness summary** combining incident load, local resources,
  shelter capacity, and hazard exposure in one table.

## How it could support planning and response

- **Planning:** the town readiness summary highlights where incident demand is
  high relative to available facilities and shelter capacity, informing where to
  invest or pre-position resources.
- **Response:** priority ranking and nearest-facility distances help direct
  limited crews to the most urgent locations first.
- **Situational awareness:** the maps and dashboard provide a shared operating
  picture for an Emergency Operations Center.
- **Field updates:** a companion mobile form (Survey123) lets responders report
  shelter status and road closures that update the dashboard in near-real time.

## How we know the data can be trusted

Before any of this is shown, the system runs automated **data-quality checks**
and produces a report. In this demonstration it deliberately includes a few
planted errors — missing locations, a duplicate record, impossible coordinates —
and the checks catch all of them. In real use, those errors would be corrected
at the source before the information informed any decision. This "show your work"
step is what separates a credible product from a nice-looking but unreliable one.

## Limitations (please read)

- **Simulated data.** Names, locations, and incidents are illustrative only.
- **Approximate distances.** Distances are straight-line, not drive-time; real
  planning would use the road network.
- **Illustrative hazards.** Hazard zones are drawn for demonstration, not taken
  from official FEMA or National Weather Service products.
- **Not operational.** This is a portfolio demonstration, not an official
  emergency management tool.

## What a real deployment would add

Authoritative public data (NH GRANIT, FEMA flood layers, HIFLD infrastructure),
drive-time analysis, automatic scheduled updates, live web maps and dashboards
published to ArcGIS Online, and a connection to an enterprise database. The
groundwork — the data model, the quality checks, the analysis, and the
reporting — is already in place and would carry directly into that build.

---

*Questions or a walkthrough: see the project README and the StoryMap outline.*
