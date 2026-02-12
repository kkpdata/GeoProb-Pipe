from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pandas import DataFrame, read_sql_query
import sqlite3
from geoprob_pipe.cmd_app.spatial_joins.utils import append_to_gis_join_parameter_invoer_table
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_mv_exit_to_gis_parameter_invoer_table(app_settings: ApplicationSettings) -> bool:

    # Check if already added, if so skip
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df_existing = read_sql_query("SELECT * FROM gis_join_parameter_invoer;", conn)
    if "mv_exit" in df_existing['parameter'].unique():
        return True

    # Getting necessary GeoDataframes
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    # Append to new version of geospatial storage
    df_to_append: DataFrame = gdf_exit_points[["mv_exit", "uittredepunt_id"]]
    df_to_append = df_to_append.rename(columns={"mv_exit": "mean"})
    append_to_gis_join_parameter_invoer_table(
        df_sjoin=df_to_append,
        parameter_name="mv_exit",
        geopackage_filepath=app_settings.geopackage_filepath)

    return True
