import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found
import pandas as pd

# tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
df_input_deklaag_sloot = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="input_sloot_deklaag",
)

# tijdelijk dataframe voor testen, input komt eigenlijk uit functie statistiek
df_input_deklaag_bodem_deklaag = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="TEMP_bodem_deklaag",
)

#  tijdelijke merge voor testen
df_input_deklaag = df_input_deklaag_sloot.merge(df_input_deklaag_bodem_deklaag, left_index=True, right_index=True)

# toevoegen -> test voor input (enkel floats)





def derive_input():
    df_input_deklaag["H1"] = df_input_deklaag["Maaiveld"] - df_input_deklaag["Bodem deklaag"]
    df_input_deklaag["H2"] = df_input_deklaag["Slootbodem"] - df_input_deklaag["Bodem deklaag"]
    df_input_deklaag["Helling sloot"] = (df_input_deklaag["Maaiveld"] - df_input_deklaag["Slootbodem"]) / (
        (df_input_deklaag["B (breedte sloot)"] - df_input_deklaag["b (breedte slootbodem)"]) * 0.5
    )
    df_input_deklaag["Intercept 2:1"] = df_input_deklaag["Bodem deklaag"] + df_input_deklaag["b (breedte slootbodem)"]
    df_input_deklaag["Xsection"] = (df_input_deklaag["Intercept 2:1"] - df_input_deklaag["Slootbodem"]) / (
        df_input_deklaag["Helling sloot"] - 2
    )
    df_input_deklaag["Ysection"] = (
        df_input_deklaag["Slootbodem"] + df_input_deklaag["Helling sloot"] * df_input_deklaag["Xsection"]
    )
    df_input_deklaag["H3"] = df_input_deklaag["Ysection"] - df_input_deklaag["Bodem deklaag"]


derive_input()


def check_situatie():
    df_input_deklaag.loc[df_input_deklaag["H2"] >= df_input_deklaag["b (breedte slootbodem)"], "Situatie"] = "H3"
    df_input_deklaag.loc[df_input_deklaag["H2"] < df_input_deklaag["b (breedte slootbodem)"], "Situatie"] = "H2"
    df_input_deklaag.loc[df_input_deklaag["H1"] > df_input_deklaag["B (breedte sloot)"], "Situatie"] = "H1"
    df_input_deklaag.loc[df_input_deklaag["Slootbodem"] <= df_input_deklaag["Bodem deklaag"], "Situatie"] = (
        "sloot doorsnijdt deklaag"
    )


check_situatie()


def dikte_effectieve_deklaag():
    df_input_deklaag.loc[
        df_input_deklaag["H2"] >= df_input_deklaag["b (breedte slootbodem)"], "Dikte effectieve deklaag"
    ] = df_input_deklaag["H3"]
    df_input_deklaag.loc[
        df_input_deklaag["H2"] < df_input_deklaag["b (breedte slootbodem)"], "Dikte effectieve deklaag"
    ] = df_input_deklaag["H2"]
    df_input_deklaag.loc[df_input_deklaag["H1"] > df_input_deklaag["B (breedte sloot)"], "Dikte effectieve deklaag"] = (
        df_input_deklaag["H1"]
    )
    df_input_deklaag.loc[
        df_input_deklaag["Slootbodem"] <= df_input_deklaag["Bodem deklaag"], "Dikte effectieve deklaag"
    ] = 0
    return df_input_deklaag
