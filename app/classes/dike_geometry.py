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


class DikeGeometry:

    def __init__(self, gdf_dike_geometry):  #: gpd.GeoDataFrame

        # TODO: coordinaten verwerken als geometrisch punt, testcase heeft enkel 1 waarde
        self.gdf_dike_geometry = gdf_dike_geometry
        self.vaknr = gdf_dike_geometry["Vaknr"]
        self.zandlaag = gdf_dike_geometry["Zandlaag (tussenlaag / pleistoceen)"]
        self.coord_voorland = gdf_dike_geometry["Coordinate voorland (RdX, RdY) [m]"]
        self.coord_buitenteen = gdf_dike_geometry["Coordinate buitenteen (RdX, RdY) [m]"]
        self.coord_binnenteen = gdf_dike_geometry["Coordinate binnenteen (RdX, RdY) [m]"]
        self.coord_uittredepunt = gdf_dike_geometry["Coordinate uittredepunt (RdX, RdY) [m]"]
        self.h_buitenwaterstand = gdf_dike_geometry["h_buitenwaterstand [mNAP]"]
        self.h_exit = gdf_dike_geometry["h_exit [mNAP]"]
        self.h_watervoerend = gdf_dike_geometry["h_watervoerend [mNAP]"]
        self.h_maaiveld = gdf_dike_geometry["h_maaiveld [mNAP]"]
        self.h_slootbodem = gdf_dike_geometry["h_slootbodem [mNAP]"]
        self.breedte_sloot = gdf_dike_geometry["B (breedte sloot) [m]"]
        self.breedte_slootbodem = gdf_dike_geometry["b (breedte slootbodem) [m]"]
        self.dikte_watervoerend_pakket = gdf_dike_geometry["D_watervoerend_pakket [m]"]
        self.dikte_deklaag_voorland = gdf_dike_geometry["d_deklaag,voorland [m]"]
        self.kv_voorland = gdf_dike_geometry["kv_deklaag_voorland [m/dag]"]
        self.doorlatendheid_watervoerend = gdf_dike_geometry["k_zandlaag [m/s]"]
        self.d_70_watervoerend_pakket = gdf_dike_geometry["d_70 [mm]"]
        self.r_factor = gdf_dike_geometry["r [-]"]
        self.sterktefactor = gdf_dike_geometry["sterktefactor"]
        self.h_onderkant_deklaag = gdf_dike_geometry["h_ok_deklaag [mNAP]"]

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
        lengte_voorland = self.coord_buitenteen - self.coord_voorland
        breedte_dijklichaam = self.coord_uittredepunt - self.coord_buitenteen
        c1_dagen = self.dikte_deklaag_voorland / self.kv_voorland
        lambda_1 = (self.doorlatendheid_watervoerend * 60 * 60 * 24 * self.dikte_watervoerend_pakket * c1_dagen) ** 0.5
        fictief_voorland = lambda_1 * np.tanh(lengte_voorland / lambda_1)
        fictieve_kwelweglengte = breedte_dijklichaam + fictief_voorland

        df_kwelweglengte = pd.DataFrame(
            {
                "Vaknr": self.vaknr,
                "kwelweglengte [m]": self.coord_uittredepunt - self.coord_voorland,
                "kwelweg 2x breedte dijklichaam [m]": 2 * breedte_dijklichaam,
                "fictieve kwelweglengte [m]": fictieve_kwelweglengte,
            }
        )
        return df_kwelweglengte

    def _count_max_number_soil_layers_in_deklaag(self):
        return sum(["h_start_grondlaag_" in col for col in self.gdf_dike_geometry])

    # TODO Deklaag in testcase is ingevuld op basis van de effectieve dikte. In onze versie is het netter om dieptes van alle lagen
    # in te vullen vanaf maaiveld, effectieve dikte te berekenen, en vervolgens hieruit de meewerkende lagen te bepalen.
    def _calc_number_of_soil_layers_in_deklaag(self):
        self.df_deklaag = pd.DataFrame({"Vaknr": self.vaknr})

        for i in range(self.max_number_soil_layers_in_deklaag):
            self.df_deklaag[f"deklaag_{i+1} [m]"] = (
                self.gdf_dike_geometry[f"h_start_grondlaag_{i+1} [mNAP]"]
                - self.gdf_dike_geometry[f"h_eind_grondlaag_{i+1} [mNAP]"]
            )
            self.df_deklaag[f"materiaal deklaag {i+1}"] = self.gdf_dike_geometry[f"materiaal_grondlaag_{i+1}"]

        self.df_deklaag["Dikte deklaag totaal [m]"] = self.df_deklaag.sum(axis=1, numeric_only=True)

        # for i in range(self.max_number_soil_layers_in_deklaag - 2):
        #     self.df_deklaag["h_start_grondlaag [mNAP]"] = self.df_deklaag.apply(
        #         (
        #             self.df_deklaag["h_start_grondlaag [mNAP]"],
        #             self.gdf_dike_geometry[f"h_start_grondlaag_{i+2} [mNAP]"],
        #         ),
        #         axis=1,
        #     )

        return self.df_deklaag

    def _calculate_dikte_eff_deklaag(self):
        h1 = self.h_maaiveld - self.h_onderkant_deklaag
        h2 = self.h_slootbodem - self.h_onderkant_deklaag
        helling_sloot = (self.h_maaiveld - self.h_slootbodem) / ((self.breedte_sloot - self.breedte_slootbodem) / 2)
        intercept_2_1 = self.h_onderkant_deklaag + self.breedte_slootbodem
        x_section = (intercept_2_1 - self.h_slootbodem) / (helling_sloot - 2)
        y_section = self.h_slootbodem + helling_sloot * x_section
        h3 = y_section - self.h_onderkant_deklaag

        self.df_deklaag["Situatie"] = None
        self.df_deklaag["Dikte effectieve deklaag [m]"] = None
        for i in range(len(h3)):
            if self.h_slootbodem[i] <= self.h_onderkant_deklaag[i]:
                self.df_deklaag["Situatie"].iat[i] = "sloot doorsnijdt deklaag"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = 0
            elif h1[i] > self.breedte_sloot[i]:
                self.df_deklaag["Situatie"].iat[i] = "H1"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h1[i]
            elif h2[i] < self.breedte_slootbodem[i]:
                self.df_deklaag["Situatie"].iat[i] = "H2"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h2[i]
            else:
                self.df_deklaag["Situatie"].iat[i] = "H3"
                self.df_deklaag["Dikte effectieve deklaag [m]"].iat[i] = h3[i]

        return self.df_deklaag
