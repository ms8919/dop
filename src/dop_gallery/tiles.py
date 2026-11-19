import math
import os

import numpy as np
import rasterio
from rasterio.windows import Window

CELL_M = 1000.0
CUTOUT_M = 200.0
TILE_EXTENSIONS = (".jp2", ".tif", ".tiff")


class MissingTileError(Exception):
    pass


def kachel_cells(x, y, half=CUTOUT_M / 2.0, cell=CELL_M):
    e0 = math.floor((x - half) / cell)
    e1 = math.floor((x + half - 1e-6) / cell)
    n0 = math.floor((y - half) / cell)
    n1 = math.floor((y + half - 1e-6) / cell)
    return [(e, n) for e in range(e0, e1 + 1) for n in range(n0, n1 + 1)]


def kachel_name(easting_km, northing_km):
    return f"32_{easting_km}_{northing_km}"


def point_kachel(x, y, cell=CELL_M):
    return kachel_name(math.floor(x / cell), math.floor(y / cell))


def tile_path(tile_dir, easting_km, northing_km):
    name = kachel_name(easting_km, northing_km)
    for ext in TILE_EXTENSIONS:
        candidate = os.path.join(tile_dir, name + ext)
        if os.path.exists(candidate):
            return candidate
    return None


def cutout(tile_dir, x, y, half=CUTOUT_M / 2.0, cell=CELL_M):
    cells = kachel_cells(x, y, half, cell)
    paths = []
    for e, n in cells:
        path = tile_path(tile_dir, e, n)
        if path is None:
            raise MissingTileError(kachel_name(e, n))
        paths.append(((e, n), path))
    with rasterio.open(paths[0][1]) as src:
        res = src.res[0]
    size = int(round(2 * half / res))
    out = np.zeros((size, size, 3), dtype="uint8")
    box_left, box_right = x - half, x + half
    box_bottom, box_top = y - half, y + half
    for (e, n), path in paths:
        tile_left, tile_right = e * cell, (e + 1) * cell
        tile_bottom, tile_top = n * cell, (n + 1) * cell
        left = max(box_left, tile_left)
        right = min(box_right, tile_right)
        bottom = max(box_bottom, tile_bottom)
        top = min(box_top, tile_top)
        if right <= left or top <= bottom:
            continue
        with rasterio.open(path) as src:
            col0 = int(round((left - tile_left) / res))
            row0 = int(round((tile_top - top) / res))
            w = int(round((right - left) / res))
            h = int(round((top - bottom) / res))
            data = src.read([1, 2, 3], window=Window(col0, row0, w, h))
        out_col = int(round((left - box_left) / res))
        out_row = int(round((box_top - top) / res))
        out[out_row : out_row + h, out_col : out_col + w, :] = np.moveaxis(data, 0, -1)
    return out


def write_jpeg(arr, path, quality=90):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    height, width = arr.shape[:2]
    with rasterio.open(
        path,
        "w",
        driver="JPEG",
        height=height,
        width=width,
        count=3,
        dtype="uint8",
        options={"QUALITY": str(quality)},
    ) as dst:
        dst.write(np.moveaxis(arr, -1, 0))
