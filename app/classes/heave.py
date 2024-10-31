import sys
from pathlib import Path

import pandas as pd
from dike_geometry import DikeGeometry

# sys.path.append(str(Path(__file__).parents[1]))   Add repo to sys.path to make sure all imports are correctly found

# # tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
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
        self.i_toelaatbaar = general_par.loc["i_toelaatbaar", "Waarde"]
        self.effectieve_deklaag = dikegeometry.effectieve_deklaag

        self.optr_heavegradient = self._optr_heavegradient()
        self.fos_heave = self._fos_heave()

    def _optr_heavegradient(self):
        df_optr_heavegradient = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "h_buitenwaterstand [mNAP]": self.gdf_dike_geometry["h_buitenwaterstand [mNAP]"],
                "h_exit [mNAP]": self.gdf_dike_geometry["h_exit [mNAP]"],
                "r [-]": self.gdf_dike_geometry["r [-]"],
                "Dikte effectieve deklaag [m]": self.effectieve_deklaag["Dikte effectieve deklaag [m]"],
            }
        )

        df_optr_heavegradient["r [-]"].mask(df_optr_heavegradient["r [-]"] <= 0, 0.1, inplace=True)

        for i in range(self.gdf_dike_geometry.shape[0]):
            if df_optr_heavegradient.loc[i, "Dikte effectieve deklaag [m]"] <= 0:
                df_optr_heavegradient.loc[i, "optr_heavegradient [-]"] = 10
            else:
                df_optr_heavegradient.loc[i, "optr_heavegradient [-]"] = (
                    (
                        df_optr_heavegradient.loc[i, "h_buitenwaterstand [mNAP]"]
                        - df_optr_heavegradient.loc[i, "h_exit [mNAP]"]
                    )
                    * df_optr_heavegradient.loc[i, "r [-]"]
                    / df_optr_heavegradient.loc[i, "Dikte effectieve deklaag [m]"]
                )

        return df_optr_heavegradient

    def _fos_heave(self):

        df_fos_heave = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "Dikte effectieve deklaag [m]": self.effectieve_deklaag["Dikte effectieve deklaag [m]"],
                "optr_heavegradient [-]": self.optr_heavegradient["optr_heavegradient [-]"],
            }
        )

        df_fos_heave.loc[df_fos_heave["Dikte effectieve deklaag [m]"] <= 0, "FoS tegen heave"] = 0
        df_fos_heave.loc[df_fos_heave["Dikte effectieve deklaag [m]"] > 0, "FoS tegen heave"] = (
            self.i_toelaatbaar / df_fos_heave["optr_heavegradient [-]"]
        )

        return df_fos_heave


checker_class = Heave(DikeGeometry(df_dike_geometry), df_dike_geometry, df_traject_par, df_general_par)


checker_class.fos_heave
