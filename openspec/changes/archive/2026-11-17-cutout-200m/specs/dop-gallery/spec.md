## MODIFIED Requirements

### Requirement: Orthophoto cutout geometry
For each resolved address the system SHALL produce a cutout of 200 m x 200 m centered on the house point in EPSG:25832, rendered at the source resolution of 0.10 m/px (2000 x 2000 px), using the newest available DOP imagery, and SHALL mosaic across 1 km tile boundaries when the box spans more than one tile.

#### Scenario: Cutout size and resolution
- **WHEN** a house point lies in the middle of a DOP tile
- **THEN** the output image is 2000 x 2000 px covering exactly 200 m x 200 m centered on the house point

#### Scenario: Box crossing a tile boundary
- **WHEN** the 200 m box around a house point spans two or more 1 km DOP tiles
- **THEN** the cutout is assembled seamlessly from all covering tiles

### Requirement: JPEG image format
The system SHALL write cutouts as JPEG images suitable for direct viewing in a browser.

#### Scenario: Viewable image
- **WHEN** a cutout is written
- **THEN** the file is a valid JPEG of 2000 x 2000 px
