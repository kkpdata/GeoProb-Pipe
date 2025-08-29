from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.utils.validation_messages import BColors
from geopandas import GeoDataFrame, read_file
from pathlib import Path
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def coupled_uittredepunten_to_vakken(app_settings: ApplicationSettings) -> bool:

    # Read uittredepunten
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    # Check if already added
    if "vak_id" in gdf_exit_points.columns:
        print(BColors.OKBLUE, f"✔  Vakken al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added

    # Spatial analyses
    gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
    gdf_exit_points_with_vakken = gdf_exit_points.sjoin_nearest(
        gdf_vakindeling[['geometry', 'id']], how='left', distance_col='distance')

    # Define which columns to keep (after spatial join)
    columns_to_keep = list(gdf_exit_points.columns)
    columns_to_keep.append("id")
    gdf_new_exit_points = gdf_exit_points_with_vakken[columns_to_keep]
    gdf_new_exit_points = gdf_new_exit_points.rename(columns={"id": "vak_id"})

    # Store back in geopackage
    gdf_new_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Vakken zijn nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
