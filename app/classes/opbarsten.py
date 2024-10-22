import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from dike_geometry import DikeGeometry

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

# tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
# df_dike_geometry = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_vak_par",
# )

# df_traject_par = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_traject_par",
#     index_col="Parameter",
# )

# df_general_par = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_gen_par",
#     index_col="Parameter",
# )


# TODO faalkans voor deelmech wordt hier niet uitgerekend, maar kans is dat dit via de PTK tool gaat
class Opbarsten(DikeGeometry):

    def __init__(self, dikegeometry, gdf_dike_geometry, traject_par, general_par):
        self.gdf_dike_geometry = gdf_dike_geometry
        self.traject_par = traject_par
        self.general_par = general_par
        self.deklagen = dikegeometry.deklagen

        self.max_number_soil_layers = self._count_max_number_soil_layers()
        self.kritiek_stijgh_verschil = self._kritiek_stijgh_verschil()
        self.optr_stijgh_verschil = self._optr_stijgh_verschil()
        self.fos_tegen_opbarsten = self._fos_tegen_opbarsten()

    # TODO Ik kom er niet achter waarom deze niet uit de class DikeGeometry gecalled kan worden dus opnieuw gemaakt
    def _count_max_number_soil_layers(self):
        count_max_soil_layers = sum(["h_start_grondlaag_" in col for col in self.gdf_dike_geometry])
        return count_max_soil_layers

    # TODO in volgende functie moet er rekening mee gehouden worden dat deklagen vanaf maaiveld worden opgegeven
    # TODO unieke code aan grondlaag hangen, anders gaat het mis. (veen en kleiig veen)
    def _kritiek_stijgh_verschil(self):
        self.h_bk_deklaag = round(
            self.gdf_dike_geometry["h_ok_deklaag [mNAP]"] + self.deklagen["D effectieve deklaag [m]"], 2
        )
        n_max_soil_layers = self.max_number_soil_layers
        n_soiltype_search = self.traject_par.shape[0]
        n_length_gdf = self.gdf_dike_geometry.shape[0]

        df_kritiek_stijgh_verschil = pd.DataFrame()
        df_kritiek_stijgh_verschil["Vaknr"] = self.gdf_dike_geometry["Vaknr"]

        for i in range(n_max_soil_layers):
            df_kritiek_stijgh_verschil[f"h_start_grondlaag_{i+1} [mNAP]"] = self.gdf_dike_geometry[
                f"h_start_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"h_eind_grondlaag_{i+1} [mNAP]"] = self.gdf_dike_geometry[
                f"h_eind_grondlaag_{i+1} [mNAP]"
            ]
            df_kritiek_stijgh_verschil[f"materiaal_grondlaag_{i+1}"] = self.gdf_dike_geometry[
                f"materiaal_grondlaag_{i+1}"
            ]
            df_kritiek_stijgh_verschil[[f"materiaal_grondlaag_{i+1}"]] = df_kritiek_stijgh_verschil[
                [f"materiaal_grondlaag_{i+1}"]
            ].fillna("geen materiaal")

        for i in range(n_max_soil_layers):
            df_kritiek_stijgh_verschil.loc[
                df_kritiek_stijgh_verschil[f"h_start_grondlaag_{n_max_soil_layers - i} [mNAP]"]
                <= self.h_bk_deklaag,
                f"d_kritiek_stijgh_versch_laag_{n_max_soil_layers - i} [m]",
            ] = self.deklagen[f"deklaag_{n_max_soil_layers-i} [m]"]
            for j in range(n_length_gdf):
                for k in range(n_soiltype_search):
                    if self.traject_par.index.str.contains(
                        df_kritiek_stijgh_verschil.loc[j, f"materiaal_grondlaag_{n_max_soil_layers-i}"]
                    )[k]:
                        df_kritiek_stijgh_verschil.loc[
                            j, f"d_kritiek_stijgh_versch_laag_{n_max_soil_layers-i} [m]"
                        ] = df_kritiek_stijgh_verschil.loc[
                            j, f"d_kritiek_stijgh_versch_laag_{n_max_soil_layers-i} [m]"
                        ] * (
                            self.traject_par.iloc[k, 0] - self.general_par.loc["g_w", "Waarde"]
                        )

        df_kritiek_stijgh_verschil["d_kritiek_stijgh_versch [mNAP]"] = (
            df_kritiek_stijgh_verschil.filter(like="d_kritiek_stijgh_versch_laag").sum(axis=1)
            / self.general_par.loc["g_w", "Waarde"]
        )

        return df_kritiek_stijgh_verschil

    def _optr_stijgh_verschil(self):
        df_optr_stijgh_verschil = pd.DataFrame()
        df_optr_stijgh_verschil["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        df_optr_stijgh_verschil["h_buitenwaterstand [mNAP]"] = self.gdf_dike_geometry["h_buitenwaterstand [mNAP]"]
        df_optr_stijgh_verschil["h_exit [mNAP]"] = self.gdf_dike_geometry["h_exit [mNAP]"]
        df_optr_stijgh_verschil["r [-]"] = self.gdf_dike_geometry["r [-]"]
        n_length_gdf = self.gdf_dike_geometry.shape[0]

        df_optr_stijgh_verschil["optr_stijgh_verschil [mNAP]"] = (
            df_optr_stijgh_verschil["h_buitenwaterstand [mNAP]"] - df_optr_stijgh_verschil["h_exit [mNAP]"]
        ) * df_optr_stijgh_verschil["r [-]"]

        for i in range(n_length_gdf):
            if df_optr_stijgh_verschil.loc[i, "optr_stijgh_verschil [mNAP]"] <= 0:
                df_optr_stijgh_verschil.loc[i, "optr_stijgh_verschil [mNAP]"] = 0.1

        return df_optr_stijgh_verschil

    def _fos_tegen_opbarsten(self):
        df_fos_tegen_opbarsten = pd.DataFrame()
        df_fos_tegen_opbarsten["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        df_fos_tegen_opbarsten["d_kritiek_stijgh_versch [mNAP]"] = self.kritiek_stijgh_verschil[
            "d_kritiek_stijgh_versch [mNAP]"
        ]
        df_fos_tegen_opbarsten["optr_stijgh_verschil [mNAP]"] = self.kritiek_stijgh_verschil[
            "optr_stijgh_verschil [mNAP]"
        ]
        df_fos_tegen_opbarsten["FoS_tegen_opbarsten"] = (
            df_fos_tegen_opbarsten["d_kritiek_stijgh_versch [mNAP]"]
            / df_fos_tegen_opbarsten["optr_stijgh_verschil [mNAP]"]
        )

        return df_fos_tegen_opbarsten


# check_script = Opbarsten(DikeGeometry(df_dike_geometry), df_dike_geometry, df_traject_par, df_general_par)

# display(check_script.fos_tegen_opbarsten)
