"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen HRD en uittredepunten.
"""

from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pathlib import Path
# from geoprob_pipe.pre_processing.spatial_joins.utils import append_hrd_to_gis_join_parameter_invoer_table
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def coupled_hrd_to_uittredepunten(app_settings: ApplicationSettings) -> bool:

    # Getting necessary GeoDataframes
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")
    gdf_hrd_locations: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="hrd_locaties")

    # Check if already added
    if "hrd_name" in gdf_exit_points.columns:
        print(BColors.OKBLUE, f"✔  HRD-locaties al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added

    # Perform spatial join to find the nearest HRD-location for each Exit Point
    gdf_exit_with_hrd = gdf_exit_points.sjoin_nearest(
        gdf_hrd_locations[['geometry', 'location_name']], how='left', distance_col='distance')

    # Define which columns to keep (after spatial join)
    columns_to_keep = list(gdf_exit_points.columns)
    columns_to_keep.append("location_name")
    gdf_new_exit_points = gdf_exit_with_hrd[columns_to_keep]
    gdf_new_exit_points = gdf_new_exit_points.rename(columns={"location_name": "hrd_name"})
    # append_hrd_to_gis_join_parameter_invoer_table(
    #     df_sjoin=gdf_new_exit_points[["uittredepunt_id", "hrd_name"]],
    #     geopackage_filepath=app_settings.geopackage_filepath)
    # print(f"{gdf_new_exit_points.columns=}")

    # raise NotImplementedError

    # Store back in geopackage
    gdf_new_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    # TODO: Uitfaseren dat HRD-koppeling middels direct aan de geometrie van het uittredepunt zit.
    print(BColors.OKBLUE, f"✅  HRD-locaties zijn nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
