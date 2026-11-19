## Context

Greenfield Python CLI in this repo. NRW publishes the required geodata as open data: current DOPs as JPEG2000 tiles (10 cm/px, RGBI, 1 km x 1 km grid in UTM32 / EPSG:25832, tile name = `<zone>_<easting_km>_<northing_km>`, e.g. `32356_5645`) via OpenGeodata.NRW (`produkte/geobasis/lusat/akt/dop/dop_jp_f10/`), per-tile flight dates via WMS `wms_nw_dop` layer `nw_dop_utm_info` (verified live: `Kachelname=32356_5645`, `Bildflugdatum=11.05.2025`, `Bodenauflösung=0.10`), and official address points (Hauskoordinaten NRW) via GEOportal.NRW. License: Datenlizenz Deutschland - Zero 2.0. See proposal.md for motivation and specs/dop-gallery/spec.md for the behavior contract.

## Goals / Non-Goals

**Goals:**
- `run` is structurally offline: it imports no HTTP client at all, so no network call can happen by accident.
- One address in the CSV -> one 1000 x 1000 px JPEG + one gallery card, newest imagery, flight date visible.
- Failures are per-address and visible in the gallery, never silent.

**Non-Goals:**
- No map view with pins, no PDF/Excel export, no historical (hist_dop) vintages, no re-cropping at sizes other than 100 m.
- No server / web app; the gallery is static files.
- `stage` is not optimized for huge address lists beyond the ~200-address scale; it may re-download the whole Hauskoordinaten dataset.

## Decisions

- **Two commands, `stage` (online, once) and `run` (offline), instead of one command with runtime caching.** The offline requirement is enforced structurally: `run` never imports `requests`. Alternative considered: single command that fetches on demand and caches - rejected because it can hit the network on the first run and would need rate limiting.
- **Local official address points (Gebäudereferenzen NW) as the geocoder, instead of Nominatim at runtime.** Nominatim requires internet (and 1 req/s), which violates the offline-first-run requirement; a per-address cache baked at stage time would only work for the exact staged CSV. Spike result (task 2.2): the bulk-distributed official address-point data is "Gebäudereferenzen NW" on OpenGeodata.NRW (`lk/akt/gebref_txt/gebref_EPSG25832_ASCII.zip`, 97 MB, `;`-separated ASCII, one row per address point in EPSG:25832). `stage` converts it once into a SQLite `addresses.db` (4.5 M points, ~26 s). Note: the file carries no PLZ, so the match key is `city + street + house number` (normalized); the CSV `zip` column is kept for display. Fallback recorded: if staging proves impractical, `stage` geocodes the input CSV via Nominatim and stores `geocode_cache.csv`.
- **Stage downloads raw DOP tiles; `run` crops locally with rasterio, instead of `stage` fetching pre-cut WCS images.** WCS (`wcs_nw_dop`, coverage `nw_dop`, verified: GeoTIFF/PNG/JPEG output, EPSG:25832, subsetting+scaling) could cut 100 m boxes directly at stage time, but then `run` would only render HTML and could never re-crop offline. rasterio (bundles GDAL + OpenJPEG) reads the JP2 tiles directly, so all imagery work happens offline. Alternative rejected: GDAL CLI subprocess - rasterio's Python API is cleaner for mosaic + crop + JPEG write.
- **Tiles stored renamed to their Kachelname** (`data/tiles/32356_5645.jp2`) plus `data/tiles_manifest.csv` (kachelname, flight_date, gsd) captured at stage time from `nw_dop_utm_info`. This makes the offline tile lookup pure arithmetic: UTM32 point -> easting//1000, northing//1000 -> up to 2x2 candidate cells for a 100 m box -> open, mosaic if needed, crop.
- **Address normalization before matching:** lowercase, fold umlauts (ae/oe/ue/ss), strip punctuation, normalize street abbreviations (`str.` -> `strasse` etc.), keep house-number letter suffixes (`12a`). Match key: `city + street + house number` (the staged Gebäudereferenzen file has no PLZ). Multiple distinct coordinates -> reported as ambiguous, not guessed.
- **Gallery as a folder (`index.html` + `images/<slug>.jpg`), rendered with stdlib string templating, English.** Alternative considered: one self-contained HTML with base64 images - rejected (~30-80 MB single file, hard to host/edit); folder is shareable as-is.
- **Stack:** Python 3, `pandas` for CSV, `rasterio` for imagery, `requests` imported only in the stage module, stdlib `argparse` + `html` for CLI and gallery. No web framework.

## Risks / Trade-offs

- [Risk] Exact JP2 file URL pattern on opengeodata.nrw is not browsable (directory listing returns 404; only the Kachelname is known from the WMS info layer) -> Resolved by spike (task 2.1): real folder is `lusat/akt/dop/dop_jp2_f10/` with `index.json` listing all 36616 files; pattern `dop10rgbi_32_<east_km>_<north_km>_1_nw_<year>.jp2`. `stage` fetches `index.json` once and maps Kachelname -> file. Remaining fallback if that ever breaks: synthesize tiles via WCS GetCoverage on `wcs_nw_dop` (coverage `nw_dop`, axes `x`/`y`, origin 278000.05/5827999.95, res 0.1, EPSG:25832) and store GeoTIFFs instead of JP2.
- [Risk] Hauskoordinaten NRW distribution format/packaging (per-municipality files? GML/CSV/SHP?) is unknown until downloaded -> Mitigation: spike task downloads a sample, then `stage` converts it once into a local queryable store (SQLite/Spatialite or GeoPackage indexed by zip+street); `run` only reads that store.
- [Risk] rasterio build without OpenJPEG cannot read JP2 -> Mitigation: spike task verifies `rasterio.open()` on one staged tile before the rest of the pipeline is built.
- [Risk] Address variants (umlauts, abbreviations, `12 a` vs `12a`) cause false "unresolved" -> Mitigation: normalization rules above + ambiguity/unresolved section in the gallery so mismatches are visible; acceptance target is that clearly formatted addresses resolve.
- [Risk] Staged tiles age as NRW re-flies on a ~2-year cycle -> Mitigation: `stage` is re-runnable to refresh `data/`; the gallery always shows the flight date, so staleness is visible.

## Migration Plan

Greenfield change: nothing to migrate. Rollback = delete the output folder and the staged `data/` directory; no external systems are modified.

## Open Questions

- Resolved by spikes during implementation: JP2 URL pattern (`dop_jp2_f10/index.json`, task 2.1) and address bulk data (Gebäudereferenzen NW zip, task 2.2). No open questions remain.
- Exact CSV column names the user will supply - handled by configurable column options with defaults (`street, house_number, zip, city`), per the spec.
