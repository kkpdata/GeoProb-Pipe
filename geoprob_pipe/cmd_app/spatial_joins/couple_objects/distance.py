from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

from .base import BaseCouple

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class DistCouple(BaseCouple):
    def __init__(
        self, app_settings: ApplicationSettings, param: str, df: pd.DataFrame
    ) -> None:
        """
        Class om de afstand tussen de uittredepunten en de lijnen toe te voegen
        aan de geopackage.

        :param app_settings: Object met alle settings van de applicatie.
        :param str param: De parameter die wordt toegevoegd aan de tabel.
        :param pd.DataFrame df: Dataframe met de waardes per uittredepunt
        """        
        self.app_settings = app_settings
        self.param = param
        self.df = df
    
    def couple_exit_points(self, scenario: str = ""):
        """
        Methode voer het correct opstellen van de dataframe en deze aan de
        geopackage toe te voegen.

        :param str scenario: Naam van het ondergrondscenario waar deze waardes voor
            gelden, defaults to ""
        """        
        df_to_add = self._create_df(self.df, scenario=scenario)
        self._upsert_to_gpkg(df_to_add)
