import os
import re
import sqlite3
import zipfile

GEBREF_ZIP_URL = "https://www.opengeodata.nrw.de/produkte/geobasis/lk/akt/gebref_txt/gebref_EPSG25832_ASCII.zip"

UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

STREET_TOKEN_MAP = {"str": "strasse", "pl": "platz", "strasse": "strasse", "platz": "platz"}


def normalize_text(value):
    if value is None:
        return ""
    s = str(value).strip().lower().translate(UMLAUTS)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def normalize_street(value):
    tokens = []
    for token in normalize_text(value).split():
        if token in STREET_TOKEN_MAP:
            token = STREET_TOKEN_MAP[token]
        elif token.endswith("str") and len(token) > 3:
            token = token[:-3] + "strasse"
        tokens.append(token)
    return " ".join(tokens)


def normalize_house_number(number, suffix=""):
    return (normalize_text(number) + normalize_text(suffix)).replace(" ", "")


def parse_gebref_line(line):
    fields = line.rstrip("\r\n").split(";")
    if len(fields) < 20 or fields[0] != "N":
        return None
    try:
        x = float(fields[18])
        y = float(fields[19])
    except ValueError:
        return None
    return {
        "city": normalize_text(fields[10]),
        "street": normalize_street(fields[14]),
        "hn": normalize_house_number(fields[15], fields[16]),
        "x": x,
        "y": y,
    }


def build_address_db(source, db_path):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE addresses (city TEXT NOT NULL, street TEXT NOT NULL, hn TEXT NOT NULL, x REAL NOT NULL, y REAL NOT NULL)"
    )
    batch = []

    def flush():
        conn.executemany("INSERT INTO addresses VALUES (?, ?, ?, ?, ?)", batch)
        batch.clear()

    if source.endswith(".zip"):
        with zipfile.ZipFile(source) as z:
            name = next(n for n in z.namelist() if n.endswith(".txt") and "anzahl" not in n)
            with z.open(name) as f:
                for raw in f:
                    rec = parse_gebref_line(raw.decode("utf-8", errors="replace"))
                    if rec:
                        batch.append((rec["city"], rec["street"], rec["hn"], rec["x"], rec["y"]))
                    if len(batch) >= 50000:
                        flush()
    else:
        with open(source, encoding="utf-8", errors="replace") as f:
            for raw in f:
                rec = parse_gebref_line(raw)
                if rec:
                    batch.append((rec["city"], rec["street"], rec["hn"], rec["x"], rec["y"]))
                if len(batch) >= 50000:
                    flush()
    flush()
    conn.execute("CREATE INDEX idx_addr ON addresses (city, street, hn)")
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]
    conn.close()
    return count


def lookup_address(db_path, city, street, house_number, suffix=""):
    key_city = normalize_text(city)
    key_street = normalize_street(street)
    key_hn = normalize_house_number(house_number, suffix)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT x, y FROM addresses WHERE city = ? AND street = ? AND hn = ?",
        (key_city, key_street, key_hn),
    ).fetchall()
    conn.close()
    coords = sorted(set((round(x, 3), round(y, 3)) for x, y in rows))
    if not coords:
        return "unmatched", []
    if len(coords) == 1:
        return "ok", coords[0]
    return "ambiguous", coords
