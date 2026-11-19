## Purpose

Turn a CSV of North Rhine-Westphalia addresses into an HTML gallery of the newest digital orthophoto (DOP) cutouts, one 100 m x 100 m house-plot image per address, on a machine with no internet connection.

## ADDED Requirements

### Requirement: Address CSV input with named columns
The system SHALL accept a CSV file of addresses whose columns are named, and the column names SHALL be configurable via CLI options with the defaults `street`, `house_number`, `zip`, `city`.

#### Scenario: Default column names
- **WHEN** the user runs the tool with a CSV containing the columns `street,house_number,zip,city` and no column options
- **THEN** each row is interpreted as one address using those columns

#### Scenario: Custom column names
- **WHEN** the user passes `--col-street strasse --col-house-number hausnr --col-zip plz --col-city ort` with a CSV using those German column names
- **THEN** each row is interpreted as one address using the mapped columns

### Requirement: Offline run command
The `run` command SHALL perform zero network access; all geodata it needs SHALL be read from the locally staged `data/` directory. A separate `stage` command, run once with internet, SHALL provision that directory.

#### Scenario: Run without network
- **WHEN** `dop-gallery run` is executed on a machine with networking disabled and a fully staged `data/` directory
- **THEN** the gallery is produced identically to a networked run

#### Scenario: Stage provisions data
- **WHEN** `dop-gallery stage --addresses addresses.csv --data-dir data/` is executed once with internet access
- **THEN** `data/` contains the address-point database, the DOP tiles covering the addresses, and a tile manifest with flight dates

### Requirement: Local address geocoding
The system SHALL resolve each CSV address to a house point in EPSG:25832 by matching against the locally staged official address-point data (Hauskoordinaten NRW), and SHALL report every address that cannot be matched or is ambiguous instead of dropping it silently.

#### Scenario: Exact match
- **WHEN** an address row matches exactly one staged address point
- **THEN** the house point coordinates are used as the cutout center

#### Scenario: No match
- **WHEN** an address row matches no staged address point
- **THEN** the address appears in an "unresolved addresses" section of the gallery with a reason, and processing continues with the remaining addresses

### Requirement: Orthophoto cutout geometry
For each resolved address the system SHALL produce a cutout of 100 m x 100 m centered on the house point in EPSG:25832, rendered at the source resolution of 0.10 m/px (1000 x 1000 px), using the newest available DOP imagery, and SHALL mosaic across 1 km tile boundaries when the box spans more than one tile.

#### Scenario: Cutout size and resolution
- **WHEN** a house point lies in the middle of a DOP tile
- **THEN** the output image is 1000 x 1000 px covering exactly 100 m x 100 m centered on the house point

#### Scenario: Box crossing a tile boundary
- **WHEN** the 100 m box around a house point spans two or more 1 km DOP tiles
- **THEN** the cutout is assembled seamlessly from all covering tiles

### Requirement: Newest imagery with visible flight date
The system SHALL use the current ("akt") statewide DOP product as the source imagery, and the gallery SHALL display, per address, the aerial flight date of the tile the cutout was taken from.

#### Scenario: Flight date shown
- **WHEN** the gallery is rendered
- **THEN** each address card shows the Bildflugdatum (e.g. 11.05.2025) recorded for its tile in the staged manifest

### Requirement: HTML gallery output
The system SHALL write the result as a gallery folder containing `index.html` and an `images/` directory with one JPEG per resolved address, named by an address slug. The gallery SHALL be in English and SHALL show, per address: the address text, the cutout image, the coordinates (EPSG:25832 and WGS84), the flight date, and the DOP tile name.

#### Scenario: Gallery layout
- **WHEN** the run completes with 200 input addresses of which 195 resolve
- **THEN** `<out>/index.html` exists, `<out>/images/` contains 195 JPEGs named by address slug, 195 cards show address + image + metadata, and 5 unresolved addresses are listed separately

### Requirement: JPEG image format
The system SHALL write cutouts as JPEG images suitable for direct viewing in a browser.

#### Scenario: Viewable image
- **WHEN** a cutout is written
- **THEN** the file is a valid JPEG of 1000 x 1000 px

### Requirement: Open data license note
The gallery SHALL include a data-source note stating that the imagery is Geobasis NRW digital orthophotos under Datenlizenz Deutschland - Zero 2.0.

#### Scenario: Source attribution present
- **WHEN** `index.html` is rendered
- **THEN** it contains a footer naming Geobasis NRW DOP and the license Datenlizenz Deutschland - Zero 2.0
