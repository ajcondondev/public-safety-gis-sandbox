# Makefile — convenience targets for the Public Safety GIS pipeline.
# Usage: make all | make data | make maps | make test | make clean

PY ?= python

.PHONY: all data analysis serve report maps dashboard metadata test clean

all:        ## run the entire pipeline (stages 01-09)
	$(PY) scripts/run_pipeline.py

quick:      ## data + analysis only (skip maps/dashboard/metadata)
	$(PY) scripts/run_pipeline.py --quick

data:       ## generate + clean + validate
	$(PY) scripts/01_create_project_structure.py
	$(PY) scripts/02_load_clean_data.py
	$(PY) scripts/03_validate_gis_data.py

analysis:   ## spatial analysis layers
	$(PY) scripts/04_generate_analysis_layers.py

serve:      ## dashboard tables + SQLite database
	$(PY) scripts/05_export_dashboard_tables.py

report:     ## summary report
	$(PY) scripts/06_generate_summary_report.py

maps:       ## interactive + static maps
	$(PY) scripts/07_generate_maps.py

dashboard:  ## self-contained HTML dashboard
	$(PY) scripts/08_build_dashboard.py

metadata:   ## FGDC/ISO-style layer metadata
	$(PY) scripts/09_generate_metadata.py

test:       ## run the unittest suite
	$(PY) -m unittest discover -s tests -v

clean:      ## remove generated artifacts (keeps committed sources)
	rm -rf data/simulated/* data/processed/* outputs/geojson/* \
	       outputs/dashboard_tables/* outputs/reports/* outputs/dashboard/* \
	       outputs/metadata/* outputs/*.sqlite \
	       outputs/maps/*.png outputs/maps/*.svg outputs/maps/*.html
