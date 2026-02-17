from __future__ import annotations
import os
import sqlite3
from pandas import read_sql, read_excel
from typing import Optional, TYPE_CHECKING
from geoprob_pipe.cmd_app.parameter_input.initiate_input_excel_tables import DF_EMPTY_CORRELATIE_INVOER
from pandas import DataFrame
from geoprob_pipe.input_data.validation.dataframes.df_parameter_invoer import DF_PARAMETER_INVOER_VALIDATION
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


# def _validate_df_scenario_invoer(df: DataFrame) -> bool:
#     return True


# class ValidationSchema:
#
#     def __init__(self, df: DataFrame, schema: DataFrameSchema):
#         self.df = df
#         self.schema = schema


# class PerformDataFrameValidation:
#
#     def __init__(self, df_label: str, validation_schemas: List[ValidationSchema]):
#         self._valid: Optional[bool] = None
#         for validation_schema in validation_schemas:
#             validation_schema.perform_validate()
#
#
#     @property
#     def validity(self) -> bool:
#         assert isinstance(self._valid, bool), "Validity checked before validation is performed"
#         return self.validity


def _validate_df_parameter_invoer(df: DataFrame, app_settings: ApplicationSettings):
    export_dir = os.path.join(
        os.path.dirname(app_settings.geopackage_filepath), "exports",
        str(app_settings.datetime_stamp), "parameter_input_process")
    for dataframe_validation in DF_PARAMETER_INVOER_VALIDATION:
        dataframe_validation.validate(df=df, export_dir=export_dir)
        if dataframe_validation.valid:
            continue
        return False
    return True

    #
    # validation = PerformDataFrameValidation(
    #     df_label="Parameter invoer", validation_schemas=[
    #         ValidationSchema(
    #             df=df[df["distribution_type"] == "cdf_curve"],
    #             schema=DataFrameSchema({
    #                 "fragility_values_ref": Column(str)
    #             }),
    #         )
    #     ]
    # )
    # return validation.validity
    #
    # # Define validation schemes
    # schemas = [
    #     {
    #         "filter": df["distribution_type"] == "cdf_curve",
    #         "schema": DataFrameSchema({
    #             "fragility_values_ref": Column(str),
    #         }),
    #     }
    # ]
    #     # Perform validation
    # for item in schemas:
    #     try:
    #         df_to_validate = df[item["filter"]]
    #         _ = item["schema"].validate(df_to_validate, lazy=True)
    #     except SchemaErrors as e:
    #
    #         df_failure_cases: DataFrame = e.failure_cases
    #         df_failure_cases = df_failure_cases.sort_values(by=["index"])
    #
    #         # Create directory to report issues in
    #         export_dir = os.path.join(
    #             os.path.dirname(app_settings.geopackage_filepath),
    #             "exports",
    #             str(app_settings.datetime_stamp),
    #             "parameter_input_process")
    #         os.makedirs(export_dir, exist_ok=True)
    #
    #         # Report issues back
    #         export_path = os.path.join(export_dir, "validation_input_tables.xlsx")
    #         if os.path.exists(export_path):
    #             os.remove(export_path)
    #         df_failure_cases.to_excel(export_path)
    #         print(f"{BColors.WARNING}Er zijn {df_failure_cases.__len__()} validatie issues voor de "
    #               f"parameter_invoer-tabel.\n "
    #               f"De gedetailleerde lijst is geëxporteerd naar\n"
    #               f"{export_path}{BColors.ENDC}")
    #
    #         return False
    # return True

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
        # if not _validate_df_scenario_invoer(df=self.df_scenario_invoer): return False
        if not _validate_df_parameter_invoer(df=self.df_parameter_invoer, app_settings=app_settings): return False
        return True
