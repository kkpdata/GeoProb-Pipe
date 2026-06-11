from typing import Dict, List
from pandas import DataFrame, Series
import copy
import sqlite3
from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MAPPER


def _gather_required_input_parameters(geopackage_filepath: str) -> List[str]:

    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT geoprob_pipe_metadata."values" 
        FROM geoprob_pipe_metadata 
        WHERE metadata_type='geohydrologisch_model';
    """)
    result = cursor.fetchone()
    if not result:
        raise ValueError
    model_string = result[0]
    conn.close()
    df_dummy_data = DataFrame(INITIAL_INPUT_MAPPER[model_string]['input'])

    _ = df_dummy_data.sort_values(by=["name"])
    df_dummy_data = df_dummy_data.sort_values(by=["name"])
    return df_dummy_data['name'].unique().tolist()


def merge_into_df(df: DataFrame, df_gather: DataFrame, on_cols: list[str]) -> DataFrame:
    """ If row (unique combination/calculation) does not have a parameter_input yet, then combine first will gather
    the new value, if provided. """

    # Combine two dataframe to ensure index is equal
    df = df.merge(
        df_gather,
        on=on_cols,
        how="left",
        suffixes=("", "_new"),
    )

    # Get value out of _new-col, if no value exists yet
    df["parameter_input"] = df["parameter_input"].combine_first(
        df["parameter_input_new"]
    )

    # Remove _new-col (not needed anymore)
    df.drop(columns=["parameter_input_new"], inplace=True)

    return df


def _1a_excel_uittredepunt_en_scenario(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "uittredepunt")
        & (df_parameter_invoer_combined["ondergrondscenario_naam"].notna())
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "ondergrondscenario_naam", "parameter_input"],
    ].rename(
        columns={
            "scope_referentie": "uittredepunt_id",
            "ondergrondscenario_naam": "naam",
        }
    ).drop_duplicates(["uittredepunt_id", "naam"])

    return merge_into_df(df, df_gather, ["uittredepunt_id", "naam"])


def _1b_gis_uittredepunt_en_scenario(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "gis_uittredepunt")
        & (df_parameter_invoer_combined["ondergrondscenario_naam"].notna())
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "ondergrondscenario_naam", "parameter_input"],
    ].rename(
        columns={
            "scope_referentie": "uittredepunt_id",
            "ondergrondscenario_naam": "naam",
        }
    ).drop_duplicates(["uittredepunt_id", "naam"])

    return merge_into_df(df, df_gather, ["uittredepunt_id", "naam"])


def _2a_excel_uittredepunt(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "uittredepunt")
        & (df_parameter_invoer_combined["ondergrondscenario_naam"].isna())
        & (df_parameter_invoer_combined["parameter_input"] != {})
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "parameter_input"],
    ].rename(columns={"scope_referentie": "uittredepunt_id"}) \
        .drop_duplicates(["uittredepunt_id"])

    return merge_into_df(df, df_gather, ["uittredepunt_id"])


def _2b_gis_uittredepunt(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "gis_uittredepunt")
        & (df_parameter_invoer_combined["parameter_input"] != {})
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "parameter_input"],
    ].rename(columns={"scope_referentie": "uittredepunt_id"}) \
        .drop_duplicates(["uittredepunt_id"])

    return merge_into_df(df, df_gather, ["uittredepunt_id"])


def _3_excel_vak_en_scenario(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "vak")
        & (df_parameter_invoer_combined["ondergrondscenario_naam"].notna())
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "ondergrondscenario_naam", "parameter_input"],
    ].rename(
        columns={
            "scope_referentie": "vak_id",
            "ondergrondscenario_naam": "naam",
        }
    ).drop_duplicates(["vak_id", "naam"])

    return merge_into_df(df, df_gather, ["vak_id", "naam"])


def _4_excel_vak(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    mask = (
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "vak")
        & (df_parameter_invoer_combined["ondergrondscenario_naam"].isna())
    )

    df_gather = df_parameter_invoer_combined.loc[
        mask,
        ["scope_referentie", "parameter_input"],
    ].rename(columns={"scope_referentie": "vak_id"}) \
        .drop_duplicates(["vak_id"])

    return merge_into_df(df, df_gather, ["vak_id"])


def _5_excel_traject(df: DataFrame, df_parameter_invoer_combined: DataFrame, parameter_name: str) -> DataFrame:

    df_gather = df_parameter_invoer_combined.loc[
        (df_parameter_invoer_combined["parameter"] == parameter_name)
        & (df_parameter_invoer_combined["scope"] == "traject")
    ]

    if df_gather.empty:
        return df

    value = df_gather.iloc[0]["parameter_input"]
    mask_na = df["parameter_input"].isna()
    df.loc[mask_na, "parameter_input"] = [
        copy.deepcopy(value) for _ in range(mask_na.sum())
    ]

    return df


def _expand(
        df_parameter_invoer_combined: DataFrame,
        df_identifiers: DataFrame,
        geopackage_filepath: str,
) -> Dict[str, DataFrame]:

    required_input_parameters = _gather_required_input_parameters(
        geopackage_filepath=geopackage_filepath
    )

    collection_of_dfs: Dict[str, DataFrame] = {}

    for parameter_name in required_input_parameters:

        df = df_identifiers.copy()
        df["parameter_input"] = Series([None] * len(df), dtype="object")

        df = _1a_excel_uittredepunt_en_scenario(df, df_parameter_invoer_combined, parameter_name)
        df = _1b_gis_uittredepunt_en_scenario(df, df_parameter_invoer_combined, parameter_name)

        df = _2a_excel_uittredepunt(df, df_parameter_invoer_combined, parameter_name)
        df = _2b_gis_uittredepunt(df, df_parameter_invoer_combined, parameter_name)

        df = _3_excel_vak_en_scenario(df, df_parameter_invoer_combined, parameter_name)

        df = _4_excel_vak(df, df_parameter_invoer_combined, parameter_name)

        df = _5_excel_traject(df, df_parameter_invoer_combined, parameter_name)

        collection_of_dfs[parameter_name] = df

    return collection_of_dfs
