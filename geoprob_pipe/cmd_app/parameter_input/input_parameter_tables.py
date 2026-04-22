from __future__ import annotations
import os
import sqlite3
from pandas import read_sql, read_excel
from typing import Optional, TYPE_CHECKING
from geoprob_pipe.cmd_app.parameter_input.initiate_input_excel_tables import DF_EMPTY_CORRELATIE_INVOER
from geoprob_pipe.calculations.systems.mappers.validation import VALIDATION_MAPPER
from pandas import DataFrame
from geoprob_pipe.utils.validation_messages import BColors
from geoprob_pipe.input_data.df_validation.df_parameter_invoer import ValidationParameterInvoer
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


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


def _validate_df_parameter_invoer(df: DataFrame, app_settings: ApplicationSettings) -> bool:
    export_dir = os.path.join(
        os.path.dirname(app_settings.geopackage_filepath), "exports",
        str(app_settings.datetime_stamp), "parameter_input_process")

    label = "Parameter invoer"

    # obj = DataFrameQueryValidation(df=df, failure_queries=FAILURE_QUERIES)
    # result: bool = obj.validate(export_dir=export_dir, label_humanized="Parameter invoer")
    # TODO: Remove FailureQueries-code

    # Set up validator
    validator = ValidationParameterInvoer(df=df)
    geohydrologisch_model = app_settings.geohydrologisch_model
    print(f"{VALIDATION_MAPPER[geohydrologisch_model]=}")
    if (geohydrologisch_model not in VALIDATION_MAPPER.keys() or
            label not in VALIDATION_MAPPER[geohydrologisch_model].keys()):
        print(f"{BColors.WARNING}Data validatie specifiek voor geohydrologisch model {geohydrologisch_model} en "
              f"dataframe {label} is not niet geïmplementeerd. Dit volgt later.{BColors.ENDC}")
    else:
        validator.columns_validations.extend(VALIDATION_MAPPER[geohydrologisch_model][label])

    # Run
    validator.run()
    if validator.df_failures is None or validator.df_failures.__len__() == 0:
        return True

    # Export validation messages
    export_path = validator.to_excel(export_dir)
    print(f"{BColors.WARNING}Validatie is (voortijdig) beëindigd omdat er {validator.df_failures.__len__()} "
          f"validatie issues voor de 'Parameter invoer'-tabel zijn gevonden. De gedetailleerde lijst is "
          f"geëxporteerd naar onderstaande locatie. Los deze issues s.v.p. eerst op. \n"
          f"{export_path}{BColors.ENDC}")
    return False


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

    def validate_and_report(self, app_settings: ApplicationSettings) -> bool:
        if not _validate_df_parameter_invoer(df=self.df_parameter_invoer, app_settings=app_settings): return False
        return True
