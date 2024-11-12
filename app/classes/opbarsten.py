import pandas as pd


# TODO faalkans voor deelmech wordt hier niet uitgerekend, maar kans is dat dit via de PTK tool gaat
class Opbarsten:

    def __init__(self, dikegeometry, gdf_dike_geometry, traject_par, general_par):
        self.kritiek_stijgh_verschil = self._kritiek_stijgh_verschil(dikegeometry, gdf_dike_geometry)
        # self.optr_stijgh_verschil = self._optr_stijgh_verschil()
        # self.fos_opbarsten = self._fos_opbarsten()

    # TODO in volgende functie moet er rekening mee gehouden worden dat deklagen vanaf maaiveld worden opgegeven
    # TODO unieke code aan grondlaag hangen, anders gaat het mis. (veen en kleiig veen)
    # TODO voor nu wordt nog gdf_dikegeometry gebruikt, moet weg als tupple format hiervoor bekend is. (zie ook fragility_curve.py)
    def _kritiek_stijgh_verschil(self, dikegeometry, gdf_dike_geometry):
        h_bovenkant_deklaag = (
            dikegeometry.h_onderkant_deklaag + dikegeometry.effectieve_deklaag["Dikte effectieve deklaag [m]"]
        )

        df_kritiek_stijgh_verschil = pd.DataFrame({"Vaknr": dikegeometry.vaknr, "h_bk_deklaag": h_bovenkant_deklaag})

        for i in range(dikegeometry.max_number_soil_layers_in_deklaag):
            # for i in range(1):
            df_kritiek_stijgh_verschil[f"h_start_grondlaag_{i+1} [mNAP]"] = gdf_dike_geometry[
                f"h_start_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"h_eind_grondlaag_{i+1} [mNAP]"] = gdf_dike_geometry[
                f"h_eind_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"materiaal_grondlaag_{i+1}"] = gdf_dike_geometry[f"materiaal_grondlaag_{i+1}"]
            df_kritiek_stijgh_verschil[f"materiaal_grondlaag_{i+1}"] = df_kritiek_stijgh_verschil[
                f"materiaal_grondlaag_{i+1}"
            ].fillna("geen materiaal")

        # # TODO vanaf hier gaat het mis, geen idee wat hier mis gaat
        # df_kritiek_stijgh_verschil.loc[
        #     df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
        #     "d_kritiek_stijgh_versch_laag_1 [m]",
        # ] = 2
        # # df_kritiek_stijgh_verschil.loc[
        # #     df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
        # #     f"d_kritiek_stijgh_versch_laag_1 [m]",
        # # ] = 10
        # # df_kritiek_stijgh_verschil.loc[
        # #     df_kritiek_stijgh_verschil[f"h_start_grondlaag_1 [mNAP]"] > df_kritiek_stijgh_verschil["h_bk_deklaag"],
        # #     f"d_kritiek_stijgh_versch_laag_1 [m]",
        # # ] = 20

        # # self.effectieve_deklaag[f"deklaag_{1} [m]"]

        # # for i in range(self.max_number_soil_layers):
        # #     df_kritiek_stijgh_verschil.loc[
        # #         df_kritiek_stijgh_verschil[f"h_start_grondlaag_{i+1} [mNAP]"]
        # #         <= df_kritiek_stijgh_verschil["h_bk_deklaag"],
        # #         f"d_kritiek_stijgh_versch_laag_{i+1} [m]",
        # #     ] = self.effectieve_deklaag[f"deklaag_{i+1} [m]"]
        # #     for j in range(self.gdf_dike_geometry.shape[0]):
        # #         for k in range(self.traject_par.shape[0]):
        # #             if self.traject_par.index.str.contains(
        # #                 df_kritiek_stijgh_verschil.loc[j, f"materiaal_grondlaag_{self.max_number_soil_layers-i}"]
        # #             )[k]:
        # #                 df_kritiek_stijgh_verschil.loc[
        # #                     j, f"d_kritiek_stijgh_versch_laag_{self.max_number_soil_layers-i} [m]"
        # #                 ] = df_kritiek_stijgh_verschil.loc[
        # #                     j, f"d_kritiek_stijgh_versch_laag_{self.max_number_soil_layers-i} [m]"
        # #                 ] * (
        # #                     self.traject_par.iloc[k, 0] - self.general_par.loc["g_w", "Waarde"]
        # #                 )

        # # df_kritiek_stijgh_verschil["d_kritiek_stijgh_versch [mNAP]"] = (
        # #     df_kritiek_stijgh_verschil.filter(like="d_kritiek_stijgh_versch_laag").sum(axis=1)
        # #     / self.general_par.loc["g_w", "Waarde"]
        # # )

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
