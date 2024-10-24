from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge


# FIXME geom_type=Table (i.e. attribute table without geometries) is niet helemaal logisch, checken/aanpassen
def process_geodatabase(path_gdb: Path, layer_name: str, geom_type: str) -> gpd.GeoDataFrame | pd.DataFrame:

    gdf = gpd.read_file(path_gdb, layer=layer_name)

    # Checks
    if not geom_type == "table":
        check_geodatabase_geometry_type(path_gdb.name, layer_name, gdf, geom_type)
        check_coordinate_reference_system(path_gdb.name, layer_name, gdf)

    if geom_type in ["LineString", "MultiLineString"]:
        gdf.geometry = merge_lines(gdf.geometry)

    return gdf


def check_geodatabase_geometry_type(name_gdb: str, layer_name: str, gdf: gpd.GeoDataFrame, geometry_type: str) -> None:

    if geometry_type == "point":
        list_check_type = ["Point"]
    elif geometry_type == "line":
        list_check_type = ["LineString", "MultiLineString"]
    elif geometry_type == "polygon":
        list_check_type = ["Polygon"]
    else:
        raise ValueError(f"Invalid geometry type given ('{geometry_type}'). Use 'point', 'line', or 'polygon'")

    if not all(geom_type in ["LineString", "MultiLineString"] for geom_type in gdf.geometry.geom_type.unique()):
        raise ValueError(
            f"Not all geometries of feature class '{layer_name}' in '{name_gdb}' are of type {geometry_type}. Found geometry types: {gdf.geometry.geom_type}"
        )


def check_coordinate_reference_system(name_gdb: str, layer_name: str, gdf: gpd.GeoDataFrame) -> None:

    if gdf.crs is None:
        raise ValueError(
            f"Feature class '{layer_name}' in '{name_gdb}' has no coordinate reference system (CRS) defined."
        )
    elif gdf.crs.to_epsg() != 28992:
        raise ValueError(
            f"Feature class '{layer_name}' in '{name_gdb}' has coordinate reference system (CRS) code EPSG:{gdf.crs.to_epsg()}, but EPSG:28992 (RD New) is required."
        )


def merge_lines(geometry_geoseries: gpd.GeoSeries) -> gpd.GeoSeries:
    """If a MultiLineString consists of connected lines (e.g. end point of line 1 is the start point of line 2), merge them into one line.
    Parameter directed=True so lines that are directed in different directions will not be merged; only lines that are pointing in the same direction.

    Examples (x indicates the line start/end points):
        ----> x ----> lines are pointing in same direction so will be merged
        <---- x ----> will not be merged because of different directions
        ----> x <---- will not be merged because of different directions

    Args:
        geometry_geoseries (gpd.GeoSeries): LineString and/or MultiLineString geometries

    Returns:
        gpd.GeoSeries: LineString geometries (merged from MultiLineStrings) and/or MultiLineStrings (if the lines of the MultiLineString are pointing in different directions)
    """
    return geometry_geoseries.apply(lambda geom: linemerge(geom, directed=True))
