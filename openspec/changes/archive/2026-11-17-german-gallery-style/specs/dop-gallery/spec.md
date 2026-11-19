## MODIFIED Requirements

### Requirement: HTML gallery output
The system SHALL write the result as a gallery folder containing `index.html` and an `images/` directory with one JPEG per resolved address, named by an address slug. The gallery SHALL be in German and SHALL show, per address: the address text, the cutout image, the coordinates (EPSG:25832 and WGS84), the flight date, and the DOP tile name.

#### Scenario: Gallery layout
- **WHEN** the run completes with 200 input addresses of which 195 resolve
- **THEN** `<out>/index.html` exists, `<out>/images/` contains 195 JPEGs named by address slug, 195 cards show address + image + metadata, and 5 unresolved addresses are listed separately

#### Scenario: German UI language
- **WHEN** `index.html` is rendered
- **THEN** all visible UI text (page title, headings, summary, card labels, unresolved section, footer) is in German, e.g. the heading "DOP-Galerie" and the unresolved section "Nicht aufgelöste Adressen"

## ADDED Requirements

### Requirement: Gallery visual style
The gallery page SHALL use a card-based layout in the style of the reference screenshot: a light gray page background with a top header bar containing the gallery title; a responsive grid of white cards with rounded corners (about 8 px) and a subtle drop shadow; each card shows the address as a bold title, the cutout image, and small gray metadata; accent elements (header title area, links/labels) use a green primary and light-blue secondary color, with green chevron links (`›`) where actions or links appear. The page SHALL NOT contain third-party logos, brand names, or navigation items from the reference site.

#### Scenario: Style markers present
- **WHEN** `index.html` is rendered
- **THEN** the HTML contains the card grid CSS (rounded corners, box-shadow), the green accent color, a header with the title "DOP-Galerie", and at least one chevron link (`›`); and it contains no reference to "Stadtwerke"

#### Scenario: Cards render addresses
- **WHEN** the gallery has resolved addresses
- **THEN** each card contains one `<img>` pointing into `images/`, the bold address title, and the metadata lines (coordinates, flight date, tile name) in German
