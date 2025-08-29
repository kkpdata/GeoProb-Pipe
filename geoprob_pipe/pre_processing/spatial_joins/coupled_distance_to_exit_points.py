"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen intrede en uittredepunten.
"""

from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pathlib import Path
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def coupled_distances_to_uittredepunten(app_settings: ApplicationSettings) -> bool:

    # Read uittredepunten
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    # Check if already added
    columns = gdf_exit_points.columns
    if "afstand_intredelijn" in columns and "afstand_buitenteenlijn" in columns and "afstand_binnenteenlijn" in columns:
        print(BColors.OKBLUE,
              f"✔  Afstanden intrede, buitenteen en binnenteen al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added

    # Distance to intredelijn
    gdf_intredelijnen: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="intredelijn")
    gdf_exit_points['afstand_intredelijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_intredelijnen.distance(pnt).min(), 1))

    # Distance to buitenteenlijn
    gdf_buitenteenlijnen: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="buitenteenlijn")
    gdf_exit_points['afstand_buitenteenlijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_buitenteenlijnen.distance(pnt).min(), 1))

    # Distance to binnenteenlijn
    gdf_binnenteenlijn: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="binnenteenlijn")
    gdf_exit_points['afstand_binnenteenlijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_binnenteenlijn.distance(pnt).min(), 1))

    # Store back in geopackage
    gdf_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE,
          f"✅  Afstanden intrede, buitenteen en binnenteen zijn nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
