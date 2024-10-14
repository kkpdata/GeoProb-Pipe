from pathlib import Path
from typing import Optional

import geopandas as gpd


def process_geodatabase(path_gdb: Path, layer_name: Optional[str] = None) -> gpd.GeoDataFrame:
    return gpd.read_file(path_gdb, layer=layer_name)
