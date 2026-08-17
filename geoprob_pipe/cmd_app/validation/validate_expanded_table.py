"""
Voor iedere rij in de excel en gis moet worden gecheckt of deze op de juiste
plaats in de expanded staat. En of er geen hogere prioriteit aanwezig is.
traject->vak->utp
scenario->wildcard
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd


if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.parameter_input.added_input_parameters import (
        InputParameterTables,
    )


def get_mean(value) -> float | None:
    """Find the mean value used from the excel or gis input.

    :param value: Data from the source tables
    :return: Mean value as float or None if not found.
    """
    if isinstance(value, dict):
        return value.get("mean")
    elif isinstance(value, str):
        d = ast.literal_eval(value)  # string → dict
        return d.get("mean", np.nan)
    return None


def _check_match(
    df_check: pd.DataFrame, df_compare: pd.DataFrame, key: str
) -> pd.DataFrame:
    """Check of the mean in the expanded table is close to the value in the source table.

    :param df_check: DataFrame with bools of checks.
    :param df_compare: DataFrame with values of alle sources
    :param key: Column name for the check.
    :return: DataFrame with completed checks for a column.
    """
    rel_tol = 1e-4
    col = key.replace("mean", "match")
    mask_nan = df_compare[key].isna()

    df_check[col] = np.isclose(df_compare["mean"], df_compare[key], rtol=rel_tol)

    df_check[col] = df_check[col].mask(mask_nan, None)

    return df_check


def _merge_traject(df_input: pd.DataFrame, df_compare: pd.DataFrame) -> pd.DataFrame:
    df_traject: pd.DataFrame = df_input.loc[df_input["scope"] == "traject"]
    df_compare = df_compare.merge(
        df_traject[["parameter", "mean"]],
        on=["parameter"],
        how="left",
        suffixes=["", "_traject"],
    )
    return df_compare


def _merge_vak_wild(df_input: pd.DataFrame, df_compare: pd.DataFrame) -> pd.DataFrame:
    df_vak_wild = df_input.loc[
        (df_input["scope"] == "vak") & (df_input["ondergrondscenario_naam"].isna())
    ]
    df_vak_wild: pd.DataFrame = df_vak_wild.rename(
        columns={"scope_referentie": "vak_id"}
    )
    df_compare = df_compare.merge(
        df_vak_wild[["parameter", "vak_id", "mean"]],
        on=["parameter", "vak_id"],
        how="left",
        suffixes=["", "_vak_wild"],
    )
    return df_compare


def _merge_vak_scen(df_input: pd.DataFrame, df_compare: pd.DataFrame) -> pd.DataFrame:
    df_vak_scen: pd.DataFrame = df_input.loc[
        (df_input["scope"] == "vak") & (df_input["ondergrondscenario_naam"].notna())
    ]
    df_vak_scen = df_vak_scen.rename(columns={"scope_referentie": "vak_id"})
    df_compare = df_compare.merge(
        df_vak_scen[["parameter", "vak_id", "ondergrondscenario_naam", "mean"]],
        on=["parameter", "vak_id", "ondergrondscenario_naam"],
        how="left",
        suffixes=["", "_vak_scen"],
    )
    return df_compare


def _merge_utp_gis_wild(
    df_input: pd.DataFrame, df_compare: pd.DataFrame
) -> pd.DataFrame:
    df_gis_utp_wild: pd.DataFrame = df_input.loc[
        (df_input["scope"] == "gis_uittredepunt")
        & (df_input["ondergrondscenario_naam"].isna())
    ]
    df_gis_utp_wild = df_gis_utp_wild.rename(
        columns={"scope_referentie": "uittredepunt_id"}
    )
    df_compare = df_compare.merge(
        df_gis_utp_wild[["parameter", "uittredepunt_id", "mean"]],
        on=["parameter", "uittredepunt_id"],
        how="left",
        suffixes=["", "_gis_utp_wild"],
    )
    return df_compare


def _merge_utp_excel_wild(
    df_input: pd.DataFrame, df_compare: pd.DataFrame
) -> pd.DataFrame:
    df_excel_utp_wild: pd.DataFrame = df_input.loc[
        (df_input["scope"] == "uittredepunt")
        & (df_input["ondergrondscenario_naam"].isna())
    ]
    df_excel_utp_wild = df_excel_utp_wild.rename(
        columns={"scope_referentie": "uittredepunt_id"}
    )
    df_compare = df_compare.merge(
        df_excel_utp_wild[["parameter", "uittredepunt_id", "mean"]],
        on=["parameter", "uittredepunt_id"],
        how="left",
        suffixes=["", "_excel_utp_wild"],
    )
    return df_compare


def _merge_utp_gis_scen(
    df_input: pd.DataFrame, df_compare: pd.DataFrame
) -> pd.DataFrame:
    df_gis_utp_scen: pd.DataFrame = df_input.loc[
        (df_input["scope"] == "gis_uittredepunt")
        & (df_input["ondergrondscenario_naam"].notna())
    ]
    df_gis_utp_scen = df_gis_utp_scen.rename(
        columns={"scope_referentie": "uittredepunt_id"}
    )
    df_compare = df_compare.merge(
        df_gis_utp_scen[
            ["parameter", "uittredepunt_id", "ondergrondscenario_naam", "mean"]
        ],
        on=["parameter", "uittredepunt_id", "ondergrondscenario_naam"],
        how="left",
        suffixes=["", "_gis_utp_scen"],
    )
    return df_compare


def _merge_utp_excel_scen(
    df_input: pd.DataFrame, df_compare: pd.DataFrame
) -> pd.DataFrame:
    df_excel_utp_scen: pd.DataFrame = df_input.loc[
        (df_input["scope"] == "uittredepunt")
        & (df_input["ondergrondscenario_naam"].notna())
    ]
    df_excel_utp_scen = df_excel_utp_scen.rename(
        columns={"scope_referentie": "uittredepunt_id"}
    )
    df_compare = df_compare.merge(
        df_excel_utp_scen[["parameter", "uittredepunt_id", "mean"]],
        on=["parameter", "uittredepunt_id"],
        how="left",
        suffixes=["", "_excel_utp_scen"],
    )
    return df_compare


def has_priority_error(row) -> bool:
    """This function will check for all rows where the first True-value
    in the row is, starting from the right to the left.
    Values can be True, False or None.
    
    In the case of None; no value was provided at this level.
    True means the value  provided matches the value in the expanded table
    And False means the value does not match the value in the expanded table.
    If true is found it will check if any of the values to the right are False.
    If one of these is found, there was a value found higher in the hierarchy that
    was unused.

    :param row: Row from the DataFrame
    :return: True if error found, else false
    """
    # Find de column index van True met de hoogste plaats in de hierarchy.
    last_true_idx: int = max(
        (i for i, value in enumerate(row) if value is True),
        default=-1,
    )

    values_after_last_true = row[last_true_idx + 1 :]

    return any(value is False for value in values_after_last_true)


def validate_expand_tables(
    tables: InputParameterTables, df_expanded: pd.DataFrame
) -> None:
    """Validation function for the expanded parameters table. Checks of the values in
    the table correspond the values in de source tables. And checks of a value higher
    in the hierarchy exist than was used.

    :param tables: Source tables.
    :param df_expanded: expanded parameter table.
    """
    df_excel: pd.DataFrame = tables.df_parameter_invoer.copy()
    df_gis: pd.DataFrame = tables.df_gis_join_parameter_invoer.copy()

    # Remove empty columns for pandas.concat.
    df_excel = df_excel.dropna(axis=1, how="all")
    df_gis = df_gis.dropna(axis=1, how="all")

    df_input: pd.DataFrame = pd.concat([df_excel, df_gis], ignore_index=True)

    # --- Clean dataframes ---
    df_excel["scope_referentie"] = df_excel["scope_referentie"].astype("Int64")
    df_gis["scope_referentie"] = df_gis["scope_referentie"].astype("Int64")
    df_gis["mean"] = df_gis["mean"].astype(float)
    df_gis["scope"] = "gis_uittredepunt"
    df_expanded = df_expanded.rename(columns={"parameter_name": "parameter"})
    df_input["ondergrondscenario_naam"] = df_input["ondergrondscenario_naam"].replace(
        "", pd.NA
    )
    df_expanded["ondergrondscenario_naam"] = df_expanded[
        "ondergrondscenario_naam"
    ].replace("", pd.NA)
    df_expanded["uittredepunt_id"] = df_expanded["uittredepunt_id"].astype("Int64")

    # Filter Dataframes
    df_expanded["mean"] = df_expanded["parameter_input"].apply(get_mean)
    df_expanded = df_expanded[
        [
            "parameter",
            "vak_id",
            "uittredepunt_id",
            "ondergrondscenario_naam",
            "mean",
        ]
    ]
    df_input = df_input[
        [
            "parameter",
            "scope",
            "scope_referentie",
            "ondergrondscenario_naam",
            "mean",
        ]
    ]

    # --- Merge per step in hierarchy ---
    df_compare: pd.DataFrame = df_expanded.copy()

    df_compare = _merge_traject(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_vak_wild(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_vak_scen(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_utp_gis_wild(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_utp_excel_wild(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_utp_excel_scen(df_input=df_input, df_compare=df_compare)
    df_compare = _merge_utp_gis_scen(df_input=df_input, df_compare=df_compare)

    # --- Check of values are equal ---
    df_check: pd.DataFrame = df_expanded.copy()

    df_check = _check_match(df_check, df_compare, "mean_traject")
    df_check = _check_match(df_check, df_compare, "mean_vak_wild")
    df_check = _check_match(df_check, df_compare, "mean_vak_scen")
    df_check = _check_match(df_check, df_compare, "mean_gis_utp_wild")
    df_check = _check_match(df_check, df_compare, "mean_excel_utp_wild")
    df_check = _check_match(df_check, df_compare, "mean_gis_utp_scen")
    df_check = _check_match(df_check, df_compare, "mean_excel_utp_scen")

    df_errors: pd.DataFrame = df_expanded.copy()

    cols = [
        "match_traject",
        "match_vak_wild",
        "match_vak_scen",
        "match_gis_utp_wild",
        "match_excel_utp_wild",
        "match_gis_utp_scen",
        "match_excel_utp_scen",
    ]
    df_errors["match"] = df_check[cols].any(axis=1)

    # --- Check highest hierarchy ---
    df_errors["highest_priority"] = (
        df_check[cols].idxmax(axis=1).where(df_errors["match"], None)
    )

    arr = df_check[cols].to_numpy(dtype=object)

    df_errors["priority_error"] = [
        has_priority_error(row)
        for row in arr
    ]
    # FIXME Temporary fix for the 'buitenwaterstand' parameter
    df_errors = df_errors.loc[df_expanded["parameter"] != "buitenwaterstand"]

    # Result: collect all rows without a match or wrong hierarchy
    df_validation_output = df_errors.loc[
        (~df_errors["match"]) | (df_errors["priority_error"])
    ]
    if len(df_validation_output) > 0:
        # TODO Print to excel with error message
        print(df_validation_output)
