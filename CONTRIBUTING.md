# Contributing

Thanks for your interest! This is a **portfolio / educational** project, so the
goal is clarity and correctness over feature volume. Contributions, suggestions,
and forks for your own learning are welcome.

## Ground rules

1. **Keep it safe.** Use only public or simulated data. Never add real 911 data,
   private resident data, or security-sensitive facility details. Keep the
   disclaimer on every user-facing artifact.
2. **Keep it runnable with no special software.** The core pipeline
   (`scripts/01`–`09`) must run on `pandas` + `PyYAML` only. Esri/ArcPy and other
   heavy dependencies stay optional and clearly marked (see `scripts/optional/`).
3. **Keep it honest.** Document approximations and limitations rather than hiding
   them.

## Development workflow

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v      # tests must pass
python scripts/run_pipeline.py               # full pipeline must build clean
```

- Add or update a test in `tests/test_pipeline.py` for any logic change.
- Run the pipeline end to end before opening a PR; CI will do the same on
  Python 3.10 and 3.12.
- Match the existing code style: small functions, docstrings that tie the code to
  a GIS Solutions Engineer responsibility, and comments explaining the *why*.

## Good first contributions

- Swap a simulated layer for a real public source (see `docs/data_sources.md`).
- Add a new QA check (extend `docs/qa_qc_plan.md` + `scripts/03`).
- Add a static map or dashboard panel.
- Improve documentation or the learning guide.

By contributing you agree your contributions are licensed under the project's
[MIT License](LICENSE).
