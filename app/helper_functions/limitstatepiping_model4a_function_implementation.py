"""Python module for the calculation of the limit state function for piping, heave and uplift in a sand layer with a cover layer."""

import math
from dataclasses import dataclass
from typing import List

from app.helper_functions import geohydro_functions, model4a, piping_functions

# Define the input variables for the functions for Uplift, Heave and Piping
# dist_L_geom: float
# dist_BUT: float
# dist_BIT: float
# L3_geom: float
# mv: float
# pp: float
# top_zand: float
# gamma_sat_cover: float
# gamma_w: float
# kD: float
# D: float
# d70: float
# c1: float
# c3: float
# mu: float
# mh: float
# mp: float
# i_c_h: float
# rc: float
# h: float


def Zu(
    L_intrede, L_BUT, k, D, c1, c3, L3, WS, PP, L_BIT, d_dek, y_satdek, y_water, MV, mu
):
    L1 = L_intrede - L_BUT
    lam1 = np.sqrt(k * D * c1)
    lam3 = np.sqrt(k * D * c3)
    Φ1 = PP + (WS - PP) * (L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)) / (
        lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
    )
    Φ2 = PP + (WS - PP) * lam3 * math.tanh(L3 / lam3) / (
        lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
    )
    Φ_uittrede = PP + (Φ2 - PP) * (math.sinh((L3 - L_BIT) / lam3)) / math.sinh(
        L3 / lam3
    )
    h_exit = max(PP, MV)
    dΦ = Φ_uittrede - h_exit
    dΦc = d_dek * ((y_satdek - y_water) / y_water)
    Zu = mu * dΦc - dΦ
    return Zu


def Zh(ic, L_intrede, L_BUT, k, D, c1, c3, L3, WS, PP, L_BIT, d_dek, MV):
    L1 = L_intrede - L_BUT
    lam1 = np.sqrt(k * D * c1)
    lam3 = np.sqrt(k * D * c3)
    Φ1 = PP + (WS - PP) * (L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)) / (
        lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
    )
    Φ2 = PP + (WS - PP) * lam3 * math.tanh(L3 / lam3) / (
        lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
    )
    Φ_uittrede = PP + (Φ2 - PP) * (math.sinh((L3 - L_BIT) / lam3)) / math.sinh(
        L3 / lam3
    )
    h_exit = max(PP, MV)
    dΦ = Φ_uittrede - h_exit
    Zh = ic - (dΦ / d_dek)
    return Zh


def Zp(L_intrede, L_BUT, k, D, c1, y_water, d70, mp, WS, d_dek, PP, MV):
    L1 = L_intrede - L_BUT
    lam1 = np.sqrt(k * D * c1)
    w1 = lam1 * math.tanh(L1 / lam1)
    L = w1 + L_BUT
    k_ms = k / (24 * 3600)
    k_intr = (0.00000133 / 9.81) * k_ms
    Fres = 0.25 * ((26.0 - y_water) / y_water) * math.tan(37.0 * math.pi / 180.00)
    Fscale = pow((d70 / 1.0e6) / 2.08e-4, 0.4) * 2.08e-4 / pow(k_intr * L, (1.0 / 3.0))
    if D == L:
        D = D - 0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D / L, 2.8) - 1.0))
    Fgeom = 0.91 * pow(D / L, totdemacht)
    Hc = Fres * Fscale * Fgeom * L
    h_exit = max(PP, MV)
    Zp = (mp * Hc) - (max(0.01, (WS - h_exit - (0.3 * d_dek))))
    return Zp


def calc_Z_combin_piping(
    dist_L_geom: float,
    dist_BUT: float,
    dist_BIT: float,
    L3_geom: float,
    mv: float,
    pp: float,
    top_zand: float,
    gamma_sat_cover: float,
    gamma_w: float,
    kD: float,
    D: float,
    d70: float,
    c_1: float,
    c_3: float,
    mu: float,
    mh: float,
    mp: float,
    i_c_h: float,
    rc: float,
    h: float,
) -> List[float]:
    r"""

    Gecombineerde grenstoestandfunctie voor uplift, heave en piping. De input X is een lijst met de volgende elementen:

    Args:
        X (List[float]): lijst met volgende elementen
            X[0] (float): dist_L_geom: geometrische voorlandlengte in m
            X[1] (float): dist_BUT: afstand tot de buitenteen in m
            X[2] (float): dist_BIT: afstand tot de binnenteen in m
            X[3] (float): L3_geom: geometrische achterlandlengte in m
            X[4] (float): mv: niveau bij het uittredepunt in m+NAP
            X[5] (float): pp: polderpeil in m+NAP
            X[6] (float): top_zand: bovenkant van de zandlaag in m+NAP
            X[7] (float): gamma_sat_cover: verzadigd volumegewicht van de deklaag in kN/m3
            X[8] (float): gamma_w: volumegewicht van water in kN/m3
            X[9] (float): kD: transmissiviteit watervoerend zandpakket in m2/d
            x[10] (float): D: dikte van de watervoerende zandlaag
            X[11] (float): d70: 70% percentiel van de korrelgrootteverdeling in m
            X[12] (float): c_1: weerstand van de deklaag in het voorland in d
            X[13] (float): c_3: weerstand van de deklaag in het achterland in d
            X[14] (float): mu: modelfactor voor uplift
            X[15] (float): mh: modelfactor voor heave
            X[16] (float): mp: modelfactor voor piping
            X[17] (float): i_c_h: kritische heave gradient in [-]
            X[18] (float): rc: reductiefactor van het verval evenredig met de dikte van de deklaag [-]
            X[19] (float): h: buitenwaterstand in m+NAP

    Returns:
        Y (List[float]): lijst me de volgende elementen:
            Y[0] (float): Dcover: deklaagdikte in m
            Y[1] (float): h_exit: niveau uittredepunt m+NAP
            Y[2] (float): d_pot_c_u: grenspotentiaal in m
            Y[3] (float): dhred: gereduceerd verval in m
            Y[4] (float): k: doorlatendheid zandlaag in m/d
            Y[5] (float): r_exit: respons in uittredepunt [-]
            Y[6] (float): pot_exit: potentiaal in uittredepunt in m+NAP
            Y[7] (float): L_kwelweg: kwelweglengte in m
            Y[8] (float): i_optredend: optredend heave gradient in [-]
            Y[9] (float): dhc: kritiek verval Sellmeijer m
            Y[10] (float): Z_u: limit state uplift [-]
            Y[11] (float): Z_h: limit state heave [-]
            Y[12] (float): Z_p: limit state piping [-]
            Y[13] (float): Z_combin: limit state combinatie uplift, heave en piping [-]
    """

    # Berekening deklaagdikte
    Dcover = piping_functions.calc_Dcover(mv, top_zand)

    # Berekening niveau bij het uittredepunt
    h_exit = piping_functions.calc_h_exit(pp, mv)

    # Berekening gereduceerd verval
    dhred = piping_functions.calc_dH_red(h, h_exit, rc, Dcover)

    # Berekening grenspotentiaal
    d_pot_c_u = piping_functions.calc_d_pot_c_u(Dcover, gamma_sat_cover, gamma_w)

    # Berekening geometrische waarden voor potentiaalberekening
    L1 = dist_L_geom - dist_BUT
    L2 = dist_BUT - dist_BIT
    # L3 is al opgegeven

    # potentiaalberekening
    k = kD / D
    # aanroepen functie potentiaalberekening, x_bit = 0.0 zodat we dist_BIT kunnen gebruiken als x)
    pot_model = model4a.Model4a(
        k=k, D=D, c1=c_1, c3=c_3, L1=L1, L3=L3_geom, x_but=(0.0 - L2), x_bit=0.0
    )
    r_exit, r_but, r_bit = pot_model.respons(dist_BIT)
    pot_exit = geohydro_functions.calc_respons2pot(pp, r_exit, h)

    # Kwelweglengte
    L_kwelweg = pot_model.W1 + dist_BUT

    # uplift
    Z_u = piping_functions.calc_Z_u(d_pot_c_u, pot_exit, h_exit, mu)

    # heave
    i_optredend = piping_functions.calc_i_optredend(pot_exit, h_exit, Dcover)
    Z_h = piping_functions.calc_Z_h(i_c_h, i_optredend, mh)

    # piping
    dhc = piping_functions.calc_dH_sellmeijer(d70, k, D, L_kwelweg, gamma_w)
    Z_p = piping_functions.calc_Z_p(dhc, dhred, mp)

    # combinatie
    Z_combin = max(Z_u, Z_h, Z_p)

    return (
        Dcover,
        h_exit,
        d_pot_c_u,
        dhred,
        k,
        r_exit,
        pot_exit,
        L_kwelweg,
        i_optredend,
        dhc,
        Z_u,
        Z_h,
        Z_p,
        Z_combin,
    )


## Class implementation


@dataclass
class LimitStatePipingModel4a:
    r"""
    Class voor het berekenen van de gecombineerde grenstoestandfunctie voor uplift, heave en piping.
    Gebruikt de model4a potentiaalberekening
    """

    dist_L_geom: float
    dist_BUT: float
    dist_BIT: float
    L3_geom: float
    mv: float
    pp: float
    top_zand: float
    gamma_sat_cover: float
    gamma_w: float
    kD: float
    D: float
    d70: float
    c_1: float
    c_3: float
    mu: float
    mh: float
    mp: float
    i_c_h: float
    rc: float
    h: float

    @property
    def Dcover(self) -> float:
        return piping_functions.calc_Dcover(self.mv, self.top_zand)

    @property
    def h_exit(self) -> float:
        return piping_functions.calc_h_exit(self.pp, self.mv)

    @property
    def dhred(self) -> float:
        return piping_functions.calc_dH_red(self.h, self.h_exit, self.rc, self.Dcover)

    @property
    def d_pot_c_u(self) -> float:
        return piping_functions.calc_d_pot_c_u(
            self.Dcover, self.gamma_sat_cover, self.gamma_w
        )

    @property
    def k(self) -> float:
        return self.kD / self.D

    @property
    def r_exit(self) -> float:
        pot_model = model4a.Model4a(
            k=self.k,
            D=self.D,
            c1=self.c_1,
            c3=self.c_3,
            L1=self.dist_L_geom - self.dist_BUT,
            L3=self.L3_geom,
            x_but=(0.0 - (self.dist_BUT - self.dist_BIT)),
            x_bit=0.0,
        )
        r_exit, r_but, r_bit = pot_model.respons(self.dist_BIT)
        return r_exit

    @property
    def pot_exit(self) -> float:
        return geohydro_functions.calc_respons2pot(self.pp, self.r_exit, self.h)

    @property
    def L_kwelweg(self) -> float:
        pot_model = model4a.Model4a(
            k=self.k,
            D=self.D,
            c1=self.c_1,
            c3=self.c_3,
            L1=self.dist_L_geom - self.dist_BUT,
            L3=self.L3_geom,
            x_but=(0.0 - (self.dist_BUT - self.dist_BIT)),
            x_bit=0.0,
        )
        return pot_model.W1 + self.dist_BUT

    @property
    def i_optredend(self) -> float:
        return piping_functions.calc_i_optredend(
            self.pot_exit, self.h_exit, self.Dcover
        )

    @property
    def dhc(self) -> float:
        return piping_functions.calc_dH_sellmeijer(
            self.d70, self.k, self.D, self.L_kwelweg, self.gamma_w
        )

    @property
    def Z_u(self) -> float:
        return piping_functions.calc_Z_u(
            self.d_pot_c_u, self.pot_exit, self.h_exit, self.mu
        )

    @property
    def Z_h(self) -> float:
        return piping_functions.calc_Z_h(self.i_c_h, self.i_optredend, self.mh)

    @property
    def Z_p(self) -> float:
        return piping_functions.calc_Z_p(self.dhc, self.dhred, self.mp)

    @property
    def Z_combin(self) -> float:
        return max(self.Z_u, self.Z_h, self.Z_p)
