import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from dop_gallery import tiles


def make_tile(path, e_km, n_km, res, value):
    cell = 1000.0
    size = int(cell / res)
    arr = np.full((3, size, size), value, dtype="uint8")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=size,
        width=size,
        count=3,
        dtype="uint8",
        crs="EPSG:25832",
        transform=from_origin(e_km * cell, (n_km + 1) * cell, res, res),
    ) as dst:
        dst.write(arr)


def test_kachel_cells_inside_one_cell():
    cells = tiles.kachel_cells(356548.89, 5645282.84, half=50.0)
    assert cells == [(356, 5645)]


def test_kachel_cells_crossing_boundary():
    cells = tiles.kachel_cells(356990.0, 5645990.0, half=50.0)
    assert sorted(cells) == [(356, 5645), (356, 5646), (357, 5645), (357, 5646)]


def test_cutout_single_tile(tmp_path):
    tile_dir = tmp_path / "tiles"
    tile_dir.mkdir()
    make_tile(tile_dir / "32_356_5645.tif", 356, 5645, res=1.0, value=200)
    x, y = 356500.0, 5645500.0
    arr = tiles.cutout(str(tile_dir), x, y, half=50.0)
    assert arr.shape == (100, 100, 3)
    assert (arr == 200).all()


def test_cutout_mosaics_across_boundary(tmp_path):
    tile_dir = tmp_path / "tiles"
    tile_dir.mkdir()
    make_tile(tile_dir / "32_356_5645.tif", 356, 5645, res=1.0, value=10)
    make_tile(tile_dir / "32_357_5645.tif", 357, 5645, res=1.0, value=20)
    x, y = 356990.0, 5645500.0
    arr = tiles.cutout(str(tile_dir), x, y, half=50.0)
    assert arr.shape == (100, 100, 3)
    assert (arr[:, :60, :] == 10).all()
    assert (arr[:, 60:, :] == 20).all()


def test_cutout_missing_tile_raises(tmp_path):
    with pytest.raises(tiles.MissingTileError):
        tiles.cutout(str(tmp_path), 356500.0, 5645500.0, half=50.0)


def test_write_jpeg_roundtrip(tmp_path):
    arr = np.zeros((100, 100, 3), dtype="uint8")
    arr[:, :, 0] = 255
    out = tmp_path / "img" / "test.jpg"
    tiles.write_jpeg(arr, str(out))
    with rasterio.open(str(out)) as src:
        assert src.width == 100 and src.height == 100 and src.count == 3
        data = src.read()
    assert data[0].mean() > 200
