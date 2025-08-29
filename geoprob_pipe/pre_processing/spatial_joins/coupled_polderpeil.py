"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen HRD en uittredepunten.
"""

from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pathlib import Path
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


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

    # Store back in geopackage
    gdf_new_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Polderpeil is nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
