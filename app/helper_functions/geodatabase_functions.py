from pathlib import Path

import geopandas as gpd
import pandas as pd


# FIXME geom_type=Table is niet helemaal logisch, checken/aanpassen
def process_geodatabase(path_gdb: Path, layer_name: str, geom_type: str) -> gpd.GeoDataFrame | pd.DataFrame:

    gdf = gpd.read_file(path_gdb, layer=layer_name)

    # Checks
    if not geom_type == "Table":
        check_geodatabase_geometry_type(gdf, geom_type)

    return gdf


def check_geodatabase_geometry_type(gdf: gpd.GeoDataFrame, geom_type: str) -> bool:

    if geom_type not in ["Point", "LineString", "Polygon"]:
        raise ValueError(f"Invalid geometry type '{geom_type}'. Use 'Point', 'LineString', or 'Polygon'")

    return gdf.geometry.geom_type.eq(geom_type).all()
