# Public-Safety GIS Sandbox

A learning project that builds a small GIS data workflow for emergency planning. It uses simulated data for the Concord to Manchester area in New Hampshire.

[![Live demo](https://img.shields.io/badge/live%20demo-online-2ea44f?logo=github)](https://ajcondondev.github.io/public-safety-gis-sandbox/)
[![CI](https://github.com/ajcondondev/public-safety-gis-sandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/ajcondondev/public-safety-gis-sandbox/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Note: This is a personal learning project. All data is simulated. It is not an official emergency management tool and should not be used for real decisions.

| | |
|:---:|:---:|
| ![Regional map](outputs/maps/regional_overview.png) | ![Incident priority map](outputs/maps/incident_priority.png) |

## What it does

It takes a set of simulated public-safety datasets and runs them through a few steps. The datasets are town boundaries, emergency facilities (fire, EMS, police, and others), shelters, hospitals, incidents, and hazard areas.

The steps are:

- Clean and standardize the data.
- Check the data for common problems, like missing coordinates, duplicate IDs, and values out of range.
- Run some basic spatial analysis, including the distance from each incident to the nearest facility, whether a point falls inside a hazard area, and a simple incident priority score.
- Produce map files, summary tables, a small SQLite database, an interactive map, and an HTML dashboard.

Each step is a separate Python script, numbered in the order it runs.

## Why I built it

I wanted to learn how GIS is used in public safety and emergency planning, and I learn best by building something. This let me practice the full path from raw data to maps and dashboards. It also made me work through the parts that are easy to skip when you only read about them, like data cleaning and quality checks.

## Main features

- A pipeline of small scripts that run in order (clean, validate, analyze, report).
- Data quality checks with a written report of what was found.
- Distance and point-in-polygon analysis written in plain Python, so no heavy GIS library is needed.
- A SQLite database with example SQL queries.
- An interactive map (Leaflet) and a simple HTML dashboard, both viewable in a browser.
- Unit tests and a GitHub Actions workflow that runs the pipeline.

## Tools used

- Python (pandas, PyYAML)
- SQLite
- Leaflet for the interactive map
- matplotlib for the static maps (optional)
- GitHub Actions for CI

The pipeline runs with just pandas and PyYAML. The ArcGIS and Esri parts are written up as notes in the `docs` folder. They are not needed to run anything.

## How to run or view it

To view it without installing anything, open the live demo:
https://ajcondondev.github.io/public-safety-gis-sandbox/

To run it locally:

```
pip install -r requirements.txt
python scripts/run_pipeline.py
```

Then open `outputs/index.html` in a browser. It links to the map, the dashboard, and the reports.

To run the tests:

```
python -m unittest discover -s tests
```

## Project structure

```
scripts/   numbered pipeline steps (01 to 09) plus helpers
sql/       database schema and example queries
tests/     unit tests
docs/      notes on the data, the workflow, and GIS concepts
data/      simulated input data
outputs/   generated maps, dashboard, reports, and data files
```

## What I learned

- How a GIS data workflow fits together, from raw files to maps and dashboards.
- Why data quality checks matter, and how to write checks that catch real problems.
- The basics of spatial analysis, like distance and point-in-polygon tests.
- How to keep a project reproducible with a config file, tests, and a single command to run everything.
- The difference between storing coordinates for the web and projecting them for accurate distance.

## Next improvements

- Replace the simulated data with real public datasets.
- Use road network distance instead of straight-line distance.
- Publish the layers and a dashboard in ArcGIS Online.
- Add more validation checks.
