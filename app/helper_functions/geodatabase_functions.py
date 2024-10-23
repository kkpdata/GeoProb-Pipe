from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge


# FIXME geom_type=Table (i.e. attribute table without geometries) is niet helemaal logisch, checken/aanpassen
def process_geodatabase(path_gdb: Path, layer_name: str, geom_type: str) -> gpd.GeoDataFrame | pd.DataFrame:

    gdf = gpd.read_file(path_gdb, layer=layer_name)

    # Checks
    if not geom_type == "Table":
        check_geodatabase_geometry_type(gdf, geom_type)
        check_coordinate_reference_system(gdf)

    if geom_type == "LineString":
        gdf = merge_segmented_lines_to_continous_polyline(gdf)

    return gdf


def check_geodatabase_geometry_type(gdf: gpd.GeoDataFrame, geometry_type: str) -> None:

    if geometry_type == "point":
        check_type = ["Point"]
    elif geometry_type == "line":
        check_type = ["LineString", "MultiLineString"]
    elif geometry_type == "polygon":
        check_type = ["Polygon"]
    else:
        raise ValueError(f"Invalid geometry type '{geometry_type}'. Use 'point', 'line', or 'polygon'")

    if not gdf.geometry.geom_type.eq(lambda check_geom: check_geom in check_type).all():
        raise ValueError(f"Not all geometries are of type {geometry_type}")


def check_coordinate_reference_system(gdf: gpd.GeoDataFrame) -> None:

    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no coordinate reference system (CRS) defined.")
    elif gdf.crs.to_epsg() != 28992:
        raise ValueError(
            f"GeoDataFrame coordinate reference system (CRS) is {gdf.crs.to_epsg()}, but EPSG:28992 (RD New) is required."
        )


# TODO dit hieronder werkt wat betreft de geometries, maar wat als de rijen die gemerged worden verschillende attribute table data bevatten?
def merge_segmented_lines_into_contiguous_polyline(
    gdf: gpd.GeoDataFrame, buffer_distance: float = 0.1
) -> gpd.GeoDataFrame:

    # Create a buffer around each MultiLineString
    gdf["buffered"] = gdf.geometry.buffer(buffer_distance)

    merged_geometries = []
    merged_indices = set()

    # Iterate through each geometry in the GeoDataFrame
    for idx, row in gdf.items():
        if idx in merged_indices:
            continue  # Skip already merged geometries

        current_geom = row.geometry
        current_buffer = row["buffered"]

        # Find all overlapping geometries and drop buffered geometry
        overlapping_lines = gdf[gdf.buffered.intersects(current_buffer)]
        gdf.drop(columns=["buffered"], inplace=True)

        # Collect lines to merge
        lines_to_merge = []
        for geom in overlapping_lines.geometry:
            # If it is MultiLineString, extend the list with its individual LineStrings
            if isinstance(geom, MultiLineString):
                # Add all LineStrings from the MultiLineString
                lines_to_merge.extend(list(geom.geoms))
            elif isinstance(geom, LineString):
                lines_to_merge.append(geom)  # Add LineString directly

        # Merge the collected lines
        if lines_to_merge:
            merged = linemerge(lines_to_merge)  # Merge the lines
            # Append the merged geometry, converting to MultiLineString if needed
            if isinstance(merged, LineString):
                merged_geometries.append(MultiLineString([merged]))  # Wrap LineString in MultiLineString
            elif isinstance(merged, MultiLineString):
                merged_geometries.append(merged)  # Directly append MultiLineString
            else:
                merged_geometries.append(MultiLineString([]))  # Handle empty case

            # Mark these indices as merged
            merged_indices.update(overlapping_lines.index)

    # Create a GeoDataFrame with merged geometries
    merged_gdf = gpd.GeoDataFrame(geometry=merged_geometries).drop_duplicates().reset_index(drop=True)

    return merged_gdf
