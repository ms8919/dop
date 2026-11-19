## 1. Change the cutout size to 200 m

- [x] 1.1 Changed `CUTOUT_M` from 100.0 to 200.0 in `src/dop_gallery/tiles.py`; verifying below via offline e2e run that every JPEG is 2000 x 2000 x 3.
- [x] 1.2 Updated the summary string in `src/dop_gallery/render.py` to "200 m x 200 m".

## 2. Tests, docs, spec

- [x] 2.1 Updated `tests/test_offline.py` to expect 2000 x 2000 JPEGs; full `pytest tests/` passes (21/21; `tests/test_tiles.py` needed no change).
- [x] 2.2 Updated `README.md`: all four mentions now "200 m x 200 m" / "2000 x 2000 Pixel"; verified against actual output (e2e gallery summary line shows "200 m x 200 m").
- [x] 2.3 Updated the main spec Purpose directly in `openspec/specs/dop-gallery/spec.md` to "one 200 m x 200 m house-plot image per address".

## 3. Validation

- [x] 3.1 Ran `pytest tests/` (21/21 pass), `openspec validate cutout-200m --strict` (valid), `openspec status --change cutout-200m` (all artifacts done). Offline e2e after re-stage: 10 resolved + 1 unresolved, all 10 JPEGs 2000x2000x3.
