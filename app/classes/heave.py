import pandas as pd
from dike_geometry import DikeGeometry


# TODO faalkans voor deelmech wordt hier niet uitgerekend, maar kans is dat dit via de PTK tool gaat
class Heave:

    def __init__(self, dikegeometry, i_toelaatbaar):
        self.optr_heavegradient = self._optr_heavegradient(dikegeometry)
        self.fos_heave = self._fos_heave(dikegeometry, i_toelaatbaar)

    def _optr_heavegradient(self, dikegeometry):
        df_optr_heavegradient = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "h_buitenwaterstand [mNAP]": dikegeometry.h_buitenwaterstand,
                "h_exit [mNAP]": dikegeometry.h_exit,
                "r [-]": dikegeometry.r_factor,
                "Dikte effectieve deklaag [m]": dikegeometry.effectieve_deklaag["Dikte effectieve deklaag [m]"],
            }
        )
        df_optr_heavegradient["r [-]"].mask(df_optr_heavegradient["r [-]"] <= 0, 0.1, inplace=True)

        for i in range(df_optr_heavegradient.shape[0]):
            if df_optr_heavegradient.at[i, "Dikte effectieve deklaag [m]"] <= 0:
                df_optr_heavegradient.at[i, "optr_heavegradient [-]"] = 10
            else:
                df_optr_heavegradient.at[i, "optr_heavegradient [-]"] = (
                    (
                        df_optr_heavegradient.at[i, "h_buitenwaterstand [mNAP]"]
                        - df_optr_heavegradient.at[i, "h_exit [mNAP]"]
                    )
                    * df_optr_heavegradient.at[i, "r [-]"]
                    / df_optr_heavegradient.at[i, "Dikte effectieve deklaag [m]"]
                )

        return df_optr_heavegradient

    def _fos_heave(self, dikegeometry, i_toelaatbaar):

        df_fos_heave = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "Dikte effectieve deklaag [m]": dikegeometry.effectieve_deklaag["Dikte effectieve deklaag [m]"],
                "optr_heavegradient [-]": self.optr_heavegradient["optr_heavegradient [-]"],
            }
        )

        df_fos_heave.loc[df_fos_heave["Dikte effectieve deklaag [m]"] <= 0, "FoS tegen heave"] = 0
        df_fos_heave.loc[df_fos_heave["Dikte effectieve deklaag [m]"] > 0, "FoS tegen heave"] = (
            i_toelaatbaar / df_fos_heave["optr_heavegradient [-]"]
        )

        return df_fos_heave
