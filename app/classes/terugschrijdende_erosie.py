import numpy as np
import pandas as pd


# TODO faalkans voor deelmech wordt hier niet uitgerekend, maar kans is dat dit via de PTK tool gaat
class Terugschr_erosie:

    def __init__(self, dikegeometry, general_par):
        self.kwelweglengte_te_gebruiken = self._calc_kwelweglengte_gebruiken(dikegeometry)
        self.grensevenwicht_zandkorrels = self._calc_grensevenwicht_zandkorrels(dikegeometry, general_par)
        self.schaling_processen = self._calc_schaling_processen(dikegeometry, general_par)
        self.geometrie_invloed = self._calc_geometrie_invloed(dikegeometry)
        self.kritiek_sth_verschil_over_kering = self._calc_kritiek_sth_verschil_over_kering(dikegeometry)
        self.optredende_sth_verschil_over_kering = self._calc_optredende_sth_verschil_over_kering(
            dikegeometry, general_par
        )
        self.fos_terugschrijdende_erosie = self._fos_terugschrijdende_erosie(dikegeometry)

    def _calc_kwelweglengte_gebruiken(self, dikegeometry):
        df_kwelweglengte_gebruiken = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "fictieve kwelweglengte [m]": dikegeometry.kwelweglengte["fictieve kwelweglengte [m]"],
                "kwelweg 2x breedte dijklichaam [m]": dikegeometry.kwelweglengte["kwelweg 2x breedte dijklichaam [m]"],
            }
        )
        # TODO functie "at" werkt hier niet wegens opbouw
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

    def _calc_grensevenwicht_zandkorrels(self, dikegeometry, general_par):
        g_w = general_par.loc["g_w", "Waarde"]
        theta = general_par.loc["theta", "Waarde"]
        eta = general_par.loc["eta", "Waarde"]
        gamma_p = general_par.loc["gamma_p", "Waarde"]

        df_grensevenwicht_zandkorrels = pd.DataFrame({"Vaknr": dikegeometry.vaknr})
        df_grensevenwicht_zandkorrels["grensevenwicht zandkorrels [kN]"] = (
            (gamma_p / g_w) * eta * np.tan(theta * np.pi / 180)
        )

        return df_grensevenwicht_zandkorrels

    def _calc_schaling_processen(self, dikegeometry, general_par):
        nu = general_par.loc["nu", "Waarde"]
        g = general_par.loc["g", "Waarde"]
        d_70m = general_par.loc["d_70m", "Waarde"]

        df_schaling_processen = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "k_zandlaag [m/s]": dikegeometry.doorlatendheid_watervoerend,
                "d_70 [mm]": dikegeometry.d_70_watervoerend_pakket,
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

    def _calc_geometrie_invloed(self, dikegeometry):
        df_geometrie_invloed = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "D_watervoerend_pakket [m]": dikegeometry.dikte_watervoerend_pakket,
            }
        )

        df_geometrie_invloed["geometrie invloed [kN]"] = 0.91 * (
            df_geometrie_invloed["D_watervoerend_pakket [m]"] / df_geometrie_invloed["kwelweglengte te gebruiken [m]"]
        ) ** (
            0.28
            / (
                (
                    df_geometrie_invloed["D_watervoerend_pakket [m]"]
                    / df_geometrie_invloed["kwelweglengte te gebruiken [m]"]
                )
                ** 2.8
                - 1
            )
            + 0.04
        )

        return df_geometrie_invloed

    def _calc_kritiek_sth_verschil_over_kering(self, dikegeometry):
        df_kritiek_sth_verschil_over_kering = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "kwelweglengte te gebruiken [m]": self.kwelweglengte_te_gebruiken["kwelweglengte te gebruiken [m]"],
                "grensevenwicht zandkorrels [kN]": self.grensevenwicht_zandkorrels["grensevenwicht zandkorrels [kN]"],
                "schaling processen [kN]": self.schaling_processen["schaling processen [kN]"],
                "geometrie invloed [kN]": self.geometrie_invloed["geometrie invloed [kN]"],
                "sterktefactor": dikegeometry.sterktefactor,
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

    def _calc_optredende_sth_verschil_over_kering(self, dikegeometry, general_par):
        r_c = general_par.loc["r_c", "Waarde"]
        df_optr_sth_verschil_over_kering = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
                "h_buitenwaterstand [mNAP]": dikegeometry.h_buitenwaterstand,
                "h_exit [mNAP]": dikegeometry.h_exit,
                "Dikte effectieve deklaag [m]": dikegeometry.effectieve_deklaag["Dikte effectieve deklaag [m]"],
            }
        )

        df_optr_sth_verschil_over_kering["Optredende stijghoogte verschil over kering [m]"] = (
            df_optr_sth_verschil_over_kering["h_buitenwaterstand [mNAP]"]
            - df_optr_sth_verschil_over_kering["h_exit [mNAP]"]
            - (r_c * df_optr_sth_verschil_over_kering["Dikte effectieve deklaag [m]"])
        )

        # TODO functie "at" werkt niet met opbouw zoals deze hieronder is neergezet. Omgooien?
        df_optr_sth_verschil_over_kering.loc[
            df_optr_sth_verschil_over_kering["Optredende stijghoogte verschil over kering [m]"] <= 0,
            "Optredende stijghoogte verschil over kering [m]",
        ] = (
            1 / 10
        )

        return df_optr_sth_verschil_over_kering

    def _fos_terugschrijdende_erosie(self, dikegeometry):
        df_fos_terugschrijdende_erosie = pd.DataFrame(
            {
                "Vaknr": dikegeometry.vaknr,
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
