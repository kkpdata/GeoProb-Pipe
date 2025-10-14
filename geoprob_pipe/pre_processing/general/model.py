from __future__ import annotations
from geoprob_pipe.utils.validation_messages import BColors
from InquirerPy import inquirer
from typing import TYPE_CHECKING
from geopandas import read_file
import sqlite3
from pandas import DataFrame
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


LEGAL_MODEL_OPTIONS =["model4a", "model4a i.c.m. MORIA"]


def created_model(app_settings: ApplicationSettings) -> bool:
    df: DataFrame = read_file(app_settings.geopackage_filepath, layer="geoprob_pipe_metadata")

    # Check if no model specified yet
    if "model" not in df['metadata_type'].values.tolist():
        specify_model_to_use(app_settings, update_record=False)
        return True

    # Check if specified model is legal
    current_specified_model = df[df['metadata_type'] == "model"]["values"].iloc[0]
    if current_specified_model not in LEGAL_MODEL_OPTIONS:
        specify_model_to_use(app_settings, update_record=True)
        return True

    # Specified model is legal
    print(BColors.OKBLUE, f"✔  Rekenmodel al ingesteld.", BColors.ENDC)
    return True


def specify_model_to_use(app_settings: ApplicationSettings, update_record: bool = False):

    choice = inquirer.select(
        message="Welk rekenmodel wil je gebruiken? De invoer parameters variëren per model.",
        choices=LEGAL_MODEL_OPTIONS,
        default=LEGAL_MODEL_OPTIONS[0],
    ).execute()

    # Push record
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    sql_statement = f"""INSERT INTO geoprob_pipe_metadata ('metadata_type', 'values') VALUES ('model', '{choice}')"""
    if update_record:
        sql_statement = f"""UPDATE geoprob_pipe_metadata SET 'values' = '{choice}' WHERE metadata_type = 'model'"""
    cursor.execute(sql_statement)
    conn.commit()
    conn.close()

    print(BColors.OKBLUE, f"✅  Rekenmodel ingesteld.", BColors.ENDC)
