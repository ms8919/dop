## Context

The `dop-gallery` tool (implemented, archived as `2026-11-17-dop-gallery`) generates a static HTML gallery from `src/dop_gallery/render.py` using inline string templates (`PAGE`, `CARD`). Current output is English with plain default styling. The user wants the gallery in German and styled like the Stadtwerke Münster homepage screenshot: light background, top bar, white rounded shadow cards in a 3-column grid, bold titles, green chevron links, blue accent. See proposal.md for scope and `specs/dop-gallery/spec.md` for the delta (MODIFIED "HTML gallery output", ADDED "Gallery visual style").

## Goals / Non-Goals

**Goals:**
- Gallery UI fully in German; card-based layout matching the reference style elements.
- Only `render.py` changes in code; offline behavior, cutouts, geocoding untouched.

**Non-Goals:**
- No copying of the Stadtwerke Münster logo, brand name, or nav items (third-party branding) — header shows a neutral "DOP-Galerie" title.
- CLI help text stays English; only the generated HTML is German.
- No dark mode, no interactivity beyond static cards, no pagination.

## Decisions

- **Restyle only the templates in `render.py`** (PAGE/CARD strings + CSS) instead of introducing a template engine — the project deliberately uses stdlib string templating; a static gallery needs nothing more.
- **Palette approximated from the screenshot** (recorded assumption, since no exact brand values were provided): green primary `#007a3d`-range for links/accents, light blue `#2aa9e0`-range for the header accent, page background `#f5f6f7`, cards `#ffffff` with `border-radius: 8px` and a soft `box-shadow`. Exact hex values are a design detail to fine-tune during implementation against a rendered screenshot.
- **German strings**: title "DOP-Galerie", summary "X Luftbild-Ausschnitte (100 m x 100 m, 0,10 m/Pixel), Y nicht aufgelöste Adressen", section "Nicht aufgelöste Adressen", card labels "Aufnahmedatum:", "DOP-Kachel:", coordinates "EPSG:25832:" / "WGS84:", unresolved reason "keine passende Adresse gefunden" / "mehrdeutig (N Kandidaten)" / "Kachel fehlt", footer with Geobasis NRW + Datenlizenz Deutschland – Zero 2.0 (license name stays as-is). The CLI-side reason strings in `run.py` feed the unresolved section, so those become German too (small edit in `run.py`, still no behavior change).
- **Chevron links**: each card gets a green "›" style link element (e.g. "Bild öffnen ›" linking to the image) to mirror the reference's green chevron links; pure CSS, no JS.
- **Header**: simple top bar with blue-tinted accent and bold "DOP-Galerie" title — replaces the reference's logo+nav without using them.

## Risks / Trade-offs

- [Risk] Palette is approximated from a screenshot, not brand guidelines -> Mitigation: implement with CSS variables at the top of the template so colors are adjustable in one place; verify visually with a rendered screenshot during apply.
- [Risk] German strings in `run.py` (unresolved reasons) leak into CLI stdout as well -> acceptable: user asked for German UI; CLI messages becoming German is consistent. Recorded in proposal.
- [Risk] Existing test `test_offline.py` asserts English strings ("Aerial flight date", footer) -> Mitigation: update assertions to the German strings in the same change.

## Migration Plan

No migration: regenerating a gallery with the new `run` command produces the new style. Old galleries remain as generated.

## Open Questions

- None blocking: exact hex values and whether cards should link to the full image are deferrable details (CSS variables + a chevron link per card, per the style requirement).
