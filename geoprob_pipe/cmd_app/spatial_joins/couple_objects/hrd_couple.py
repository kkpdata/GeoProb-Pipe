"""
Class voor het koppelen van de HRD-locaties aan de uittredepunten.
Versimpelde versie van de ShapeCouple class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd
import numpy as np

from .base_couple import BaseCouple

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class HRDCouple(BaseCouple):
    def __init__(self, app_settings: ApplicationSettings) -> None:
        """
        Class voor het koppelen van de hrd locatie namen aan de uittredepunten.

        :param app_settings: Object met de settings van de applicatie.
        """        
        self.app_settings = app_settings

    def couple_exit_points(self) -> None:
        """
        Koppel de hrd_locaties aan de uittredepunten. En voeg deze toe aan de
        geopackage op de juiste manier.
        """        
        # Read uittredepunten
        gdf_exit_points: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer="uittredepunten"
        )
        gdf_hrd: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer="hrd_locaties"
        )
        join_df = gdf_exit_points.sjoin_nearest(gdf_hrd, how="left")
        df_to_add = self._create_df_hrd(join_df)
        self._upsert_to_gpkg(df_to_add)

    def _create_df_hrd(self, join_df: pd.DataFrame) -> pd.DataFrame:
        """
        Methode om de dataframe op te zetten voor de hrd locatie invoer.

        :param join_df: _description_
        :return: _description_
        """        
        df = join_df[["uittredepunt_id"]].copy()
        df = df.rename(columns={"uittredepunt_id": "scope_referentie"})
        df["parameter"] = "buitenwaterstand"
        df["scope"] = "uittredepunt"
        df["ondergrondscenario_naam"] = ""
        df["distribution_type"] = "cdf_curve"
        df["mean"] = np.nan
        df["variation"] = np.nan
        df["deviation"] = np.nan
        df["minimum"] = np.nan
        df["maximum"] = np.nan
        df["fragility_values_ref"] = join_df.get("location_name", "")
        df["bronnen"] = ""
        df["opmerking"] = ""

        # Sort columns
        df = df[
            [
                "parameter",
                "scope",
                "scope_referentie",
                "ondergrondscenario_naam",
                "distribution_type",
                "mean",
                "variation",
                "deviation",
                "minimum",
                "maximum",
                "fragility_values_ref",
                "bronnen",
                "opmerking",
            ]
        ]
        return df
