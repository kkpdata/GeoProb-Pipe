"""
Voor idere rij in de excel en gis moet worden gecheckt of deze op de juiste
plaats in de expanded staat. En of er geen hogere prioriteit aanwezig is.
traject->vak->utp
scenario->wildcard
"""

import ast
import sqlite3

import numpy as np
import pandas as pd

# TODO Permanete test gpkg als deze naar de nieuwe standaard is gezet
gpkg_filepath = r"C:\Users\vinji\Python\Libraries\GEOprob-Pipe\Workspace\fix.geoprob_pipe.gpkg"


def get_mean(x):
    if isinstance(x, dict):
        return x.get("mean")
    elif isinstance(x, str):
        d = ast.literal_eval(x)  # string → dict
        return d.get("mean", np.nan)
    return None


def _check_match(df_check: pd.DataFrame, df_compare: pd.DataFrame, key: str):
    rel_tol = 1e-4
    col = key.replace("mean", "match")
    mask_nan = df_compare[key].isna()

    df_check[col] = np.isclose(
        df_compare["mean"], df_compare[key], rtol=rel_tol
    )

    df_check[col] = df_check[col].mask(mask_nan, None)

    return df_check


def validate_expand_tables():
    # --- Verzamel data op uit database
    conn = sqlite3.connect(gpkg_filepath)
    df_out = pd.read_sql("SELECT * FROM data__expanded_parameters", conn)
    df_excel = pd.read_sql("SELECT * FROM data__excel_parameter_invoer", conn)
    df_excel["scope_referentie"] = df_excel["scope_referentie"].astype("Int64")
    df_gis = pd.read_sql("SELECT * FROM data__gis_parameter_invoer", conn)
    df_gis["scope_referentie"] = df_gis["scope_referentie"].astype("Int64")
    df_gis["mean"] = df_gis["mean"].astype(float)
    conn.close()

    df_gis["scope"] = "gis_uittredepunt"
    # Verwijder lege kolommen
    df_excel = df_excel.dropna(axis=1, how="all")
    df_gis = df_gis.dropna(axis=1, how="all")
    df_input = pd.concat([df_excel, df_gis], ignore_index=True)

    # --- Clean dataframes
    df_input["ondergrondscenario_naam"] = df_input[
        "ondergrondscenario_naam"
    ].replace("", pd.NA)
    df_out["ondergrondscenario_naam"] = df_out[
        "ondergrondscenario_naam"
    ].replace("", pd.NA)
    df_out["uittredepunt_id"] = df_out["uittredepunt_id"].astype("Int64")
    df_out = df_out.rename(columns={"parameter_name": "parameter"})

    # Filter Dataframes
    df_out["mean"] = df_out["parameter_input"].apply(get_mean)
    df_out = df_out[
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

    # --- Merge per stap
    df_compare = df_out.copy()

    # Traject
    df_traject = df_input.loc[df_input["scope"] == "traject"]
    df_compare = df_compare.merge(
        df_traject[["parameter", "mean"]],
        on=["parameter"],
        how="left",
        suffixes=["", "_traject"],
    )

    # Vak zonder scenario (Wildcard)
    df_vak_wild = df_input.loc[
        (df_input["scope"] == "vak")
        & (df_input["ondergrondscenario_naam"].isna())
    ]
    df_vak_wild = df_vak_wild.rename(columns={"scope_referentie": "vak_id"})
    df_compare = df_compare.merge(
        df_vak_wild[["parameter", "vak_id", "mean"]],
        on=["parameter", "vak_id"],
        how="left",
        suffixes=["", "_vak_wild"],
    )

    # Vak met scenario
    df_vak_scen = df_input.loc[
        (df_input["scope"] == "vak")
        & (df_input["ondergrondscenario_naam"].notna())
    ]
    df_vak_scen = df_vak_scen.rename(columns={"scope_referentie": "vak_id"})
    df_compare = df_compare.merge(
        df_vak_scen[
            ["parameter", "vak_id", "ondergrondscenario_naam", "mean"]
        ],
        on=["parameter", "vak_id", "ondergrondscenario_naam"],
        how="left",
        suffixes=["", "_vak_scen"],
    )

    # gis_utp zonder scenario (Wildcard)
    df_gis_utp_wild = df_input.loc[
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

    # excel_upt zonder scenario (Wildcard)
    df_excel_utp_wild = df_input.loc[
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
    # gis_utp met scenario
    df_gis_utp_scen = df_input.loc[
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
    # excel_utp met scenario
    df_excel_utp_scen = df_input.loc[
        (df_input["scope"] == "uittredepunt")
        & (df_input["ondergrondscenario_naam"].notna())
    ]
    df_excel_utp_scen = df_excel_utp_wild.rename(
        columns={"scope_referentie": "uittredepunt_id"}
    )
    df_compare = df_compare.merge(
        df_excel_utp_scen[["parameter", "uittredepunt_id", "mean"]],
        on=["parameter", "uittredepunt_id"],
        how="left",
        suffixes=["", "_excel_utp_scen"],
    )

    # --- Check of waardes overeenkomen

    df_check = df_out.copy()

    df_check = _check_match(df_check, df_compare, "mean_traject")
    df_check = _check_match(df_check, df_compare, "mean_vak_wild")
    df_check = _check_match(df_check, df_compare, "mean_vak_scen")
    df_check = _check_match(df_check, df_compare, "mean_gis_utp_wild")
    df_check = _check_match(df_check, df_compare, "mean_excel_utp_wild")
    df_check = _check_match(df_check, df_compare, "mean_gis_utp_scen")
    df_check = _check_match(df_check, df_compare, "mean_excel_utp_scen")

    df_errors = df_out.copy()
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
    
    # Hoogste prioriteit check
    df_errors["highest_priority"] = (
        df_check[cols].idxmax(axis=1).where(df_errors["match"], None)
    )
   
    arr = df_check[cols].to_numpy(dtype=object)

    df_errors["priority_error"] = [
        any(v is False for v in row[(max([i for i, x in enumerate(row) if x is True], default=-1) + 1):])
        for row in arr
    ]

    # Result
    print(df_errors.loc[
        (~df_errors["match"]) | (df_errors["priority_error"])
    ])


validate_expand_tables()
