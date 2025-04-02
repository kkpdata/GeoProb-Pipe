"""Python module for the calculation of the limit state function for piping, heave and uplift in a sand layer with a cover layer."""

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


def calc_Z_combin_piping(X: List[float]) -> List[float]:
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
    [
        dist_L_geom,
        dist_BUT,
        dist_BIT,
        L3_geom,
        mv,
        pp,
        top_zand,
        gamma_sat_cover,
        gamma_w,
        kD,
        D,
        d70,
        c_1,
        c_3,
        mu,
        mh,
        mp,
        i_c_h,
        rc,
        h,
    ] = X

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

    return [Dcover,h_exit,d_pot_c_u,dhred,k,r_exit,pot_exit,L_kwelweg,i_optredend,dhc,Z_u,Z_h,Z_p,Z_combin]
    


def Z_u(X: List[float]) -> float:
    r"""Grenstoestandfunctie voor uplift.

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
        Z_u (float): limit state uplift [-]
    """

    return calc_Z_combin_piping(X)[10]


def Z_h(X: List[float]) -> float:
    r"""Grenstoestandfunctie voor uplift.

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
        Z_u (float): limit state uplift [-]
    """
    return calc_Z_combin_piping(X)[11]


def Z_p(X: List[float]) -> float:
    r"""Grenstoestandfunctie voor uplift.

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
        Z_u (float): limit state uplift [-]
    """
    return calc_Z_combin_piping(X)[12]
