from __future__ import annotations
from geoprob_pipe.utils.validation_messages import BColors
from InquirerPy import inquirer
from typing import TYPE_CHECKING
from geopandas import read_file
import sqlite3
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER
from pandas import DataFrame
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def created_model(app_settings: ApplicationSettings) -> bool:
    df: DataFrame = read_file(app_settings.geopackage_filepath, layer="geoprob_pipe_metadata")

    # Check if no model specified yet
    metadata_types = [str(value) for value in df['metadata_type'].values.tolist()]
    if "geohydrologisch_model" not in metadata_types:
        specify_model_to_use(app_settings, update_record=False)
        return True

    # Check if specified model is legal
    current_specified_model = df[df['metadata_type'] == "geohydrologisch_model"]["values"].iloc[0]
    if current_specified_model not in SYSTEM_CALCULATION_MAPPER.keys():
        specify_model_to_use(app_settings, update_record=True)
        return True

    # Specified model is legal
    print(BColors.OKBLUE, f"✔  Geohydrologisch model al ingesteld.", BColors.ENDC)
    return True


def specify_model_to_use(app_settings: ApplicationSettings, update_record: bool = False):
    model_labels = [value["label"] for key, value in SYSTEM_CALCULATION_MAPPER.items()]

    choice = inquirer.select(
        message="Welk geohydrologisch model wil je gebruiken? De invoer parameters variëren per model.",
        choices=model_labels,
        default=model_labels[0],
    ).execute()

    # Push record
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    choice_formatted: str = choice
    choice_formatted = choice_formatted.replace(" ", "").lower()
    sql_statement = f"""
    INSERT INTO geoprob_pipe_metadata 
    ('metadata_type', 'values') VALUES ('geohydrologisch_model', '{choice_formatted}')"""
    if update_record:
        sql_statement = f"""
        UPDATE geoprob_pipe_metadata 
        SET 'values' = '{choice_formatted}' 
        WHERE metadata_type = 'geohydrologisch_model'"""
    cursor.execute(sql_statement)
    conn.commit()
    conn.close()

    print(BColors.OKBLUE, f"✅  Geohydrologisch model ingesteld.", BColors.ENDC)
