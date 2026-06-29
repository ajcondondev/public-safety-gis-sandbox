#!/usr/bin/env bash
# run.sh — run the full Public Safety GIS pipeline on macOS/Linux.
# Usage:  ./run.sh            # full pipeline
#         ./run.sh --tests    # run tests first, then pipeline
set -euo pipefail
cd "$(dirname "$0")"
python scripts/run_pipeline.py "$@"
