from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from typing import TYPE_CHECKING
import sqlite3
from geoprob_pipe.cmd_app.utils.misc import get_geohydrological_model
from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MAPPER
from pandas import DataFrame
import numpy as np
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def push_scenario_invoer_tabel(app_settings: ApplicationSettings):

    # Genereer tabel input (o.b.v. vakindeling)
    gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
    gdf_vakindeling = gdf_vakindeling.sort_values(by=["id"])
    df_scenarios = gdf_vakindeling[["id"]].copy()
    df_scenarios.loc[:, 'naam'] = "scenario1"
    df_scenarios.loc[:, 'kans'] = 1.00

    # Rename columns
    df_scenarios = df_scenarios.rename(columns={"id": "vak_id"})

    # Push to geopackage
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df_scenarios.to_sql("scenario_invoer", conn, if_exists="replace", index=False)
    conn.close()


def push_parameter_invoer_tabel(app_settings: ApplicationSettings):

    model_string = get_geohydrological_model(app_settings=app_settings)

    # Start base of table
    df_dummy_data = DataFrame(INITIAL_INPUT_MAPPER[model_string]['input'])
    df_dummy_data = df_dummy_data.sort_values(by=["name"])
    df_parameter_invoer: DataFrame = df_dummy_data[[
        "name", "distribution_type", "mean", "variation", "deviation"]].copy()

    # Rename columns
    df_parameter_invoer = df_parameter_invoer.rename(columns={"name": "parameter"})

    # Convert distribution type objects to string
    df_parameter_invoer["distribution_type"] = df_parameter_invoer["distribution_type"].apply(lambda x: x.__str__())

    # Add missing columns
    df_parameter_invoer.loc[:, "scope"] = "traject"
    df_parameter_invoer.loc[:, "scope_referentie"] = ""
    df_parameter_invoer.loc[:, "ondergrondscenario_naam"] = ""
    df_parameter_invoer.loc[:, "bronnen"] = ""
    df_parameter_invoer.loc[:, "opmerking"] = ""
    df_parameter_invoer.loc[:, "fragility_values_ref"] = ""
    df_parameter_invoer.loc[:, "minimum"] = np.nan
    df_parameter_invoer.loc[:, "maximum"] = np.nan

    # Sort dataframe
    df_parameter_invoer = df_parameter_invoer[[
        "parameter", "scope", "scope_referentie", "ondergrondscenario_naam",
        "distribution_type", "mean", "variation", "deviation", "minimum", "maximum", "fragility_values_ref",
        "bronnen", "opmerking"]].copy()

    # Push to geopackage
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df_parameter_invoer.to_sql("parameter_invoer", conn, if_exists="replace", index=False)
    conn.close()


def push_fragility_values_invoer_tabel(app_settings: ApplicationSettings):

    # Construct table
    water_levels = [3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]
    exceedance_values = [5.8, 4.6, 2.8, 1.7, 1.3, 0.65, 0.377, 0.236, 0.119, 0.048, 0.0195, 0.0069, 0.00134, 0.0001]
    example_fragility_values = {
        "fragility_values_ref": ["voorbeeld_hr"] * water_levels.__len__(),
        "waarde": water_levels,
        "kans": exceedance_values}
    df_fragility_values_invoer = DataFrame(example_fragility_values)

    # Push to geopackage
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df_fragility_values_invoer.to_sql("fragility_values_invoer", conn, if_exists="replace", index=False)
    conn.close()


DF_EMPTY_CORRELATIE_INVOER = DataFrame({"parameter_a": [], "parameter_b": [], "correlation": []})


def push_correlatie_invoer_tabel(app_settings: ApplicationSettings):
    # Push to geopackage
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    DF_EMPTY_CORRELATIE_INVOER.to_sql("correlatie_invoer", conn, if_exists="replace", index=False)
    conn.close()


def initiate_input_excel_tables(app_settings: ApplicationSettings):

    # Fill 'Scenario invoer'
    push_scenario_invoer_tabel(app_settings=app_settings)

    # Fill 'Parameter invoer'
    push_parameter_invoer_tabel(app_settings=app_settings)

    # Fill 'Fragility values invoer'
    push_fragility_values_invoer_tabel(app_settings=app_settings)

    # Fill 'Correlatie invoer'
    push_correlatie_invoer_tabel(app_settings=app_settings)
