import html
import os

PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>DOP-Galerie</title>
<style>
:root {{
  --green: #007a3d;
  --blue: #2aa9e0;
  --bg: #f5f6f7;
  --card: #ffffff;
  --text: #1a1a1a;
  --muted: #5f6368;
}}
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background: var(--bg); color: var(--text); }}
header.topbar {{ background: var(--card); border-bottom: 3px solid var(--blue); padding: 0.9em 2em; display: flex; align-items: center; gap: 0.6em; }}
header.topbar .dot {{ width: 14px; height: 14px; border-radius: 50%; background: var(--blue); display: inline-block; }}
header.topbar h1 {{ font-size: 1.3em; margin: 0; }}
main {{ padding: 1.5em 2em 2em; }}
.summary {{ color: var(--muted); margin: 0 0 1.5em; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.2em; }}
.card {{ background: var(--card); border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.14); padding: 1em; display: flex; flex-direction: column; }}
.card h2 {{ font-size: 1.05em; margin: 0 0 0.6em; }}
.card img {{ width: 100%; border-radius: 6px; display: block; }}
.meta {{ font-size: 0.8em; color: var(--muted); line-height: 1.6; margin-top: 0.6em; }}
a.more {{ color: var(--green); font-weight: 600; text-decoration: none; font-size: 0.9em; margin-top: auto; padding-top: 0.8em; align-self: flex-end; }}
a.more:hover {{ text-decoration: underline; }}
a.more .chev {{ font-size: 1.1em; }}
section.unresolved {{ margin-top: 2.5em; background: var(--card); border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.14); padding: 1em 1.2em; }}
section.unresolved h2 {{ font-size: 1.05em; margin-top: 0; }}
section.unresolved li {{ color: #a33; font-size: 0.9em; }}
footer {{ margin: 2.5em 2em 1.5em; font-size: 0.75em; color: var(--muted); border-top: 1px solid #ddd; padding-top: 0.8em; }}
</style>
</head>
<body>
<header class="topbar"><span class="dot"></span><h1>DOP-Galerie</h1></header>
<main>
<p class="summary">{resolved} Luftbild-Ausschnitte (200 m &times; 200 m, 0,10 m/Pixel), {unresolved} nicht aufgel&ouml;ste Adressen.</p>
<div class="grid">
{cards}
</div>
<section class="unresolved">
<h2>Nicht aufgel&ouml;ste Adressen</h2>
<ul>
{unresolved_items}
</ul>
</section>
</main>
<footer>Luftbilder: Geobasis NRW &ndash; Digitale Orthophotos (DOP), 10 cm Bodenaufl&ouml;sung.
Lizenz: Datenlizenz Deutschland &ndash; Zero 2.0 (https://www.govdata.de/dl-de/zero-2-0).
Adresspunkte: Geb&auml;udereferenzen NW (ALKIS), EPSG:25832.</footer>
</body>
</html>
"""

CARD = """<div class="card">
<h2>{address}</h2>
<img src="{img}" alt="{address}">
<div class="meta">
EPSG:25832: {x:.2f}, {y:.2f} &nbsp;|&nbsp; WGS84: {lat:.6f}, {lon:.6f}<br>
Aufnahmedatum: {flight}<br>
DOP-Kachel: {tile}
</div>
<a class="more" href="{img}">Bild &ouml;ffnen <span class="chev">&rsaquo;</span></a>
</div>"""


def render_gallery(entries, unresolved, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cards = []
    for entry in entries:
        cards.append(
            CARD.format(
                img=html.escape(entry["img"]),
                address=html.escape(entry["address"]),
                x=entry["x"],
                y=entry["y"],
                lat=entry["lat"],
                lon=entry["lon"],
                flight=html.escape(entry["flight_date"] or "unbekannt"),
                tile=html.escape(entry["tile"]),
            )
        )
    unresolved_items = "".join(
        f"<li>{html.escape(address)} &mdash; {html.escape(reason)}</li>"
        for address, reason in unresolved
    ) or "<li>keine</li>"
    page = PAGE.format(
        resolved=len(entries),
        unresolved=len(unresolved),
        cards="\n".join(cards),
        unresolved_items=unresolved_items,
    )
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    return os.path.join(out_dir, "index.html")
