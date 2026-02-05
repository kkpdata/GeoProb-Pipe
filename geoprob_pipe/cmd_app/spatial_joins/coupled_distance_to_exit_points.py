"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen intrede en uittredepunten.
"""

from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pathlib import Path
from geoprob_pipe.cmd_app.spatial_joins.utils import append_to_gis_join_parameter_invoer_table
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_distances_to_uittredepunten(app_settings: ApplicationSettings) -> bool:

    # Read uittredepunten
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    # Check if already added
    columns = gdf_exit_points.columns
    if "afstand_intredelijn" in columns and "afstand_buitenteenlijn" in columns and "afstand_binnenteenlijn" in columns:
        print(BColors.OKBLUE,
              f"✔  Afstanden intrede, buitenteen en binnenteen al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added
    # TODO: Uitfaseren dat deze kolommen gekoppeld worden aan de exit_points tabel

    # Distance to intredelijn
    gdf_intredelijnen: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="intredelijn")
    gdf_exit_points['afstand_intredelijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_intredelijnen.distance(pnt).min(), 1))
    df_l_intrede = gdf_exit_points[["uittredepunt_id", "afstand_intredelijn"]]
    df_l_intrede = df_l_intrede.rename(columns={"afstand_intredelijn": "mean"})
    append_to_gis_join_parameter_invoer_table(
        df_sjoin=df_l_intrede, parameter_name="L_intrede", geopackage_filepath=app_settings.geopackage_filepath)

    # Distance to buitenteenlijn
    gdf_buitenteenlijnen: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="buitenteenlijn")
    gdf_exit_points['afstand_buitenteenlijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_buitenteenlijnen.distance(pnt).min(), 1))
    df_l_but = gdf_exit_points[["uittredepunt_id", "afstand_buitenteenlijn"]]
    df_l_but = df_l_but.rename(columns={"afstand_buitenteenlijn": "mean"})
    append_to_gis_join_parameter_invoer_table(
        df_sjoin=df_l_but, parameter_name="L_but", geopackage_filepath=app_settings.geopackage_filepath)

    # Distance to binnenteenlijn
    gdf_binnenteenlijn: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="binnenteenlijn")
    gdf_exit_points['afstand_binnenteenlijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_binnenteenlijn.distance(pnt).min(), 1))
    df_l_intrede = gdf_exit_points[["uittredepunt_id", "afstand_binnenteenlijn"]]
    df_l_intrede = df_l_intrede.rename(columns={"afstand_binnenteenlijn": "mean"})
    append_to_gis_join_parameter_invoer_table(
        df_sjoin=df_l_intrede, parameter_name="L_bit", geopackage_filepath=app_settings.geopackage_filepath)

    # Store back in geopackage
    gdf_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE,
          f"✅  Afstanden intrede, buitenteen en binnenteen zijn nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
