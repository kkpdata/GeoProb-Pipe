# TODO fix parameter zowel per vak in excel en per utp in gis
# TODO fix gis parameters niet uit expanded gevonden?
"""
Voor idere rij in de excel en gis moet worden gecheckt of deze op de juiste
plaats in de expanded staat. En of er iets is overgeslagen door dubble input.
traject->vak->utp
scenario->wildcard
"""


import ast
import sqlite3

import numpy as np
import pandas as pd

# TODO Permanete test gpkg als deze naar de nieuwe standaard is gezet
gpkg_filepath = r"C:\Users\vinji\Python\Libraries\GEOprob-Pipe\Workspace\fix.geoprob_pipe.gpkg"


def _extract_mean(val):
    if pd.isna(val):
        return np.nan
    try:
        d = ast.literal_eval(val)  # string → dict
        return d.get("mean", np.nan)
    except Exception:
        return np.nan


def _vak(
    df_expanded: pd.DataFrame,
    df_excel_vak: pd.DataFrame,
    utp_list: list,
    parameter: str,
):
    mask = df_expanded["uittredepunt_id"].isin(utp_list)

    df_expanded_vak = df_expanded.loc[~mask]
    df_expanded_vak = df_expanded_vak.rename(
        columns={"parameter_name": "parameter"}
    )
    df_expanded_vak["mean_val"] = df_expanded_vak["parameter_input"].apply(
        _extract_mean
    )
    df_excel_vak = df_excel_vak.rename(
        columns={"mean": "mean_val", "scope_referentie": "vak_id"}
    )
    # merge
    keys = ["parameter", "vak_id", "ondergrondscenario_naam"]
    df_compare = df_excel_vak.merge(
        df_expanded_vak[keys + ["mean_val"]],
        on=keys,
        how="outer",
        suffixes=("_excel", "_expanded"),
        indicator=True,
    )

    tolerance = 1e-4

    df_compare["verschil"] = np.abs(
        df_compare["mean_val_excel"] - df_compare["mean_val_expanded"]
    )
    df_errors = df_compare[
        (df_compare["_merge"] != "both")  # ontbrekende rijen
        | (df_compare["verschil"] > tolerance)
        | (
            df_compare["mean_val_excel"].isna()
            != df_compare["mean_val_expanded"].isna()
        )
    ].dropna(subset=["distribution_type"])
    if len(df_errors) != 0:
        print(f"Errors over vak bij {parameter}: {len(df_errors)}")
        print(
            df_errors[
                [
                    "parameter",
                    "vak_id",
                    "ondergrondscenario_naam",
                    "mean_val_excel",
                    "mean_val_expanded",
                    "verschil",
                ]
            ].head()
        )

    return df_errors


def _utp(
    df_expanded: pd.DataFrame,
    df_excel_utp: pd.DataFrame,
    utp_list: list,
    parameter: str,
):
    mask = df_expanded["uittredepunt_id"].isin(utp_list)

    df_expanded_utp = df_expanded.loc[mask]
    df_expanded_utp = df_expanded_utp.rename(
        columns={"parameter_name": "parameter"}
    )
    df_expanded_utp["mean_val"] = df_expanded_utp["parameter_input"].apply(
        _extract_mean
    )
    df_excel_utp = df_excel_utp.rename(
        columns={"mean": "mean_val", "scope_referentie": "uittredepunt_id"}
    )
    # merge
    keys = ["parameter", "uittredepunt_id", "ondergrondscenario_naam"]

    df_compare = df_excel_utp.merge(
        df_expanded_utp[keys + ["mean_val"]],
        on=keys,
        how="outer",
        suffixes=("_excel", "_expanded"),
        indicator=True,
    )

    tolerance = 1e-4

    df_compare["verschil"] = np.abs(
        df_compare["mean_val_excel"] - df_compare["mean_val_expanded"]
    )
    df_errors = df_compare[
        (df_compare["_merge"] != "both")  # ontbrekende rijen
        | (df_compare["verschil"] > tolerance)
        | (
            df_compare["mean_val_excel"].isna()
            != df_compare["mean_val_expanded"].isna()
        )
    ].dropna(subset=["distribution_type"])
    if len(df_errors) != 0:
        print(f"Errors over utp bij {parameter}: {len(df_errors)}")
        print(
            df_errors[
                [
                    "parameter",
                    "uittredepunt_id",
                    "ondergrondscenario_naam",
                    "mean_val_excel",
                    "mean_val_expanded",
                    "verschil",
                ]
            ].head()
        )

    return df_errors


def test_expand():
    conn = sqlite3.connect(gpkg_filepath)

    # Verzamel data
    df_excel_vak = pd.read_sql(
        "SELECT * FROM data__excel_parameter_invoer WHERE scope = 'vak'", conn
    )
    df_excel_utp = pd.read_sql(
        "SELECT * FROM data__excel_parameter_invoer WHERE scope = 'uittredepunt'",
        conn,
    )
    df_gis_utp = pd.read_sql(
        "SELECT * FROM data__gis_parameter_invoer WHERE scope = 'uittredepunt'",
        conn,
    )
    if not df_excel_utp.empty:
        df_utp = pd.concat(
            [df_excel_utp, df_gis_utp], join="outer", ignore_index=True
        )
    else:
        df_utp = df_gis_utp

    df_expanded = pd.read_sql("SELECT * FROM data__expanded_parameters", conn)

    df_errors = pd.DataFrame()
    for param in df_expanded["parameter_name"].unique().tolist():
        mask_utp = df_utp["parameter"] == param
        mask_vak = df_excel_vak["parameter"] == param
        mask_expanded = df_expanded["parameter_name"] == param
        utp_list = df_utp.loc[mask_utp, "scope_referentie"].unique().tolist()  # type:ignore

        df_errors = pd.concat(
            [
                df_errors,
                _vak(
                    df_expanded=df_expanded[mask_expanded],
                    df_excel_vak=df_excel_vak[mask_vak],
                    utp_list=utp_list,
                    parameter=param,
                ),
            ]
        )
        df_errors = pd.concat(
            [
                df_errors,
                _utp(
                    df_expanded=df_expanded[mask_expanded],
                    df_excel_utp=df_utp[mask_utp],
                    utp_list=utp_list,
                    parameter=param,
                ),
            ]
        )
    assert len(df_errors) == 0


test_expand()
