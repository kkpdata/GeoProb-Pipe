from __future__ import annotations
from pandas import DataFrame
import sqlite3
from pandas import read_sql, read_excel
from typing import Optional
from geoprob_pipe.questionnaire.parameter_input.initiate_input_excel_tables import DF_EMPTY_CORRELATIE_INVOER


def _load_df_correlatie_invoer_from_geopackage(geopackage_filepath: str) -> DataFrame:

    # Check if table exists in geopackage (older versions don't have this)
    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='correlatie_invoer';")
    bool_table_exists = cursor.fetchone() is not None

    # Return empty if not exists
    if not bool_table_exists:
        return DF_EMPTY_CORRELATIE_INVOER

    # Return db table if exists
    df_correlatie_invoer = read_sql("SELECT * FROM correlatie_invoer;", conn)
    conn.close()
    return df_correlatie_invoer


class InputParameterTables:

    def __init__(self, geopackage_filepath: str, path_to_excel: Optional[str] = None):

        # Placeholders
        self.df_scenario_invoer: Optional[DataFrame] = None
        self.df_parameter_invoer: Optional[DataFrame] = None
        self.df_fragility_values_invoer: Optional[DataFrame] = None
        self.df_correlatie_invoer: Optional[DataFrame] = None

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
        self.df_correlatie_invoer = _load_df_correlatie_invoer_from_geopackage(geopackage_filepath=geopackage_filepath)
        conn.close()

    def _load_data_from_excel(self, path_to_excel: str, geopackage_filepath: str):
        self.df_scenario_invoer = read_excel(path_to_excel, sheet_name="Scenario invoer", header=2)
        self.df_parameter_invoer = read_excel(path_to_excel, sheet_name="Parameter invoer", header=3)
        conn = sqlite3.connect(geopackage_filepath)
        self.df_gis_join_parameter_invoer = read_sql("SELECT * FROM gis_join_parameter_invoer;", conn)
        conn.close()
        self.df_fragility_values_invoer = read_excel(path_to_excel, sheet_name="Fragility values", header=3)
        self.df_correlatie_invoer = read_excel(path_to_excel, sheet_name="Correlatie invoer", header=3)
