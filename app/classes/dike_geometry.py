import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

df_dike_geometry = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_vak_par",
)

df_traject_par = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_traject_par",
    index_col="Parameter",
)

df_general_par = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_gen_par",
    index_col="Parameter",
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

        self.max_number_soil_layers = self._count_max_number_soil_layers()
        self.kwelweglengte = self._calculate_kwelweglengte()
        self.deklagen = self._calc_number_of_soil_layers_deklaag()
        self.effectivieve_deklaag = self._calculate_dikte_eff_deklaag()

    def _calculate_kwelweglengte(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        #  breedte_achterland = self.uittredepunt - self.binnenteen -> niet duidelijk waarom dit wordt berekend, wordt nergens gebruikt
        lengte_voorland = self.buitenteen - self.voorland
        breedte_dijklichaam = self.uittredepunt - self.buitenteen
        c1_dagen = self.d_deklaag_voorland / self.kv_voorland
        lambda_1 = (self.doorlatendheid_wv_pakket * 60 * 60 * 24 * self.D_watervoerend_pakket * c1_dagen) ** 0.5
        fictief_voorland = lambda_1 * np.tanh(lengte_voorland / lambda_1)
        fictieve_kwelweglengte = breedte_dijklichaam + fictief_voorland

        df_kwelweglengte = pd.DataFrame()
        df_kwelweglengte["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        df_kwelweglengte["kwelweglengte [m]"] = self.uittredepunt - self.voorland
        df_kwelweglengte["kwelweg 2x breedte dijklichaam [m]"] = 2 * breedte_dijklichaam
        df_kwelweglengte["fictieve kwelweglengte [m]"] = fictieve_kwelweglengte

        return df_kwelweglengte

    def _count_max_number_soil_layers(self):
        self.max_number_soil_layers_calc = sum(["h_start_grondlaag_" in col for col in self.gdf_dike_geometry])
        return self.max_number_soil_layers_calc

    # Deklaag in testcase is ingevuld op basis van de effectieve dikte. In onze versie is het netter om dieptes van alle lagen
    # in te vullen vanaf maaiveld, effectieve dikte te berekenen, en vervolgens hieruit de meewerkende lagen te bepalen.

    def _calc_number_of_soil_layers_deklaag(self):
        # max_number_soil_layers = self._count_columns_with_substring(self.gdf_dike_geometry, "h_start_grondlaag_")
        self.df_deklagen = pd.DataFrame()

        for i in range(self.max_number_soil_layers):
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

    def _calculate_dikte_eff_deklaag(self):
        maaiveld = self.gdf_dike_geometry["h_maaiveld [mNAP]"]
        slootbodem = self.gdf_dike_geometry["h_slootbodem [mNAP]"]
        breedte_sloot = self.gdf_dike_geometry["B (breedte sloot) [m]"]
        breedte_slootbodem = self.gdf_dike_geometry["b (breedte slootbodem) [m]"]
        bodem_deklaag = self.gdf_dike_geometry["h_ok_deklaag [mNAP]"]
        h1 = maaiveld - bodem_deklaag
        h2 = slootbodem - bodem_deklaag
        helling_sloot = (maaiveld - slootbodem) / ((breedte_sloot - breedte_slootbodem) / 2)
        intercept_2_1 = bodem_deklaag + breedte_slootbodem
        x_section = (intercept_2_1 - slootbodem) / (helling_sloot - 2)
        y_section = slootbodem + helling_sloot * x_section
        y_check = intercept_2_1 + 2 * x_section
        h3 = y_section - bodem_deklaag

        situatie = [None] * len(h3)
        d_effectief = [None] * len(h3)

        for i in range(len(h3)):
            if slootbodem[i] <= bodem_deklaag[i]:
                situatie[i] = "sloot doorsnijdt deklaag"
                d_effectief[i] = 0
            elif h1[i] > breedte_sloot[i]:
                situatie[i] = "H1"
                d_effectief[i] = h1[i]
            elif h2[i] < breedte_slootbodem[i]:
                situatie[i] = "H2"
                d_effectief[i] = h2[i]
            else:
                situatie[i] = "H3"
                d_effectief[i] = h3[i]

        self.df_deklagen["Situatie"] = situatie
        self.df_deklagen["D effectieve deklaag [m]"] = d_effectief

        return self.df_deklagen
