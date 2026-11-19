## Why

We need digital orthophotos (DOP) of ~200 house plots in North Rhine-Westphalia, starting from nothing but a CSV of addresses, and the result must be usable on a machine with no internet connection. NRW publishes its DOPs as open data (Datenlizenz Deutschland – Zero 2.0) with 10 cm ground resolution, and official address coordinates (Hauskoordinaten NRW), but there is no tool that chains address -> coordinates -> newest orthophoto cutout -> a browsable gallery, fully offline. This change builds that tool.

## What Changes

- New CLI tool `dop-gallery` (Python, English) with two commands:
  - `stage`: run once **with** internet. Downloads the Hauskoordinaten NRW address-point dataset and the current ("akt") DOP JPEG2000 tiles covering the input addresses, queries flight dates per tile from the `nw_dop_utm_info` WMS layer, and writes a local `data/` directory (tiles renamed to their 1 km grid cell name, a tile manifest with flight dates, the address database).
  - `run`: **fully offline**. Reads the address CSV, geocodes against the local Hauskoordinaten data, crops a 100 m x 100 m (1000 x 1000 px at 10 cm/px) cutout of the newest DOP around each house point (mosaicking across 1 km tile boundaries when needed), and renders an HTML gallery.
- New capability `dop-gallery` (see specs delta).
- No existing code is modified; the project is a greenfield scaffold.

## Capabilities

### New Capabilities
- `dop-gallery`: offline tool that turns a CSV of NRW addresses into an HTML gallery of the newest digital orthophoto cutouts (100 m x 100 m per house plot), with a one-time online `stage` step that provisions local geodata.

### Modified Capabilities
- None (no existing specs).

## Impact

- New Python package/CLI under the project root; dependencies: `pandas` (CSV), `rasterio` (reads NRW JPEG2000 DOP tiles via bundled GDAL/OpenJPEG, crops and writes JPEG), `requests` (stage-time downloads only). HTML rendering via Python stdlib string templating (no web framework).
- External data sources (stage-time only, open data):
  - DOP tiles: `https://www.opengeodata.nrw.de/produkte/geobasis/lusat/akt/dop/dop_jp_f10/` (current product; license Datenlizenz Deutschland – Zero 2.0, no attribution required)
  - DOP flight metadata: WMS `https://www.wms.nrw.de/geobasis/wms_nw_dop`, layer `nw_dop_utm_info` (returns per-tile `Kachelname`, `Bildflugdatum`, `Bodenauflösung`; verified: 1 km x 1 km UTM32 grid, e.g. Kachelname `32356_5645`, 0.10 m/px, flight 11.05.2025)
  - Address points: Hauskoordinaten NRW via GEOportal.NRW (open data)
  - (Fallback geocoder if Hauskoordinaten staging proves impractical: Nominatim, 1 req/s, OSM ODbL - recorded as an implementation fallback, not the primary path.)
- The `run` command performs zero network access; all geodata is read from the staged `data/` directory.
- Output layout: `<out>/index.html` plus `<out>/images/<address-slug>.jpg`; unmatched addresses are listed in the gallery, never silently dropped.
