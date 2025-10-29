from __future__ import annotations
from pandas import DataFrame
import sqlite3
from pandas import read_sql, read_excel
from typing import TYPE_CHECKING, Optional


class InputParameterTables:

    def __init__(
            self,
            geopackage_filepath: str,
            path_to_excel: Optional[str] = None):

        # Placeholders
        self.df_scenario_invoer: Optional[DataFrame] = None
        self.df_parameter_invoer: Optional[DataFrame] = None
        self.df_fragility_values_invoer: Optional[DataFrame] = None

        if path_to_excel is not None:
            self._load_data_from_excel(path_to_excel=path_to_excel, geopackage_filepath=geopackage_filepath)
        else:
            self._load_data_from_geopackage(geopackage_filepath=geopackage_filepath)

    def _load_data_from_geopackage(self, geopackage_filepath: str):
        conn = sqlite3.connect(geopackage_filepath)
        df_scenario_invoer = read_sql("SELECT * FROM scenario_invoer;", conn)
        self.df_scenario_invoer = df_scenario_invoer[["vak_id", "naam", "kans"]]
        self.df_parameter_invoer = read_sql("SELECT * FROM parameter_invoer;", conn)
        self.df_gis_join_parameter_invoer = read_sql("SELECT * FROM gis_join_parameter_invoer;", conn)
        self.df_fragility_values_invoer = read_sql("SELECT * FROM fragility_values_invoer;", conn)
        conn.close()

    def _load_data_from_excel(self, path_to_excel: str, geopackage_filepath: str):
        self.df_scenario_invoer = read_excel(path_to_excel, sheet_name="Scenario invoer", header=2)
        self.df_parameter_invoer = read_excel(path_to_excel, sheet_name="Parameter invoer", header=3)
        conn = sqlite3.connect(geopackage_filepath)
        self.df_gis_join_parameter_invoer = read_sql("SELECT * FROM gis_join_parameter_invoer;", conn)
        conn.close()
        self.df_fragility_values_invoer = read_excel(path_to_excel, sheet_name="Fragility values", header=3)
