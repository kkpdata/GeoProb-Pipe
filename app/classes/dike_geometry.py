import geopandas as gpd
import numpy as np
import pandas as pd

df_dike_geometry = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="test_vak_par",
)

# Test_voor_coordinaten
df_coordinate_test = pd.read_excel(
    r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
    sheet_name="Coordinaten_test",
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

#jjaja

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

        self.kwelweglengte = self._calculate_kwelweglengte()
        self.max_number_soil_layers_in_deklaag = self._count_max_number_soil_layers_in_deklaag()
        self.deklaag = self._calc_number_of_soil_layers_in_deklaag()
        self.effectieve_deklaag = self._calculate_dikte_eff_deklaag()

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

        df_kwelweglengte = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "kwelweglengte [m]": self.uittredepunt - self.voorland,
                "kwelweg 2x breedte dijklichaam [m]": 2 * breedte_dijklichaam,
                "fictieve kwelweglengte [m]": fictieve_kwelweglengte,
            }
        )
        return df_kwelweglengte

    def _count_max_number_soil_layers_in_deklaag(self):
        return sum(["h_start_grondlaag_" in col for col in self.gdf_dike_geometry])

    def _calc_number_of_soil_layers_in_deklaag(self):
        # TODO Deklaag in testcase is ingevuld op basis van de effectieve dikte. In onze versie is het netter om dieptes van alle lagen
        # in te vullen vanaf maaiveld, effectieve dikte te berekenen, en vervolgens hieruit de meewerkende lagen te bepalen.
        self.df_deklaag = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                # "h_start_grondlaag [mNAP]": self.gdf_dike_geometry["h_start_grondlaag_1 [mNAP]"],
            }
        )

        # for i in range(self.max_number_soil_layers_in_deklaag - 2):
        #     self.df_deklaag["h_start_grondlaag [mNAP]"] = self.df_deklaag.apply(
        #         (
        #             self.df_deklaag["h_start_grondlaag [mNAP]"],
        #             self.gdf_dike_geometry[f"h_start_grondlaag_{i+2} [mNAP]"],
        #         ),
        #         axis=1,
        #     )

        for i in range(self.max_number_soil_layers_in_deklaag):

            self.df_deklaag[f"deklaag_{i+1} [m]"] = (
                self.gdf_dike_geometry[f"h_start_grondlaag_{i+1} [mNAP]"]
                - self.gdf_dike_geometry[f"h_eind_grondlaag_{i+1} [mNAP]"]
            )
            self.df_deklaag[f"materiaal deklaag {i+1}"] = self.gdf_dike_geometry[f"materiaal_grondlaag_{i+1}"]

        self.df_deklaag["Dikte deklaag totaal [m]"] = self.df_deklaag.sum(axis=1, numeric_only=True)

        return self.df_deklaag

    def _calculate_dikte_eff_deklaag(self):
        maaiveld_NAP = self.gdf_dike_geometry["h_maaiveld [mNAP]"]
        slootbodem_NAP = self.gdf_dike_geometry["h_slootbodem [mNAP]"]
        slootbodem_breedte = self.gdf_dike_geometry["b (breedte slootbodem) [m]"]
        sloot_breedte = self.gdf_dike_geometry["B (breedte sloot) [m]"]
        deklaag_bodem_NAP = self.gdf_dike_geometry["h_ok_deklaag [mNAP]"]

        h1 = maaiveld_NAP - deklaag_bodem_NAP
        h2 = slootbodem_NAP - deklaag_bodem_NAP
        helling_sloot = (maaiveld_NAP - slootbodem_NAP) / ((sloot_breedte - slootbodem_breedte) / 2)
        intercept_2_1 = deklaag_bodem_NAP + slootbodem_breedte
        x_section = (intercept_2_1 - slootbodem_NAP) / (helling_sloot - 2)
        y_section = slootbodem_NAP + helling_sloot * x_section
        h3 = y_section - deklaag_bodem_NAP

        self.df_deklaag["Situatie"] = None
        self.df_deklaag["Dikte effectieve deklaag [m]"] = None
        for i in range(len(h3)):
            if slootbodem_NAP[i] <= deklaag_bodem_NAP[i]:
                self.df_deklaag["Situatie"].iat[i] = "sloot doorsnijdt deklaag"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = 0
            elif h1[i] > sloot_breedte[i]:
                self.df_deklaag["Situatie"].iat[i] = "H1"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h1[i]
            elif h2[i] < slootbodem_breedte[i]:
                self.df_deklaag["Situatie"].iat[i] = "H2"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h2[i]
            else:
                self.df_deklaag["Situatie"].iat[i] = "H3"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h3[i]

        return self.df_deklaag


# check = DikeGeometry(df_dike_geometry)
# display(check.effectieve_deklaag)
