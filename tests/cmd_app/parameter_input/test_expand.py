# TODO fix parameter zowel per vak in excel en per utp in gis
# TODO fix gis parameters niet uit expanded gevonden?
"""
Voor idere rij in de excel en gis moet worden gecheckt of deze op de juiste
plaats in de expanded staat. En of er iets is overgeslagen door dubble input.
traject->vak->utp
scenario->wildcard
Mischien naar validation
"""

import ast
import math
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


# ---------------------------
# 1. Prioriteitsfunctie
# ---------------------------

def scope_priority(row):
    if row["scope"] == "uittredepunt":
        return 1
    if row["scope"] == "gis_uittredepunt":
        return 2
    if row["scope"] == "vak":
        return 3
    if row["scope"] == "traject":
        return 4
    return 99



# ---------------------------
# 2. Matching functie
# ---------------------------

def find_candidates(out_row, df_input):
    p = out_row["parameter_name"]
    vak = out_row["vak_id"]
    uit = out_row["uittredepunt_id"]
    scen = out_row["ondergrondscenario_naam"]

    df = df_input[df_input["parameter"] == p]

    candidates = []

    # uittredepunt niveau (GEEN vak!)
    candidates.append(df[
        (df["scope"].isin(["uittredepunt", "gis_uittredepunt"])) &
        (df["scope_referentie"] == uit)
    ])

    # vak niveau (GEEN uittredepunt!)
    candidates.append(df[
        (df["scope"] == "vak") &
        (df["scope_referentie"] == vak)
    ])

    # traject
    candidates.append(df[
        df["scope"] == "traject"
    ])

    candidates = pd.concat(candidates, ignore_index=True)

    if candidates.empty:
        return candidates

    candidates = candidates.copy()
    
    candidates["scope_prio"] = candidates.apply(scope_priority, axis=1)

    candidates["is_exact_scenario"] = (
        candidates["ondergrondscenario_naam"] == scen
    )

    # scenario wildcard (fallback)
    candidates = candidates[
        candidates["ondergrondscenario_naam"].isna() |
        (candidates["ondergrondscenario_naam"] == scen)
    ]
    candidates = candidates[~candidates["mean"].isna()]
    return candidates



# ---------------------------
# 3. Validatie per rij
# ---------------------------

def validate_row(out_row, df_input):
    candidates = find_candidates(out_row, df_input)

    if candidates.empty:
        return "NO_CANDIDATE"

    # beste kandidaat volgens regels
    best = candidates.sort_values(
        ["scope_prio", "is_exact_scenario"],
        ascending=[True, False]
    ).iloc[0]

    out_mean = get_mean(out_row["parameter_input"])

    # ---------------------------
    # 1. waarde check
    # ---------------------------
    if not math.isclose(out_mean, best["mean"], rel_tol=1e-6):
        return "WRONG_MEAN"

    # ---------------------------
    # 2. fallback gebruikt terwijl exact bestaat
    # ---------------------------
    same_scope = candidates[
        candidates["scope_prio"] == best["scope_prio"]
    ]

    exact_exists = same_scope[same_scope["is_exact_scenario"]]

    if not best["is_exact_scenario"] and not exact_exists.empty:
        return "FALLBACK_WHILE_EXACT_EXISTS"

    # ---------------------------
    # 3. lagere scope gebruikt terwijl hogere bestaat
    # ---------------------------
    better_scope = candidates[
        candidates["scope_prio"] < best["scope_prio"]
    ]

    if not better_scope.empty:
        return "HIGHER_SCOPE_AVAILABLE"

    return "OK"



# ---------------------------
# 4. Run validatie
# ---------------------------
def validate(df_out, df_input):
    df_out = df_out.copy()

    df_out["validation"] = df_out.apply(
        lambda r: validate_row(r, df_input), axis=1
    )

    errors = df_out[df_out["validation"] != "OK"]

    return df_out, errors


# ---------------------------
# 5. Gebruik
# ---------------------------
conn = sqlite3.connect(gpkg_filepath)
df_out = pd.read_sql("SELECT * FROM data__expanded_parameters", conn)
df_excel = pd.read_sql("SELECT * FROM data__excel_parameter_invoer", conn)
df_gis = pd.read_sql("SELECT * FROM data__gis_parameter_invoer", conn)
df_gis["scope"] = "gis_uittredepunt"
df_input = pd.concat([df_excel, df_gis], ignore_index=True)

df_input["ondergrondscenario_naam"] = (
    df_input["ondergrondscenario_naam"]
    .replace("", pd.NA)
)

df_input["scope_referentie"] = df_input["scope_referentie"].astype("Int64")
df_out["vak_id"] = df_out["vak_id"].astype("Int64")
df_out["uittredepunt_id"] = df_out["uittredepunt_id"].astype("Int64")
conn.close()


validated, errors = validate(df_out, df_input)

print("Aantal fouten:", len(errors))
print(errors.head())
