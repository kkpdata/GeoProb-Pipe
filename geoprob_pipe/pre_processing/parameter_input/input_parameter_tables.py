from __future__ import annotations
from pandas import DataFrame
import sqlite3
from pandas import read_sql
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


class InputParameterTables:

    def __init__(self, app_settings: Optional[ApplicationSettings] = None, path_to_excel: Optional[str] = None):

        if app_settings is None and path_to_excel is None:
            raise ValueError

        # Placeholders
        self.df_scenario_invoer: Optional[DataFrame] = None
        self.df_parameter_invoer: Optional[DataFrame] = None
        self.df_fragility_values_invoer: Optional[DataFrame] = None
        self.tables_exist_in_geopackage: Optional[bool] = None

        if app_settings is not None:
            self._load_data_from_geopackage(app_settings)
        else:
            self._load_data_from_excel()

    def _load_data_from_geopackage(self, app_settings: ApplicationSettings):
        gpkg_file_path = app_settings.geopackage_filepath
        conn = sqlite3.connect(gpkg_file_path)
        self.df_scenario_invoer = read_sql("SELECT * FROM scenario_invoer;", conn)
        self.df_parameter_invoer = read_sql("SELECT * FROM parameter_invoer;", conn)
        self.df_fragility_values_invoer = read_sql("SELECT * FROM fragility_values_invoer;", conn)
        self.tables_exist_in_geopackage = True
        conn.close()

    def _load_data_from_excel(self):
        raise NotImplementedError  # TODO
