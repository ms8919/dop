## 1. Restyle and translate the gallery templates

- [x] 1.1 Rewrote the `PAGE`/`CARD` templates and CSS in `src/dop_gallery/render.py`: German UI strings (title "DOP-Galerie", summary, "Nicht aufgelöste Adressen", card labels "Aufnahmedatum"/"DOP-Kachel", footer), light gray background, top header bar with blue-tinted accent and bold title, responsive white card grid (3 columns, `border-radius: 8px`, subtle `box-shadow`), bold address title per card, small gray metadata, green chevron link (`›`) per card, green/blue accent colors defined as CSS variables at the top. Verify by rendering a sample gallery and checking the HTML contains the German strings, card CSS, accent color variables, and chevron.
- [x] 1.2 Updated the unresolved-reason strings in `src/dop_gallery/run.py` to German ("keine passende Adresse gefunden", "mehrdeutig (N Kandidaten)", "Kachel <name> fehlt") so the unresolved section is fully German. Verify `pytest tests/` still passes after updating the assertions in `tests/test_offline.py` to the German strings (e.g. "Aufnahmedatum", license footer, "Nicht aufgelöste Adressen").

## 2. Tests and visual verification

- [x] 2.1 Added `tests/test_render.py` asserting the rendered `index.html` contains: heading "DOP-Galerie", German section "Nicht aufgelöste Adressen", card class/CSS with border-radius and box-shadow, the green accent color variable, a chevron `›`, and does NOT contain "Stadtwerke". Verify the test passes.
- [x] 2.2 Regenerated the e2e gallery from the staged fixture data (`/tmp/e2e`, 10 addresses + 1 unresolvable, run fully offline with sockets blocked) and visually verified via browser screenshot: header bar with blue accent + "DOP-Galerie", 3-column grid of white rounded shadow cards, bold address titles, images, German metadata ("Aufnahmedatum: 11.05.2025", "DOP-Kachel: ..."), green "Bild öffnen ›" chevron links, "Nicht aufgelöste Adressen" section, German license footer. (Note: the screenshot tool renders file:// URLs blank in this environment; served the gallery over localhost HTTP for the visual check.)

## 3. Docs and validation

- [x] 3.1 Updated `README.md` (German): gallery-output section now describes the German card-style gallery (header, white rounded cards, green "Bild öffnen ›" links) and the "Nicht aufgelöste Adressen" section — matching the actual output strings.
- [x] 3.2 Ran full `pytest tests/` (21/21 pass), `openspec validate german-gallery-style --strict` (valid), `openspec status --change german-gallery-style` (proposal/specs/design/tasks all done).
