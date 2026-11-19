## Context

`dop-gallery` currently cuts a 100 m x 100 m (1000 x 1000 px at 0.10 m/px) window per address, centered on the house point, from staged 1 km DOP tiles (`CUTOUT_M = 100.0` in `src/dop_gallery/tiles.py`; `cutout()` derives the pixel size from the tile resolution as `round(2 * half / res)`). The user wants 200 m per address. See proposal.md and the delta in `specs/dop-gallery/spec.md`.

## Goals / Non-Goals

**Goals:**
- Cutout becomes 200 m x 200 m = 2000 x 2000 px, still centered on the house point, still mosaicked across tile boundaries, still fully offline.

**Non-Goals:**
- No configurable `--size` CLI flag (the size stays a fixed constant; recorded assumption in the proposal).
- No change to staging, geocoding, tile grid, or the gallery layout.

## Decisions

- **Change only the `CUTOUT_M` constant (100.0 -> 200.0) in `tiles.py`.** `cutout()` already computes the pixel window from the tile resolution, so 200 m automatically yields 2000 x 2000 px; the mosaic logic (`kachel_cells`) is resolution-independent and a 200 m box still spans at most 2 x 2 tiles, so no logic changes are needed. Alternative (CLI option per run) rejected: not requested, adds surface area.
- **Update the visible size text** in `render.py`'s summary ("100 m x 100 m" -> "200 m x 200 m") so the gallery matches the actual geometry.
- **Main spec Purpose is edited directly** (`openspec/specs/dop-gallery/spec.md`, "100 m x 100 m house-plot image" -> "200 m x 200 m"), because delta specs must not carry a Purpose for an existing capability.

## Risks / Trade-offs

- [Risk] Larger cutouts double JPEG dimensions (2000 x 2000), roughly quadrupling file size per image (~4x pixels) -> acceptable: ~200 addresses still produce a gallery of a few hundred MB at most; JPEG quality stays 90.
- [Risk] Tests hardcode 1000 x 1000 -> update `tests/test_offline.py` expectation to 2000 x 2000; `tests/test_tiles.py` passes `half=` explicitly and remains valid as-is.

## Migration Plan

No migration: rerun `dop-gallery run` on staged data to regenerate the gallery with 200 m cutouts. Staged tiles need no change.

## Open Questions

- None.
