from __future__ import annotations
from geopandas import GeoDataFrame
from pandas import DataFrame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _get_uittredepunten_gdf_beta_results(geoprob_pipe: GeoProbPipe, df_betas: DataFrame) -> GeoDataFrame:

    # Gather uittredepunten coord values
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    gdf_coords = gdf_uittredepunten[["uittredepunt_id", "geometry"]]

    # Merge coord values to limit state dataframe
    df_merged = df_betas.merge(gdf_coords, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return GeoDataFrame(df_merged, geometry="geometry", crs=gdf_uittredepunten.crs)


def get_gdf_beta_limit_states(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_limit_states)
    if export:
        gdf.to_file(geoprob_pipe.input_data.app_settings.geopackage_filepath,
                    layer="beta_limit_states", driver="GPKG", mode="w")
    return gdf


def get_gdf_beta_scenarios(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_scenarios)
    if export:
        gdf.to_file(
            geoprob_pipe.input_data.app_settings.geopackage_filepath,
            layer="beta_scenarios", driver="GPKG", mode="w")
    return gdf


def get_gdf_beta_uittredepunten(geoprob_pipe: GeoProbPipe, export: bool = False) -> GeoDataFrame:
    gdf = _get_uittredepunten_gdf_beta_results(geoprob_pipe, geoprob_pipe.results.df_beta_uittredepunten)
    if export:
        gdf.to_file(
            geoprob_pipe.input_data.app_settings.geopackage_filepath,
            layer="beta_uittredepunten", driver="GPKG", mode="w")
    return gdf
