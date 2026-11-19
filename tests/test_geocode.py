import os
import sqlite3

from dop_gallery import geocode

SAMPLE_LINES = [
    "N;DENW01HK1;A;05;Nordrhein-Westfalen;9;Arnsberg;11;Bochum;000;Bochum;0000;;04086;Obertor;50;;32;370279.838;5705335.366;2026-07-01",
    "N;DENW01HK2;B;05;Nordrhein-Westfalen;9;Arnsberg;11;Bochum;000;Bochum;0000;;04176;Wilhelm-Leithe-Weg;76;a;32;370473.340;5703695.059;2026-07-01",
    "N;DENW01HK3;A;05;Nordrhein-Westfalen;9;Arnsberg;11;Bochum;000;Bochum;0000;;02787;Ückendorfer Str.;102;;32;369980.950;5705743.088;2026-07-01",
    "N;DENW01HK4;A;05;Nordrhein-Westfalen;9;Arnsberg;11;Bochum;000;Bochum;0000;;04105;Schlaraffiastr.;9;;32;370363.576;5703187.572;2026-07-01",
    "N;DENW01HK5;A;05;Nordrhein-Westfalen;7;Köln;05;Köln;000;Köln;0000;;01001;Domkloster;4;;32;356548.890;5645282.840;2026-07-01",
]


def write_db(tmp_path, lines):
    txt = tmp_path / "gebref.txt"
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    db = tmp_path / "addresses.db"
    geocode.build_address_db(str(txt), str(db))
    return str(db)


def test_normalize_text_umlauts_and_punctuation():
    assert geocode.normalize_text("Ückendorfer Str.") == "ueckendorfer str"
    assert geocode.normalize_text("Köln  Süd") == "koeln sued"
    assert geocode.normalize_text("Straße ß") == "strasse ss"


def test_normalize_street_abbreviations():
    assert geocode.normalize_street("Schlaraffiastr.") == "schlaraffiastrasse"
    assert geocode.normalize_street("Am Markt Pl.") == "am markt platz"
    assert geocode.normalize_street("Obertor") == "obertor"


def test_normalize_house_number():
    assert geocode.normalize_house_number("76", "a") == "76a"
    assert geocode.normalize_house_number("76 a") == "76a"
    assert geocode.normalize_house_number(" 50 ") == "50"


def test_lookup_exact_match(tmp_path):
    db = write_db(tmp_path, SAMPLE_LINES)
    status, res = geocode.lookup_address(db, "Köln", "Domkloster", "4")
    assert status == "ok"
    assert res == (356548.89, 5645282.84)


def test_lookup_umlaut_and_abbreviation_variant(tmp_path):
    db = write_db(tmp_path, SAMPLE_LINES)
    status, res = geocode.lookup_address(db, "Bochum", "Ückendorfer Straße", "102")
    assert status == "ok"
    assert res == (369980.95, 5705743.088)
    status, res = geocode.lookup_address(db, "Bochum", "Schlaraffiastr.", "9")
    assert status == "ok"


def test_lookup_house_number_suffix(tmp_path):
    db = write_db(tmp_path, SAMPLE_LINES)
    status, res = geocode.lookup_address(db, "Bochum", "Wilhelm-Leithe-Weg", "76a")
    assert status == "ok"
    assert res == (370473.34, 5703695.059)


def test_lookup_no_match(tmp_path):
    db = write_db(tmp_path, SAMPLE_LINES)
    status, res = geocode.lookup_address(db, "Nowhere", "Nirgendwo", "1")
    assert status == "unmatched"
    assert res == []


def test_lookup_ambiguous(tmp_path):
    lines = SAMPLE_LINES + [
        "N;DENW01HK6;A;05;NRW;9;Arnsberg;11;Bochum;000;Bochum;0000;;04086;Obertor;50;;32;370999.000;5705999.000;2026-07-01",
    ]
    db = write_db(tmp_path, lines)
    status, res = geocode.lookup_address(db, "Bochum", "Obertor", "50")
    assert status == "ambiguous"
    assert len(res) == 2


def test_parse_gebref_line_rejects_garbage():
    assert geocode.parse_gebref_line("hello world") is None
    assert geocode.parse_gebref_line("") is None
