"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen intrede en uittredepunten.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import fiona

from geoprob_pipe.cmd_app.spatial_joins.couple_objects.distance import (
    DistCouple,
)
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_distances_to_uittredepunten(
    app_settings: ApplicationSettings,
) -> bool:
    """
    Bepaal de afstanden tussen de uittredepunten en de intrede, binnenteen en
    buitenteenlijnen. Als deze er al in staan worden ze overschreven.

    :param app_settings: Object met de instellingen van de applicatie
    """    

    # Read uittredepunten
    gdf_exit_points: gpd.GeoDataFrame = gpd.read_file(
        app_settings.geopackage_filepath, layer="uittredepunten"
    )

    # Distance to intredelijn
    layers: list[str] = fiona.listlayers(app_settings.geopackage_filepath)
    for layer in layers:
        if "intredelijn" in layers:  # Een intredelijn voor alle scenarios
            gdf_intredelijnen: gpd.GeoDataFrame = gpd.read_file(
                app_settings.geopackage_filepath, layer="intredelijn"
            )
            gdf_exit_points["afstand_intredelijn"] = (
                gdf_exit_points.geometry.apply(
                    lambda pnt: round(gdf_intredelijnen.distance(pnt).min(), 1)
                )
            )
            df_l_intrede = gdf_exit_points[
                ["uittredepunt_id", "afstand_intredelijn"]
            ]
            df_l_intrede = df_l_intrede.rename(
                columns={"afstand_intredelijn": "L_intrede__mean"}
            )
            DistCouple(
                app_settings, "L_intrede", df_l_intrede
            ).couple_exit_points()

        # Intrede lijn per scenario        
        if len(layer.split("__")) == 2 and "intredelijn" in layer.split("__")[0]:
            gdf_intredelijnen: gpd.GeoDataFrame = gpd.read_file(
                app_settings.geopackage_filepath, layer=layer
            )
            gdf_exit_points["afstand_intredelijn"] = (
                gdf_exit_points.geometry.apply(
                    lambda pnt: round(
                        gdf_intredelijnen.distance(pnt).min(), 1
                    )
                )
            )
            df_l_intrede = gdf_exit_points[
                ["uittredepunt_id", "afstand_intredelijn"]
            ]
            df_l_intrede = df_l_intrede.rename(
                columns={"afstand_intredelijn": "L_intrede__mean"}
            )
            DistCouple(
                app_settings, "L_intrede", df_l_intrede
            ).couple_exit_points(scenario=layer.split("__")[1])

    # Distance to buitenteenlijn
    gdf_buitenteenlijnen: gpd.GeoDataFrame = gpd.read_file(
        app_settings.geopackage_filepath, layer="buitenteenlijn"
    )
    gdf_exit_points["afstand_buitenteenlijn"] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_buitenteenlijnen.distance(pnt).min(), 1)
    )
    df_l_but = gdf_exit_points[["uittredepunt_id", "afstand_buitenteenlijn"]]
    df_l_but = df_l_but.rename(
        columns={"afstand_buitenteenlijn": "L_but__mean"}
    )

    DistCouple(app_settings, "L_but", df_l_but).couple_exit_points()

    # Distance to binnenteenlijn
    gdf_binnenteenlijn: gpd.GeoDataFrame = gpd.read_file(
        app_settings.geopackage_filepath, layer="binnenteenlijn"
    )
    gdf_exit_points["afstand_binnenteenlijn"] = gdf_exit_points.geometry.apply(
        lambda pnt: round(gdf_binnenteenlijn.distance(pnt).min(), 1)
    )
    df_l_bit = gdf_exit_points[["uittredepunt_id", "afstand_binnenteenlijn"]]
    df_l_bit = df_l_bit.rename(
        columns={"afstand_binnenteenlijn": "L_bit__mean"}
    )

    DistCouple(app_settings, "L_bit", df_l_bit).couple_exit_points()

    print(
        BColors.OKBLUE,
        "✔ Afstanden intrede, buitenteen en binnenteen zijn nu gekoppeld aan de uittredepunten.",
        BColors.ENDC,
    )
    return True
