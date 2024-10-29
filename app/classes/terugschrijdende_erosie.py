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
class Terugschr_erosie(DikeGeometry):
    def __init__(self, dikegeometry, gdf_dike_geometry, traject_par, general_par):
        self.gdf_dike_geometry = gdf_dike_geometry
        self.traject_par = traject_par
        self.general_par = general_par
        self.deklagen = dikegeometry.deklagen
        self.kwelweglengte = dikegeometry.kwelweglengte

        self.kwelweglengte_te_gebruiken = self._calc_kwelweglengte_gebruiken()
        self.grensevenwicht_zandkorrels = self._calc_grensevenwicht_zandkorrels()
        self.schaling_processen = self._calc_schaling_processen()
        self.geometrie_invloed = self._calc_geometrie_invloed()
        self.kritiek_sth_verschil_over_kering = self._calc_kritiek_sth_verschil_over_kering()
        self.optredende_sth_verschil_over_kering = self._calc_optredende_sth_verschil_over_kering()
        self.fos_terugschrijdende_erosie = self._fos_terugschrijdende_erosie()

    def _calc_kwelweglengte_gebruiken(self):
        df_kwelweglengte_gebruiken = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "fictieve kwelweglengte [m]": self.kwelweglengte["fictieve kwelweglengte [m]"],
                "kwelweg 2x breedte dijklichaam [m]": self.kwelweglengte["kwelweg 2x breedte dijklichaam [m]"],
            }
        )

        df_kwelweglengte_gebruiken.loc[
            df_kwelweglengte_gebruiken["kwelweg 2x breedte dijklichaam [m]"]
            <= df_kwelweglengte_gebruiken["fictieve kwelweglengte [m]"],
            "kwelweglengte te gebruiken [m]",
        ] = df_kwelweglengte_gebruiken["kwelweg 2x breedte dijklichaam [m]"]
        df_kwelweglengte_gebruiken.loc[
            df_kwelweglengte_gebruiken["kwelweg 2x breedte dijklichaam [m]"]
            > df_kwelweglengte_gebruiken["fictieve kwelweglengte [m]"],
            "kwelweglengte te gebruiken [m]",
        ] = df_kwelweglengte_gebruiken["fictieve kwelweglengte [m]"]

        return df_kwelweglengte_gebruiken

    def _calc_grensevenwicht_zandkorrels(self):
        g_w = self.general_par.loc["g_w", "Waarde"]
        theta = self.general_par.loc["theta", "Waarde"]
        eta = self.general_par.loc["eta", "Waarde"]
        gamma_p = self.general_par.loc["gamma_p", "Waarde"]

        df_grensevenwicht_zandkorrels = pd.DataFrame({"Vaknr": self.gdf_dike_geometry["Vaknr"]})
        df_grensevenwicht_zandkorrels["grensevenwicht zandkorrels [kN]"] = (
            (gamma_p / g_w) * eta * np.tan(theta * np.pi / 180)
        )

        return df_grensevenwicht_zandkorrels

    def _calc_schaling_processen(self):
        nu = self.general_par.loc["nu", "Waarde"]
        g = self.general_par.loc["g", "Waarde"]
        d_70m = self.general_par.loc["d_70m", "Waarde"]

        df_schaling_processen = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "k_zandlaag [m/s]": self.gdf_dike_geometry["k_zandlaag [m/s]"],
                "d_70 [mm]": self.gdf_dike_geometry["d_70 [mm]"],
            }
        )

        df_schaling_processen["intrinsieke doorlatendheid [m2]"] = nu * df_schaling_processen["k_zandlaag [m/s]"] / g
        df_schaling_processen["schaling processen [kN]"] = (
            d_70m
            / (
                df_schaling_processen["kwelweglengte te gebruiken [m]"]
                * df_schaling_processen["intrinsieke doorlatendheid [m2]"]
            )
            ** (1 / 3)
            * ((df_schaling_processen["d_70 [mm]"] / 1000) / d_70m) ** 0.4
        )

        return df_schaling_processen

    def _calc_geometrie_invloed(self):
        df_geometrie_invloed = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "D_watervoerend_pakket [m]": self.gdf_dike_geometry["D_watervoerend_pakket [m]"],
            }
        )

        df_geometrie_invloed["geometrie invloed [kN]"] = 0.91 * (
            self.gdf_dike_geometry["D_watervoerend_pakket [m]"] / df_geometrie_invloed["kwelweglengte te gebruiken [m]"]
        ) ** (
            0.28
            / (
                (
                    self.gdf_dike_geometry["D_watervoerend_pakket [m]"]
                    / df_geometrie_invloed["kwelweglengte te gebruiken [m]"]
                )
                ** 2.8
                - 1
            )
            + 0.04
        )

        return df_geometrie_invloed

    def _calc_kritiek_sth_verschil_over_kering(self):
        df_kritiek_sth_verschil_over_kering = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "grensevenwicht zandkorrels [kN]": self.grensevenwicht_zandkorrels["grensevenwicht zandkorrels [kN]"],
                "schaling processen [kN]": self.schaling_processen["schaling processen [kN]"],
                "geometrie invloed [kN]": self.geometrie_invloed["geometrie invloed [kN]"],
                "sterktefactor": self.gdf_dike_geometry["sterktefactor"],
            }
        )

        df_kritiek_sth_verschil_over_kering["kritiek sth verschil over kering [m]"] = (
            df_kritiek_sth_verschil_over_kering["sterktefactor"]
            * df_kritiek_sth_verschil_over_kering["kwelweglengte te gebruiken [m]"]
            * df_kritiek_sth_verschil_over_kering["grensevenwicht zandkorrels [kN]"]
            * df_kritiek_sth_verschil_over_kering["schaling processen [kN]"]
            * df_kritiek_sth_verschil_over_kering["geometrie invloed [kN]"]
        )

        return df_kritiek_sth_verschil_over_kering

    def _calc_optredende_sth_verschil_over_kering(self):
        r_c = self.general_par.loc["r_c", "Waarde"]
        df_optr_sth_verschil_over_kering = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "h_buitenwaterstand [mNAP]": self.gdf_dike_geometry["h_buitenwaterstand [mNAP]"],
                "h_exit [mNAP]": self.gdf_dike_geometry["h_exit [mNAP]"],
                "D effectieve deklaag [m]": self.deklagen["D effectieve deklaag [m]"],
            }
        )

        df_optr_sth_verschil_over_kering["Optredende stijghoogte verschil over kering [m]"] = (
            df_optr_sth_verschil_over_kering["h_buitenwaterstand [mNAP]"]
            - df_optr_sth_verschil_over_kering["h_exit [mNAP]"]
            - (r_c * df_optr_sth_verschil_over_kering["D effectieve deklaag [m]"])
        )

        df_optr_sth_verschil_over_kering.loc[
            df_optr_sth_verschil_over_kering["Optredende stijghoogte verschil over kering [m]"] <= 0,
            "Optredende stijghoogte verschil over kering [m]",
        ] = (
            1 / 10
        )

        return df_optr_sth_verschil_over_kering

    def _fos_terugschrijdende_erosie(self):
        df_fos_terugschrijdende_erosie = pd.DataFrame(
            {
                "Vaknr": self.gdf_dike_geometry["Vaknr"],
                "kritiek sth verschil over kering [m]": self.kritiek_sth_verschil_over_kering[
                    "kritiek sth verschil over kering [m]"
                ],
                "Optredende stijghoogte verschil over kering [m]": self.optredende_sth_verschil_over_kering[
                    "Optredende stijghoogte verschil over kering [m]"
                ],
            }
        )

        df_fos_terugschrijdende_erosie["FoS terugschrijdende erosie"] = (
            df_fos_terugschrijdende_erosie["kritiek sth verschil over kering [m]"]
            / df_fos_terugschrijdende_erosie["Optredende stijghoogte verschil over kering [m]"]
        )

        return df_fos_terugschrijdende_erosie


checker = Terugschr_erosie(DikeGeometry(df_dike_geometry), df_dike_geometry, df_traject_par, df_general_par)

display(checker.fos_terugschrijdende_erosie)
