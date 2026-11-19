## Why

The user wants a larger context around each house: the per-address DOP cutout should be 200 m instead of 100 m, so each gallery card shows the whole house plot plus its surroundings (street, neighboring plots), not just the immediate parcel.

## What Changes

- The cutout size per address changes from **100 m x 100 m (1000 x 1000 px)** to **200 m x 200 m (2000 x 2000 px)** at the unchanged source resolution of 0.10 m/px, still centered on the house point in EPSG:25832.
- Spec impact: MODIFIED requirement "Orthophoto cutout geometry" in the `dop-gallery` capability (size 100 m -> 200 m, pixels 1000 -> 2000). The main spec's `## Purpose` also says "100 m x 100 m" and is updated directly during implementation (Purpose edits go to the main spec, not the delta).
- Recorded assumption: "200 m" means a 200 m x 200 m square (side length 200 m) centered on the house point; the size stays a fixed constant, no new CLI option.
- Mosaic behavior is unchanged in principle: a 200 m box spans at most 2 x 2 of the 1 km tiles, so the existing multi-tile mosaic logic covers it.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `dop-gallery`: "Orthophoto cutout geometry" requirement changes from 100 m x 100 m / 1000 x 1000 px to 200 m x 200 m / 2000 x 2000 px.

## Impact

- Code: `src/dop_gallery/tiles.py` (`CUTOUT_M` 100.0 -> 200.0) and the summary string in `src/dop_gallery/render.py` ("100 m x 100 m" -> "200 m x 200 m").
- Tests: `tests/test_offline.py` expects 1000 x 1000 JPEGs -> 2000 x 2000; `tests/test_tiles.py` passes `half=` explicitly and stays valid.
- Docs: `README.md` mentions of 100 m / 1000 x 1000 px updated to 200 m / 2000 x 2000 px.
- Main spec `openspec/specs/dop-gallery/spec.md`: Purpose wording updated directly (100 m -> 200 m).
- No staging, geocoding, or offline behavior changes; staged tiles are unaffected (same 1 km tiles).
