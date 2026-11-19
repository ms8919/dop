## Why

The project now has a working `dop-gallery` CLI (implemented and verified end-to-end), but no README: a new user has no single place that explains what the tool does, how to install it, the two-step stage/run workflow, the expected CSV format, and what the output looks like. Documentation is the missing piece before the tool can be handed to others.

## What Changes

- Add a top-level `README.md` in easy-to-understand German ("einfache Sprache": short sentences, simple words, jargon explained) describing how to use the project:
  - what `dop-gallery` does (address CSV -> offline HTML gallery of NRW DOP cutouts, 100 m x 100 m per address)
  - installation (Python >= 3.11, `pip install -e .` / uv venv, dependencies)
  - the one-time online `stage` command and the fully offline `run` command, with all CLI flags (`--addresses`, `--data-dir`, `--col-street`, `--col-house-number`, `--col-zip`, `--col-city`, `--out`)
  - the input CSV format (named columns, configurable via `--col-*`, defaults `street,house_number,zip,city`) with a small example
  - the staged `data/` layout (`addresses.db`, `tiles/<kachel>.jp2`, `tiles_manifest.csv`) and the output gallery layout (`index.html` + `images/*.jpg`, card contents, unresolved-addresses section)
  - data sources and license (Geobasis NRW DOP + Gebäudereferenzen NW, Datenlizenz Deutschland - Zero 2.0), development/testing (`pytest tests/`)
- No code changes. Docs only.

## Capabilities

### New Capabilities
- None. This is a documentation-only change; `skip_specs: true` is set in `.openspec.yaml` because no spec-level behavior changes.

### Modified Capabilities
- None.

## Impact

- One new file: `README.md` at the project root. No code, tests, specs, or configuration are touched.
