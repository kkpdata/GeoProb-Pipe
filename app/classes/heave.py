import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
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
class Heave(DikeGeometry):

    def __init__(self, dikegeometry, gdf_dike_geometry, traject_par, general_par):
        self.gdf_dike_geometry = gdf_dike_geometry
        self.traject_par = traject_par
        self.general_par = general_par
        self.deklagen = dikegeometry.deklagen

        self.optr_heavegradient = self._optr_heavegradient()
        self.fos_tegen_heave = self._fos_tegen_heave()

    def _optr_heavegradient(self):
        self.df_optr_heavegradient = pd.DataFrame()
        self.df_optr_heavegradient["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        self.df_optr_heavegradient["h_buitenwaterstand [mNAP]"] = self.gdf_dike_geometry["h_buitenwaterstand [mNAP]"]
        self.df_optr_heavegradient["h_exit [mNAP]"] = self.gdf_dike_geometry["h_exit [mNAP]"]
        self.df_optr_heavegradient["r [-]"] = self.gdf_dike_geometry["r [-]"]
        self.df_optr_heavegradient["D effectieve deklaag [m]"] = self.deklagen["D effectieve deklaag [m]"]
        n_length_gdf = self.gdf_dike_geometry.shape[0]

        for i in range(n_length_gdf):
            if self.df_optr_heavegradient.loc[i, "r [-]"] <= 0:
                self.df_optr_heavegradient.loc[i, "r [-]"] = 0.1

        for i in range(n_length_gdf):
            if self.df_optr_heavegradient.loc[i, "D effectieve deklaag [m]"] <= 0:
                self.df_optr_heavegradient.loc[i, "optr_heavegradient [-]"] = 10
            else:
                self.df_optr_heavegradient.loc[i, "optr_heavegradient [-]"] = (
                    (
                        self.df_optr_heavegradient.loc[i, "h_buitenwaterstand [mNAP]"]
                        - self.df_optr_heavegradient.loc[i, "h_exit [mNAP]"]
                    )
                    * self.df_optr_heavegradient.loc[i, "r [-]"]
                    / self.df_optr_heavegradient.loc[i, "D effectieve deklaag [m]"]
                )

        return self.df_optr_heavegradient

    def _fos_tegen_heave(self):
        i_c = self.general_par.loc["i_toelaatbaar", "Waarde"]
        self.df_fos_tegen_heave = pd.DataFrame()
        self.df_fos_tegen_heave["Vaknr"] = self.gdf_dike_geometry["Vaknr"]
        self.df_fos_tegen_heave["D effectieve deklaag [m]"] = self.deklagen["D effectieve deklaag [m]"]
        self.df_fos_tegen_heave["optr_heavegradient [-]"] = self.optr_heavegradient["optr_heavegradient [-]"]

        self.df_fos_tegen_heave.loc[self.df_fos_tegen_heave["D effectieve deklaag [m]"] <= 0, "FoS tegen heave"] = 0
        self.df_fos_tegen_heave.loc[self.df_fos_tegen_heave["D effectieve deklaag [m]"] > 0, "FoS tegen heave"] = (
            i_c / self.df_fos_tegen_heave["optr_heavegradient [-]"]
        )

        return self.df_fos_tegen_heave


checkerdecheck = Heave(DikeGeometry(df_dike_geometry), df_dike_geometry, df_traject_par, df_general_par)

checkerdecheck.fos_tegen_heave
