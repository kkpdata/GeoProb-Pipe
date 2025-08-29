import geoprob_pipe.calculations.physical_components.piping as pc_piping
from typing import Tuple


# noinspection PyPep8Naming
def z_uplift(
        L_achterland: float, c_voorland: float, c_achterland: float, polderpeil: float, buitenwaterstand: float,
        L_intrede: float, L_but: float, L_bit: float, mv_exit: float, top_zand: float, kD_wvp: float,
        modelfactor_u: float, gamma_water: float, gamma_sat_deklaag: float, D_wvp: float, **_,
) -> Tuple[float, float, float, float, float, float, float]:
    """Grenstoestandfunctie voor opbarsten (uplift). """

    L_voorland = pc_piping.calc_lengte_voorland(L_intrede=L_intrede, L_but=L_but)
    r_exit = pc_piping.calc_r_exit_model4a(
        kD_wvp=kD_wvp, D_wvp=D_wvp, c_voorland=c_voorland, c_achterland=c_achterland, L_but=L_but,  L_bit=L_bit,
        L_achterland=L_achterland, L_voorland=L_voorland)
    phi_exit = pc_piping.calc_phi_exit(polderpeil=polderpeil, r_exit=r_exit, buitenwaterstand=buitenwaterstand)
    h_exit = pc_piping.calc_h_exit( polderpeil=polderpeil, mv_exit=mv_exit)
    d_deklaag = pc_piping.calc_d_deklaag(mv_exit=mv_exit, top_zand=top_zand)
    dphi_c_u = pc_piping.calc_dphi_c_u(
        d_deklaag=d_deklaag, gamma_sat_deklaag=gamma_sat_deklaag, gamma_water=gamma_water)

    z_u = modelfactor_u * dphi_c_u - (phi_exit - h_exit)

    return z_u, L_voorland, r_exit, phi_exit, h_exit, d_deklaag, dphi_c_u

