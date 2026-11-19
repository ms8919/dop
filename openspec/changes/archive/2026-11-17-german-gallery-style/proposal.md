## Why

The generated gallery is currently in English with a plain default look. The user wants the gallery in German and styled like the Stadtwerke Münster website shown in the screenshot: a light page with a top bar, a grid of white rounded cards with soft shadows, bold card titles, and green chevron links. This makes the gallery match the look and feel of the customer's own site.

## What Changes

- The generated `index.html` gallery UI becomes **German** (headings, labels, summary, unresolved section, footer wording) instead of English.
- The gallery page adopts the **card-based style** from the reference screenshot:
  - light gray page background, white cards with rounded corners (~8 px) and a subtle drop shadow
  - 3-column responsive card grid (auto-fill, min ~340 px)
  - bold, large card title (the address) at the top of each card, image below it
  - metadata in small gray text
  - green accent color for links/labels with a chevron (`›`), light-blue accent for the header/title area
  - top header bar with the gallery title
  - system sans-serif font stack
- Constraint recorded: only the **style elements** (layout, colors, cards, chevrons, typography) are adopted. The Stadtwerke Münster logo, name, and navigation items are third-party branding and are NOT copied; the header shows a neutral "DOP-Galerie" title.
- The CLI itself (`dop-gallery stage/run --help`) stays in English; only the generated gallery page is German.
- Spec impact: MODIFIED requirement "HTML gallery output" (language English -> German) plus one ADDED requirement "Gallery visual style" in the `dop-gallery` capability.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `dop-gallery`: the "HTML gallery output" requirement changes (German UI instead of English) and gains a new "Gallery visual style" requirement (card grid, rounded corners, shadow, green chevron accents, header bar, approximating the reference screenshot's style without using its logo/brand).

## Impact

- Code: only `src/dop_gallery/render.py` (HTML/CSS templates and German strings). No changes to `run.py`, `tiles.py`, `geocode.py`, `stage.py`, `cli.py`.
- Tests: `tests/test_offline.py` assertions on English UI strings are updated to the German strings; a new test asserts the style markers (card CSS class, green accent color, German heading, chevron link) are present in the generated HTML.
- Docs: `README.md` gallery-output description is updated to mention the German, card-styled gallery.
- No data, staging, or offline behavior changes.
