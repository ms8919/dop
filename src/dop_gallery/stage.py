import csv
import os
import re
import tempfile

import requests

from . import geocode, tiles
from .run import read_addresses

DOP_INDEX_URL = "https://www.opengeodata.nrw.de/produkte/geobasis/lusat/akt/dop/dop_jp2_f10/index.json"
DOP_BASE_URL = "https://www.opengeodata.nrw.de/produkte/geobasis/lusat/akt/dop/dop_jp2_f10/"
WMS_URL = "https://www.wms.nrw.de/geobasis/wms_nw_dop"
WMS_INFO_LAYER = "nw_dop_utm_info"

TILE_NAME_RE = re.compile(r"dop10rgbi_(\d+)_(\d+)_(\d+)_\d+_nw_(\d+)\.jp2")


def download(url, dest, session):
    with session.get(url, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)


def ensure_address_db(data_dir, session):
    db_path = os.path.join(data_dir, "addresses.db")
    if os.path.exists(db_path):
        return db_path
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "gebref.zip")
        print(f"downloading address data (Gebäudereferenzen NW, ~97 MB) ...")
        download(geocode.GEBREF_ZIP_URL, zip_path, session)
        print("building local address database ...")
        count = geocode.build_address_db(zip_path, db_path)
    print(f"address database ready: {count} address points")
    return db_path


def flight_date_for_kachel(session, easting_km, northing_km):
    x = easting_km * 1000 + 500
    y = northing_km * 1000 + 500
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": WMS_INFO_LAYER,
        "QUERY_LAYERS": WMS_INFO_LAYER,
        "CRS": "EPSG:25832",
        "BBOX": f"{x - 1},{y - 1},{x + 1},{y + 1}",
        "WIDTH": 10,
        "HEIGHT": 10,
        "I": 5,
        "J": 5,
        "FORMAT": "image/png",
        "INFO_FORMAT": "text/plain",
        "FEATURE_COUNT": 1,
    }
    resp = session.get(WMS_URL, params=params, timeout=60)
    text = resp.text
    date = re.search(r"Bildflugdatum\s*=\s*'([^']*)'", text)
    return date.group(1) if date else ""


def load_tile_index(session):
    resp = session.get(DOP_INDEX_URL, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    mapping = {}
    for dataset in data.get("datasets", []):
        for f in dataset.get("files", []):
            m = TILE_NAME_RE.match(f["name"])
            if m:
                zone, e, n, year = m.groups()
                key = f"{zone}_{e}_{n}"
                if key not in mapping or year > mapping[key][1]:
                    mapping[key] = (f["name"], year)
    return mapping


def run_stage(args):
    data_dir = args.data_dir
    tile_dir = os.path.join(data_dir, "tiles")
    os.makedirs(tile_dir, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "dop-gallery/0.1 (open data staging)"

    db_path = ensure_address_db(data_dir, session)
    rows = read_addresses(args.addresses, args.col_street, args.col_house_number, args.col_zip, args.col_city)

    cells = set()
    unresolved = 0
    for row in rows:
        status, result = geocode.lookup_address(db_path, row["city"], row["street"], row["house_number"])
        if status != "ok":
            unresolved += 1
            continue
        x, y = result
        cells.update(tiles.kachel_cells(x, y))
    print(f"geocoded {len(rows) - unresolved}/{len(rows)} addresses, {len(cells)} DOP tiles needed")

    tile_index = load_tile_index(session)
    manifest_path = os.path.join(data_dir, "tiles_manifest.csv")
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["kachel", "flight_date", "year", "file"])
        for e, n in sorted(cells):
            kachel = tiles.kachel_name(e, n)
            if kachel not in tile_index:
                print(f"warning: no DOP tile listed for {kachel}")
                continue
            file_name, year = tile_index[kachel]
            dest = os.path.join(tile_dir, kachel + ".jp2")
            if not os.path.exists(dest):
                print(f"downloading {file_name} ...")
                download(DOP_BASE_URL + file_name, dest, session)
            flight = flight_date_for_kachel(session, e, n)
            writer.writerow([kachel, flight, year, file_name])
    print(f"stage complete: {len(cells)} tiles in {tile_dir}, manifest at {manifest_path}")
    return 0
