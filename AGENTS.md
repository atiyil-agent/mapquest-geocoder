# AGENTS.md

## Cursor Cloud specific instructions

This repository is a small Python CLI package, `mapquest_geocoder`, that geocodes a
city/town name into latitude/longitude via the MapQuest Geocoding API. The single
console entry point is `mapquest-geocode` (defined in `setup.py`, implemented in
`mapquest_geocoder/geocode.py`).

### Environment
- Development uses a virtualenv at `.venv` (gitignored). The startup update script
  creates/updates it and installs the package in editable mode (`pip install -e .`),
  which also pulls the only runtime dependency, `requests`.
- Always invoke tools via the venv, e.g. `.venv/bin/python`, `.venv/bin/mapquest-geocode`.
  (`python3 -m venv` needs the `python3.12-venv` system package, already present in the
  VM snapshot.)

### Test / lint / run
- Tests (stdlib `unittest`, fully mocked — no network or API key needed):
  `.venv/bin/python -m unittest discover -s tests`
- Lint: the repo ships no linter config. `pyflakes` works well if you need one
  (`.venv/bin/pip install pyflakes` then `.venv/bin/python -m pyflakes mapquest_geocoder tests setup.py`).
  It is intentionally NOT in the update script since it is not a project dependency.
- Run the CLI: `.venv/bin/mapquest-geocode "New York" --api-key YOUR_KEY`

### Gotchas
- A real, successful geocode requires a valid MapQuest API key passed via `--api-key`.
  Without one, the live API returns HTTP 401 and the CLI exits non-zero with a graceful
  error (this is expected, not a bug). The success path is covered end-to-end by the
  mocked unit tests.
