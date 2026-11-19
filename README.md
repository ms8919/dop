# dop-gallery

`dop-gallery` macht aus einer Liste von Adressen in Nordrhein-Westfalen eine
HTML-Galerie mit Luftbildern. Für jede Adresse wird ein Bild-Ausschnitt von
200 m x 200 m aus den offiziellen Orthofotos (DOP) von NRW erstellt.

Das Besondere: Nach einem einmaligen Daten-Download arbeitet das Programm
**komplett ohne Internet**.

## Was das Programm macht

```
Adress-CSV  -->  Adresse in Koordinaten umwandeln  -->  Luftbild-Ausschnitt (200 m x 200 m)
                                                          |
                                              HTML-Galerie (index.html + Bilder)
```

Die Luftbilder haben eine Auflösung von 10 cm pro Pixel. Jedes Bild ist also
2000 x 2000 Pixel groß. In der Galerie sieht man zu jeder Adresse: das Bild,
die Koordinaten, das Aufnahmedatum des Luftbilds und die Kachel-Nummer.

## Voraussetzungen

- Python 3.11 oder neuer
- Internet nur für den einmaligen Download der Daten (Schritt 1)

## Installation

```bash
pip install -e .
```

Oder mit [uv](https://docs.astral.sh/uv/):

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
```

Danach gibt es den Befehl `dop-gallery`. Alternativ geht auch
`python -m dop_gallery`.

## Schritt 1: Daten einmalig herunterladen (braucht Internet)

```bash
dop-gallery stage --addresses adressen.csv --data-dir data
```

Dieser Befehl lädt einmalig:

- die offiziellen Adress-Koordinaten von NRW (Gebäudereferenzen NW) nach `data/addresses.db`
- die passenden Luftbild-Kacheln (JPEG2000) nach `data/tiles/`
- eine Liste mit dem Aufnahme-Datum jeder Kachel: `data/tiles_manifest.csv`

Danach wird kein Internet mehr benötigt. Der Befehl kann jederzeit erneut
ausgeführt werden, um die Daten zu aktualisieren.

## Schritt 2: Galerie erstellen (funktioniert ohne Internet)

```bash
dop-gallery run --addresses adressen.csv --data-dir data --out galerie
```

Das Ergebnis liegt dann in `galerie/`:

```
galerie/
  index.html          <- im Browser öffnen
  images/*.jpg        <- ein Bild pro Adresse (2000 x 2000 Pixel)
```

Die Galerie ist auf Deutsch und im Kachel-Stil gestaltet: eine Kopfzeile oben,
darunter weiße Kacheln mit abgerundeten Ecken auf hellgrauem Hintergrund. Jede
Kachel zeigt die Adresse, das Luftbild und die Angaben dazu (Koordinaten,
Aufnahmedatum, Kachel-Nummer) sowie einen grünen Link „Bild öffnen ›".

Adressen, die nicht gefunden wurden, stehen in der Galerie in einem eigenen
Abschnitt „Nicht aufgelöste Adressen". Sie gehen nicht verloren.

## Die Adress-CSV-Datei

Die Datei braucht eine Kopfzeile mit Spalten-Namen. Standard-Spalten:

```csv
street,house_number,zip,city
Domkloster,4,50667,Köln
Bahnhofsvorplatz,1,50667,Köln
```

Hat deine CSV deutsche Spalten-Namen, dann gib sie mit `--col-*` an:

```csv
strasse,hausnr,plz,ort
Domkloster,4,50667,Köln
```

```bash
dop-gallery run --addresses adressen.csv --data-dir data --out galerie \
  --col-street strasse --col-house-number hausnr --col-zip plz --col-city ort
```

## Alle Optionen

| Option | Bedeutung | Standard |
|---|---|---|
| `--addresses` | CSV-Datei mit den Adressen | (Pflicht) |
| `--data-dir` | Ordner mit den heruntergeladenen Daten | `data` |
| `--col-street` | Spalte mit der Straße | `street` |
| `--col-house-number` | Spalte mit der Hausnummer | `house_number` |
| `--col-zip` | Spalte mit der PLZ | `zip` |
| `--col-city` | Spalte mit dem Ort | `city` |
| `--out` | Ausgabe-Ordner für die Galerie (nur bei `run`) | `dop-gallery` |

## Datenquellen und Lizenz

- Luftbilder: Digitale Orthophotos (DOP) von Geobasis NRW, 10 cm Auflösung
- Adress-Koordinaten: Gebäudereferenzen NW (ALKIS)
- Lizenz: [Datenlizenz Deutschland – Zero 2.0](https://www.govdata.de/dl-de/zero-2-0)
  (freie Nutzung, keine Namensnennung nötig)

## Tests ausführen

```bash
pytest tests/
```

## Projekt-Struktur

```
src/dop_gallery/
  cli.py       Befehlszeile (stage / run)
  stage.py     lädt die Daten einmalig herunter (braucht Internet)
  run.py       erstellt die Galerie (ohne Internet)
  geocode.py   findet Adressen in der lokalen Datenbank
  tiles.py     schneidet die Bild-Ausschnitte aus den Kacheln
  render.py    erstellt die HTML-Galerie
tests/         Unit-Tests
```
