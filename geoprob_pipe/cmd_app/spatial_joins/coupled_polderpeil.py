"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen HRD en uittredepunten.
"""

from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pathlib import Path
from pandas import DataFrame
from geoprob_pipe.cmd_app.spatial_joins.utils import append_to_gis_join_parameter_invoer_table
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_polderpeil_to_uittredepunten(app_settings: ApplicationSettings) -> bool:


    # Getting necessary GeoDataframes
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")
    gdf_polderpeil: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="polderpeil")

    # Check if already added
    if "polderpeil" in gdf_exit_points.columns:
        print(BColors.OKBLUE, f"✔  Polderpeil al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added

    # Perform spatial join to find the nearest HRD-location for each Exit Point
    gdf_exit_with_hrd = gdf_exit_points.sjoin_nearest(
        gdf_polderpeil[['geometry', 'polderpeil']], how='left', distance_col='distance')

    # Define which columns to keep (after spatial join)
    columns_to_keep = list(gdf_exit_points.columns)
    columns_to_keep.append("polderpeil")
    gdf_new_exit_points = gdf_exit_with_hrd[columns_to_keep]

    # Append to new version of geospatial storage
    df_to_append: DataFrame = gdf_new_exit_points[["polderpeil", "uittredepunt_id"]]
    df_to_append = df_to_append.rename(columns={"polderpeil": "mean"})
    append_to_gis_join_parameter_invoer_table(
        df_sjoin=df_to_append,
        parameter_name="polderpeil",
        geopackage_filepath=app_settings.geopackage_filepath)

    # Store back in geopackage
    gdf_new_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    # TODO: Uitfaseren deze oude manier van polderpeil opslaan
    print(BColors.OKBLUE, f"✅  Polderpeil is nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
