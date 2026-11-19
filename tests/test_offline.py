import ast
import os
import socket

import pytest

SRC = os.path.join(os.path.dirname(__file__), "..", "src", "dop_gallery")
OFFLINE_MODULES = ["__init__.py", "__main__.py", "cli.py", "run.py", "geocode.py", "tiles.py", "render.py"]


def test_run_path_never_imports_requests():
    for name in OFFLINE_MODULES:
        tree = ast.parse(open(os.path.join(SRC, name), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] != "requests" for alias in node.names), name
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] != "requests", name


def test_run_works_with_network_disabled(tmp_path, monkeypatch):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    from dop_gallery import geocode, run

    tile_dir = tmp_path / "data" / "tiles"
    tile_dir.mkdir(parents=True)
    size = 10000
    arr = np.zeros((4, size, size), dtype="uint8")
    with rasterio.open(
        tile_dir / "32_356_5645.jp2",
        "w",
        driver="JP2OpenJPEG",
        height=size,
        width=size,
        count=4,
        dtype="uint8",
        crs="EPSG:25832",
        transform=from_origin(356000.0, 5646000.0, 0.1, 0.1),
    ) as dst:
        dst.write(arr)

    txt = tmp_path / "gebref.txt"
    txt.write_text(
        "N;ID1;A;05;NRW;7;Köln;05;Köln;000;Köln;0000;;01001;Domkloster;4;;32;356548.890;5645282.840;2026-07-01\n",
        encoding="utf-8",
    )
    geocode.build_address_db(str(txt), str(tmp_path / "data" / "addresses.db"))
    with open(tmp_path / "data" / "tiles_manifest.csv", "w", encoding="utf-8") as f:
        f.write("kachel,flight_date,year,file\n32_356_5645,11.05.2025,2025,x.jp2\n")

    csv_path = tmp_path / "addresses.csv"
    csv_path.write_text("street,house_number,zip,city\nDomkloster,4,50667,Köln\n", encoding="utf-8")

    def no_network(*args, **kwargs):
        raise AssertionError("network access attempted during offline run")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)

    class Args:
        addresses = str(csv_path)
        data_dir = str(tmp_path / "data")
        out = str(tmp_path / "out")
        col_street = "street"
        col_house_number = "house_number"
        col_zip = "zip"
        col_city = "city"

    assert run.run_gallery(Args) == 0
    index = tmp_path / "out" / "index.html"
    assert index.exists()
    page = index.read_text(encoding="utf-8")
    assert "Domkloster 4, 50667 Köln" in page
    assert "11.05.2025" in page
    assert "Datenlizenz Deutschland" in page
    imgs = list((tmp_path / "out" / "images").glob("*.jpg"))
    assert len(imgs) == 1
    with rasterio.open(str(imgs[0])) as src:
        assert src.width == 2000 and src.height == 2000
