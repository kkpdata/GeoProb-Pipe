"""Python module for the calculation of the limit state function for piping, heave and uplift in a sand layer with a cover layer."""

import math
from dataclasses import dataclass
from typing import List

from geoprob_pipe.helper_functions import geohydro_functions, model4a, piping_functions_old

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

# def Z_u(dist_L_geom: float,dist_BUT: float,dist_BIT: float,L3_geom: 
#         float,mv: float,pp: float,top_zand: float,gamma_sat_cover: float,
#         gamma_w: float,kD: float,D: float,c_1: float,c_3: float,mu: float,
#         h: float) -> float:
#     r"""Calculate the uplift limit state function."""
#     # Calculate the geometrical values for potential calculation
#     L1 = dist_L_geom - dist_BUT
#     L2 = dist_BUT - dist_BIT

#     # Potential calculation
#     k = kD / D
#     # Call the potential calculation function with x_bit=0.0 to use dist_BIT as x
#     pot_model = model4a.Model4a(
#             k=k, D=D, c1=c_1, c3=c_3, L1=L1, L3=L3_geom, x_but=(0.0 - L2), x_bit=0.0
#         )
#     r_exit, r_but, r_bit = pot_model.respons(dist_BIT)
#     pot_exit = geohydro_functions.calc_respons2pot(pp, r_exit, h)

#     # Calculate the h_exit
#     h_exit = piping_functions.calc_h_exit(pp, mv)

#     # Calculate the deklaagdikte
#     Dcover = piping_functions.calc_Dcover(mv, top_zand)

#     # Calculate the critical potential
#     d_pot_c_u = piping_functions.calc_d_pot_c_u(Dcover, gamma_sat_cover, gamma_w)

#     # Calculate the uplift limit state function
#     Zu = piping_functions.calc_Z_u(d_pot_c_u, pot_exit, h_exit, mu)
#     return Zu


# def Zu(
#     L_intrede, L_BUT, k, D, c1, c3, L3, WS, PP, L_BIT, d_dek, y_satdek, y_water, MV, mu
# ):
#     L1 = L_intrede - L_BUT
#     lam1 = np.sqrt(k * D * c1)
#     lam3 = np.sqrt(k * D * c3)
#     Φ1 = PP + (WS - PP) * (L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)) / (
#         lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
#     )
#     Φ2 = PP + (WS - PP) * lam3 * math.tanh(L3 / lam3) / (
#         lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
#     )
#     Φ_uittrede = PP + (Φ2 - PP) * (math.sinh((L3 - L_BIT) / lam3)) / math.sinh(
#         L3 / lam3
#     )
#     h_exit = max(PP, MV)
#     dΦ = Φ_uittrede - h_exit
#     dΦc = d_dek * ((y_satdek - y_water) / y_water)
#     Zu = mu * dΦc - dΦ
#     return Zu


# def Zh(ic, L_intrede, L_BUT, k, D, c1, c3, L3, WS, PP, L_BIT, d_dek, MV):
#     L1 = L_intrede - L_BUT
#     lam1 = np.sqrt(k * D * c1)
#     lam3 = np.sqrt(k * D * c3)
#     Φ1 = PP + (WS - PP) * (L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)) / (
#         lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
#     )
#     Φ2 = PP + (WS - PP) * lam3 * math.tanh(L3 / lam3) / (
#         lam1 * math.tanh(L1 / lam1) + L_BUT - L_BIT + lam3 * math.tanh(L3 / lam3)
#     )
#     Φ_uittrede = PP + (Φ2 - PP) * (math.sinh((L3 - L_BIT) / lam3)) / math.sinh(
#         L3 / lam3
#     )
#     h_exit = max(PP, MV)
#     dΦ = Φ_uittrede - h_exit
#     Zh = ic - (dΦ / d_dek)
#     return Zh


# def Zp(L_intrede, L_BUT, k, D, c1, y_water, d70, mp, WS, d_dek, PP, MV):
#     L1 = L_intrede - L_BUT
#     lam1 = np.sqrt(k * D * c1)
#     w1 = lam1 * math.tanh(L1 / lam1)
#     L = w1 + L_BUT
#     k_ms = k / (24 * 3600)
#     k_intr = (0.00000133 / 9.81) * k_ms
#     Fres = 0.25 * ((26.0 - y_water) / y_water) * math.tan(37.0 * math.pi / 180.00)
#     Fscale = pow((d70 / 1.0e6) / 2.08e-4, 0.4) * 2.08e-4 / pow(k_intr * L, (1.0 / 3.0))
#     if D == L:
#         D = D - 0.001
#     else:
#         pass
#     totdemacht = 0.04 + (0.28 / (pow(D / L, 2.8) - 1.0))
#     Fgeom = 0.91 * pow(D / L, totdemacht)
#     Hc = Fres * Fscale * Fgeom * L
#     h_exit = max(PP, MV)
#     Zp = (mp * Hc) - (max(0.01, (WS - h_exit - (0.3 * d_dek))))
#     return Zp


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
    kD_wvp: float,
    D_wvp: float,
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

    Gecombineerde grenstoestandfunctie voor uplift, heave en piping. 
    Returns:
            Y[0] (float): Z_u: limit state uplift [-]
            Y[1] (float): Z_h: limit state heave [-]
            Y[2] (float): Z_p: limit state piping [-]
            Y[3] (float): Z_combin: limit state combinatie uplift, heave en piping [-]
    """

    # Berekening deklaagdikte
    Dcover = piping_functions_old.calc_Dcover(mv, top_zand)

    # Berekening niveau bij het uittredepunt
    h_exit = piping_functions_old.calc_h_exit(pp, mv)

    # Berekening gereduceerd verval
    dhred = piping_functions_old.calc_dH_red(h, h_exit, rc, Dcover)

    # Berekening grenspotentiaal
    d_pot_c_u = piping_functions_old.calc_d_pot_c_u(Dcover, gamma_sat_cover, gamma_w)

    # Berekening geometrische waarden voor potentiaalberekening
    L1 = dist_L_geom - dist_BUT
    L2 = dist_BUT - dist_BIT
    # L3 is al opgegeven

    # potentiaalberekening
    k = kD_wvp / D_wvp
    # aanroepen functie potentiaalberekening, x_bit = 0.0 zodat we dist_BIT kunnen gebruiken als x)
    pot_model = model4a.Model4a(
        k=k, D=D_wvp, c1=c_1, c3=c_3, L1=L1, L3=L3_geom, x_but=(0.0 - L2), x_bit=0.0
    )
    r_exit, r_but, r_bit = pot_model.respons(dist_BIT)
    pot_exit = geohydro_functions.calc_respons2pot(pp, r_exit, h)

    # Kwelweglengte
    L_kwelweg = pot_model.W1 + dist_BUT

    # uplift
    Z_u = piping_functions_old.calc_Z_u(d_pot_c_u, pot_exit, h_exit, mu)

    # heave
    i_optredend = piping_functions_old.calc_i_optredend(pot_exit, h_exit, Dcover)
    Z_h = piping_functions_old.calc_Z_h(i_c_h, i_optredend, mh)

    # piping
    dhc = piping_functions_old.calc_dH_sellmeijer(d70, k, D_wvp, L_kwelweg, gamma_w)
    Z_p = piping_functions_old.calc_Z_p(dhc, dhred, mp)

    # combinatie
    Z_combin = max(Z_u, Z_h, Z_p)

    return [Z_u,Z_h,Z_p,Z_combin]
    
