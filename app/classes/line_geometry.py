from pathlib import Path

import geopandas as gpd

from app.helper_functions.geodatabase_functions import process_geodatabase


class LineGeometry:

    def __init__(self, path_gdb: Path, layer_name: str) -> None:

        # TODO check: maakt het uit in welke richting de keringslijnen lopen? Zo ja: checks inbouwen
        self.gdf = process_geodatabase(path_gdb, layer_name=layer_name, geom_type="line")

        if self.gdf.empty:
            raise ValueError(
                f"Feature class '{layer_name}' in '{path_gdb.name}' should contain at least one line geometry'"
            )
