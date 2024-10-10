from pathlib import Path

import geopandas as gpd


def process_geodatabase(path_gdb: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(path_gdb)
