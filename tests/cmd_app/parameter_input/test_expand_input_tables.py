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
    df_expanded: pd.DataFrame, df_excel_vak: pd.DataFrame, utp_list: list
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

    tolerance = 1e-6

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
        print(f"Errors over vak: {len(df_errors)}")
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

    assert len(df_errors) == 0


def _utp(
    df_expanded: pd.DataFrame, df_excel_utp: pd.DataFrame, utp_list: list
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

    tolerance = 1e-6

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
        print(f"Errors over utp: {len(df_errors)}")
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

    assert len(df_errors) == 0


def test_expand():
    conn = sqlite3.connect(gpkg_filepath)

    # Verzamel data
    df_excel_vak = pd.read_sql(
        "SELECT * FROM data__excel_parameter_invoer WHERE scope == 'vak'", conn
    )
    df_excel_utp = pd.read_sql(
        "SELECT * FROM data__excel_parameter_invoer WHERE scope == 'uittredepunt'",
        conn,
    )
    df_expanded = pd.read_sql("SELECT * FROM data__expanded_parameters", conn)

    utp_list = df_excel_utp["scope_referentie"].unique().tolist()

    _vak(df_expanded, df_excel_vak, utp_list)
    _utp(df_expanded, df_excel_utp, utp_list)
