import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

# tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
df_dike_geometry = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_vak_par",
)

df_traject_par = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_traject_par",
)

df_general_par = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_gen_par",
)


class DikeGeometry:

    def __init__(self, gdf_dike_geometry):  #: gpd.GeoDataFrame

        # TODO: coordinaten verwerken als geometrisch punt, testcase heeft enkel 1 waarde
        self.gdf_dike_geometry = gdf_dike_geometry
        self.voorland = gdf_dike_geometry["Coordinate voorland (RdX, RdY) [m]"]
        self.buitenteen = gdf_dike_geometry["Coordinate buitenteen (RdX, RdY) [m]"]
        self.binnenteen = gdf_dike_geometry["Coordinate binnenteen (RdX, RdY) [m]"]
        self.uittredepunt = gdf_dike_geometry["Coordinate uittredepunt (RdX, RdY) [m]"]
        self.kv_voorland = gdf_dike_geometry["kv_deklaag_voorland [m/dag]"]
        self.d_deklaag_voorland = gdf_dike_geometry["d_deklaag,voorland [m]"]
        self.doorlatendheid_wv_pakket = gdf_dike_geometry["k_zandlaag [m/s]"]
        self.D_watervoerend_pakket = gdf_dike_geometry["D_watervoerend_pakket [m]"]
        self.h_maaiveld = gdf_dike_geometry["h_maaiveld [mNAP]"]

        self.kwelweglengte = self._calculate_kwelweglengte()
        self.deklagen = self._calc_number_of_soil_layers_deklaag()
        self.effectivieve_deklaag = self._calculate_dikte_eff_deklaag()

    def _calculate_kwelweglengte(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # self.kwelweglengte = self.uittredepunt - self.voorland -> niet duidelijk waarom dit wordt berekend, wordt nergens gebruikt
        # breedte_achterland = self.uittredepunt - self.binnenteen -> niet duidelijk waarom dit wordt berekend, wordt nergens gebruikt
        lengte_voorland = self.buitenteen - self.voorland
        breedte_dijklichaam = self.uittredepunt - self.buitenteen
        c1_dagen = self.d_deklaag_voorland / self.kv_voorland
        lambda_1 = (self.doorlatendheid_wv_pakket * 60 * 60 * 24 * self.D_watervoerend_pakket * c1_dagen) ** 0.5
        fictief_voorland = lambda_1 * np.tanh(lengte_voorland / lambda_1)
        self.fictieve_kwelweglengte = breedte_dijklichaam + fictief_voorland
        return self.fictieve_kwelweglengte

    def _count_columns_with_substring(self, df, substring):
        count = sum([substring in col for col in df.columns])
        return count

    def _calc_number_of_soil_layers_deklaag(self):
        max_number_h_start = self._count_columns_with_substring(self.gdf_dike_geometry, "h_start_grondlaag_")
        self.df_deklagen = pd.DataFrame()

        for i in range(max_number_h_start):
            self.df_deklagen[f"deklaag_{i+1} [m]"] = (
                self.gdf_dike_geometry[f"h_start_grondlaag_{i+1} [mNAP]"]
                - self.gdf_dike_geometry[f"h_eind_grondlaag_{i+1} [mNAP]"]
            )
            self.df_deklagen[f"materiaal deklaag {i+1}"] = self.gdf_dike_geometry[f"materiaal_grondlaag_{i+1}"]

        self.df_deklagen["d deklaag totaal [m]"] = self.df_deklagen.sum(axis=1, numeric_only=True)
        self.df_deklagen["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        first_column = self.df_deklagen.pop("Vaknr")
        self.df_deklagen.insert(0, "Vaknr", first_column)

        return self.df_deklagen

    # Hier gaat het mis
    def _calculate_dikte_eff_deklaag(self):
        h1 = self.gdf_dike_geometry["h_slootbodem [mNAP]"] - self.df_deklagen["d deklaag totaal [m]"]
        return h1


#         def calculate_dikte_eff_deklaag(self):
#            self.h1 = gdf_dike_geometry["Maaiveld"] - gdf_dike_geometry["Bodem deklaag"]
#            self.h2 = gdf_dike_geometry["Slootbodem"] - gdf_dike_geometry["Bodem deklaag"]
#            self.helling_sloot = (df_input_deklaag["Maaiveld"] - df_input_deklaag["Slootbodem"]) / (
#                (df_input_deklaag["B (breedte sloot)"] - df_input_deklaag["b (breedte slootbodem)"]) * 0.5
#             )


# def derive_input():
#     df_input_deklaag["Helling sloot"] = (df_input_deklaag["Maaiveld"] - df_input_deklaag["Slootbodem"]) / (
#         (df_input_deklaag["B (breedte sloot)"] - df_input_deklaag["b (breedte slootbodem)"]) * 0.5
#     )
#     df_input_deklaag["Intercept 2:1"] = df_input_deklaag["Bodem deklaag"] + df_input_deklaag["b (breedte slootbodem)"]
#     df_input_deklaag["Xsection"] = (df_input_deklaag["Intercept 2:1"] - df_input_deklaag["Slootbodem"]) / (
#         df_input_deklaag["Helling sloot"] - 2
#     )
#     df_input_deklaag["Ysection"] = (
#         df_input_deklaag["Slootbodem"] + df_input_deklaag["Helling sloot"] * df_input_deklaag["Xsection"]
#     )
#     df_input_deklaag["H3"] = df_input_deklaag["Ysection"] - df_input_deklaag["Bodem deklaag"]


# derive_input()


# def check_situatie():
#     df_input_deklaag.loc[df_input_deklaag["H2"] >= df_input_deklaag["b (breedte slootbodem)"], "Situatie"] = "H3"
#     df_input_deklaag.loc[df_input_deklaag["H2"] < df_input_deklaag["b (breedte slootbodem)"], "Situatie"] = "H2"
#     df_input_deklaag.loc[df_input_deklaag["H1"] > df_input_deklaag["B (breedte sloot)"], "Situatie"] = "H1"
#     df_input_deklaag.loc[df_input_deklaag["Slootbodem"] <= df_input_deklaag["Bodem deklaag"], "Situatie"] = (
#         "sloot doorsnijdt deklaag"
#     )


# check_situatie()


# def dikte_effectieve_deklaag():
#     df_input_deklaag.loc[
#         df_input_deklaag["H2"] >= df_input_deklaag["b (breedte slootbodem)"], "Dikte effectieve deklaag"
#     ] = df_input_deklaag["H3"]
#     df_input_deklaag.loc[
#         df_input_deklaag["H2"] < df_input_deklaag["b (breedte slootbodem)"], "Dikte effectieve deklaag"
#     ] = df_input_deklaag["H2"]
#     df_input_deklaag.loc[df_input_deklaag["H1"] > df_input_deklaag["B (breedte sloot)"], "Dikte effectieve deklaag"] = (
#         df_input_deklaag["H1"]
#     )
#     df_input_deklaag.loc[
#         df_input_deklaag["Slootbodem"] <= df_input_deklaag["Bodem deklaag"], "Dikte effectieve deklaag"
#     ] = 0
#     return df_input_deklaag


check_script = DikeGeometry(df_dike_geometry)

display(check_script.df_deklagen["d deklaag totaal [m]"])
display(check_script.effectivieve_deklaag)
