from __future__ import annotations
from geopandas import GeoDataFrame, points_from_xy
from pandas import DataFrame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _get_uittredepunten_gdf_beta_results(
        geoprob_pipe: GeoProbPipe, df_betas: DataFrame
) -> GeoDataFrame:

    # Gather uittredepunten coord values
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_coords = df_uittredepunten[["uittredepunt_id", "uittredepunt_x_coord", "uittredepunt_y_coord"]]

    # Merge coord values to limit state dataframe
    df = df_betas.merge(df_coords, left_on="uittredepunt_id", right_on="uittredepunt_id")

    # Create GeoDataFrame
    gdf = GeoDataFrame(
        df, geometry=points_from_xy(df['uittredepunt_x_coord'], df['uittredepunt_y_coord']), crs='EPSG:28992')
    return gdf.drop(columns=['uittredepunt_x_coord', 'uittredepunt_y_coord'])


def get_gdf_beta_limit_states(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_limit_states)
    if export:
        gdf.to_file(geoprob_pipe.spatial.export_path_geopackage, layer="beta_limit_states", driver="GPKG")
    return gdf


def get_gdf_beta_scenarios(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_scenarios)
    if export:
        gdf.to_file(geoprob_pipe.spatial.export_path_geopackage, layer="beta_scenarios", driver="GPKG")
    return gdf


def get_gdf_beta_uittredepunten(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_uittredepunten)
    if export:
        gdf.to_file(geoprob_pipe.spatial.export_path_geopackage, layer="beta_uittredepunten", driver="GPKG")
    return gdf
