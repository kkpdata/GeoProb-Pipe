import sys
from pathlib import Path

import pandas as pd
from dike_geometry import DikeGeometry

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

# tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
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


# TODO faalkans voor deelmech wordt hier niet uitgerekend, maar kans is dat dit via de PTK tool gaat
class Opbarsten(DikeGeometry):

    def __init__(self, dikegeometry, gdf_dike_geometry, traject_par, general_par):
        self.gdf_dike_geometry = gdf_dike_geometry
        self.traject_par = traject_par
        self.general_par = general_par
        self.effectieve_deklaag = dikegeometry.effectieve_deklaag

        self.max_number_soil_layers = self._count_max_number_soil_layers()
        self.kritiek_stijgh_verschil = self._kritiek_stijgh_verschil()
        # self.optr_stijgh_verschil = self._optr_stijgh_verschil()
        # self.fos_opbarsten = self._fos_opbarsten()

    # TODO Ik kom er niet achter waarom deze niet uit de class DikeGeometry gecalled kan worden dus opnieuw gemaakt
    def _count_max_number_soil_layers(self):
        count_max_soil_layers = sum(["h_start_grondlaag_" in col for col in self.gdf_dike_geometry])
        return count_max_soil_layers

    # TODO in volgende functie moet er rekening mee gehouden worden dat deklagen vanaf maaiveld worden opgegeven
    # TODO unieke code aan grondlaag hangen, anders gaat het mis. (veen en kleiig veen)
    def _kritiek_stijgh_verschil(self):
        h_bk_deklaag = (
            self.gdf_dike_geometry["h_ok_deklaag [mNAP]"] + self.effectieve_deklaag["Dikte effectieve deklaag [m]"]
        )

        df_kritiek_stijgh_verschil = pd.DataFrame(
            {"Vaknr": self.gdf_dike_geometry["Vaknr"], "h_bk_deklaag": h_bk_deklaag}
        )

        # for i in range(self.max_number_soil_layers):
        for i in range(1):
            df_kritiek_stijgh_verschil[f"h_start_grondlaag_{i+1} [mNAP]"] = self.gdf_dike_geometry[
                f"h_start_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"h_eind_grondlaag_{i+1} [mNAP]"] = self.gdf_dike_geometry[
                f"h_eind_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"materiaal_grondlaag_{i+1}"] = self.gdf_dike_geometry[
                f"materiaal_grondlaag_{i+1}"
            ]
            df_kritiek_stijgh_verschil[f"materiaal_grondlaag_{i+1}"] = df_kritiek_stijgh_verschil[
                f"materiaal_grondlaag_{i+1}"
            ].fillna("geen materiaal")

        # TODO vanaf hier gaat het mis, geen idee wat hier mis gaat
        df_kritiek_stijgh_verschil.loc[
            df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
            "d_kritiek_stijgh_versch_laag_1 [m]",
        ] = 2
        # df_kritiek_stijgh_verschil.loc[
        #     df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
        #     f"d_kritiek_stijgh_versch_laag_1 [m]",
        # ] = 10
        # df_kritiek_stijgh_verschil.loc[
        #     df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] > df_kritiek_stijgh_verschil["h_bk_deklaag"],
        #     f"d_kritiek_stijgh_versch_laag_1 [m]",
        # ] = 20

        # self.effectieve_deklaag[f"deklaag_{1} [m]"]

        # for i in range(self.max_number_soil_layers):
        #     df_kritiek_stijgh_verschil.loc[
        #         df_kritiek_stijgh_verschil[f"h_start_grondlaag_{i+1} [mNAP]"]
        #         <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
        #         f"d_kritiek_stijgh_versch_laag_{i+1} [m]",
        #     ] = self.effectieve_deklaag[f"deklaag_{i+1} [m]"]
        #     for j in range(self.gdf_dike_geometry.shape[0]):
        #         for k in range(self.traject_par.shape[0]):
        #             if self.traject_par.index.str.contains(
        #                 df_kritiek_stijgh_verschil.loc[j, f"materiaal_grondlaag_{self.max_number_soil_layers-i}"]
        #             )[k]:
        #                 df_kritiek_stijgh_verschil.loc[
        #                     j, f"d_kritiek_stijgh_versch_laag_{self.max_number_soil_layers-i} [m]"
        #                 ] = df_kritiek_stijgh_verschil.loc[
        #                     j, f"d_kritiek_stijgh_versch_laag_{self.max_number_soil_layers-i} [m]"
        #                 ] * (
        #                     self.traject_par.iloc[k, 0] - self.general_par.loc["g_w", "Waarde"]
        #                 )

        # df_kritiek_stijgh_verschil["d_kritiek_stijgh_versch [mNAP]"] = (
        #     df_kritiek_stijgh_verschil.filter(like="d_kritiek_stijgh_versch_laag").sum(axis=1)
        #     / self.general_par.loc["g_w", "Waarde"]
        # )

        return df_kritiek_stijgh_verschil

    # def _optr_stijgh_verschil(self):
    #     df_optr_stijgh_verschil = pd.DataFrame(
    #         {
    #             "Vaknr": self.gdf_dike_geometry["Vaknr"],
    #             "h_buitenwaterstand [mNAP]": self.gdf_dike_geometry["h_buitenwaterstand [mNAP]"],
    #             "h_exit [mNAP]": self.gdf_dike_geometry["h_exit [mNAP]"],
    #             "r [-]": self.gdf_dike_geometry["r [-]"],
    #         }
    #     )

    #     df_optr_stijgh_verschil["optr_stijgh_verschil [mNAP]"] = (
    #         df_optr_stijgh_verschil["h_buitenwaterstand [mNAP]"] - df_optr_stijgh_verschil["h_exit [mNAP]"]
    #     ) * df_optr_stijgh_verschil["r [-]"]

    #     for i in range(self.gdf_dike_geometry.shape[0]):
    #         if df_optr_stijgh_verschil.loc[i, "optr_stijgh_verschil [mNAP]"] <= 0:
    #             df_optr_stijgh_verschil.loc[i, "optr_stijgh_verschil [mNAP]"] = 0.1

    #     return df_optr_stijgh_verschil

    # def _fos_opbarsten(self):
    #     df_fos_opbarsten = pd.DataFrame(
    #         {
    #             "Vaknr": self.gdf_dike_geometry["Vaknr"],
    #             "d_kritiek_stijgh_versch [mNAP]": self.kritiek_stijgh_verschil["d_kritiek_stijgh_versch [mNAP]"],
    #             "optr_stijgh_verschil [mNAP]": self.kritiek_stijgh_verschil["optr_stijgh_verschil [mNAP]"],
    #         }
    #     )

    #     df_fos_opbarsten["FoS_tegen_opbarsten"] = (
    #         df_fos_opbarsten["d_kritiek_stijgh_versch [mNAP]"] / df_fos_opbarsten["optr_stijgh_verschil [mNAP]"]
    #     )

    #     return df_fos_opbarsten


check_script = Opbarsten(DikeGeometry(df_dike_geometry), df_dike_geometry, df_traject_par, df_general_par)

display(check_script.kritiek_stijgh_verschil)
