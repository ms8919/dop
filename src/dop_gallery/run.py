import csv
import os
import re

from pyproj import Transformer

from . import geocode, render, tiles


def make_slug(zip_code, city, street, house_number):
    raw = f"{zip_code}-{city}-{street}-{house_number}"
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower().translate(geocode.UMLAUTS)).strip("-")
    return slug or "address"


def read_addresses(path, col_street, col_house_number, col_zip, col_city):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [
            name
            for name in (col_street, col_house_number, col_zip, col_city)
            if name not in (reader.fieldnames or [])
        ]
        if missing:
            raise SystemExit(f"error: CSV is missing column(s): {', '.join(missing)}")
        rows = []
        for row in reader:
            rows.append(
                {
                    "street": (row.get(col_street) or "").strip(),
                    "house_number": (row.get(col_house_number) or "").strip(),
                    "zip": (row.get(col_zip) or "").strip(),
                    "city": (row.get(col_city) or "").strip(),
                }
            )
    return rows


def load_manifest(data_dir):
    manifest = {}
    path = os.path.join(data_dir, "tiles_manifest.csv")
    if not os.path.exists(path):
        return manifest
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            manifest[row["kachel"]] = row.get("flight_date", "")
    return manifest


def run_gallery(args):
    data_dir = args.data_dir
    db_path = os.path.join(data_dir, "addresses.db")
    tile_dir = os.path.join(data_dir, "tiles")
    if not os.path.exists(db_path):
        raise SystemExit(f"error: {db_path} not found - run 'dop-gallery stage' first")
    if not os.path.isdir(tile_dir):
        raise SystemExit(f"error: {tile_dir} not found - run 'dop-gallery stage' first")

    rows = read_addresses(args.addresses, args.col_street, args.col_house_number, args.col_zip, args.col_city)
    manifest = load_manifest(data_dir)
    images_dir = os.path.join(args.out, "images")
    os.makedirs(images_dir, exist_ok=True)

    to_wgs84 = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)
    entries = []
    unresolved = []
    for row in rows:
        address = f"{row['street']} {row['house_number']}, {row['zip']} {row['city']}"
        status, result = geocode.lookup_address(db_path, row["city"], row["street"], row["house_number"])
        if status != "ok":
            reason = "keine passende Adresse gefunden" if status == "unmatched" else f"mehrdeutig ({len(result)} Kandidaten)"
            unresolved.append((address, reason))
            continue
        x, y = result
        try:
            arr = tiles.cutout(tile_dir, x, y)
        except tiles.MissingTileError as exc:
            unresolved.append((address, f"Kachel {exc} fehlt"))
            continue
        slug = make_slug(row["zip"], row["city"], row["street"], row["house_number"])
        img_name = f"{slug}.jpg"
        tiles.write_jpeg(arr, os.path.join(images_dir, img_name))
        lon, lat = to_wgs84.transform(x, y)
        tile = tiles.point_kachel(x, y)
        entries.append(
            {
                "address": address,
                "img": f"images/{img_name}",
                "x": x,
                "y": y,
                "lon": lon,
                "lat": lat,
                "flight_date": manifest.get(tile, ""),
                "tile": tile,
            }
        )

    index = render.render_gallery(entries, unresolved, args.out)
    print(f"gallery written to {index}")
    print(f"resolved: {len(entries)}, unresolved: {len(unresolved)}")
    return 0
