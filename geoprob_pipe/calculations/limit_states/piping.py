import geoprob_pipe.calculations.physical_components.piping as pc_piping
from typing import Tuple


# noinspection PyPep8Naming
def z_piping(
        c_voorland: float, buitenwaterstand: float, polderpeil: float, mv_exit: float, L_but: float, L_intrede: float,
        modelfactor_p: float, d70: float, D_wvp: float, kD_wvp: float, top_zand: float, gamma_water: float, g: float,
        v: float, theta: float, eta: float, d70_m: float, gamma_korrel: float, r_c_deklaag: float, **_,
) -> Tuple[float, float, float, float, float, float, float, float, float]:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """

    L_voorland = pc_piping.calc_lengte_voorland(L_intrede=L_intrede, L_but=L_but)
    lambda_voorland = pc_piping.calc_lambda_voorland(kD_wvp=kD_wvp, c_voorland=c_voorland)
    W_voorland = pc_piping.calc_W_voorland(lambda_voorland=lambda_voorland, L_voorland=L_voorland)
    L_kwelweg = pc_piping.calc_L_kwelweg(L_but=L_but, W_voorland=W_voorland)
    dh_c = pc_piping.calc_dh_c(
        d70=d70, D_wvp=D_wvp, kD_wvp=kD_wvp, L_kwelweg=L_kwelweg, gamma_water=gamma_water, g=g, v=v, theta=theta,
        eta=eta, d70_m=d70_m, gamma_korrel=gamma_korrel)
    h_exit = pc_piping.calc_h_exit(polderpeil=polderpeil,mv_exit=mv_exit)
    d_deklaag = pc_piping.calc_d_deklaag(mv_exit=mv_exit, top_zand=top_zand)
    dh_red = pc_piping.calc_dh_red(
        buitenwaterstand=buitenwaterstand, h_exit=h_exit, r_c_deklaag=r_c_deklaag, d_deklaag=d_deklaag)

    z_p = (modelfactor_p * dh_c) - dh_red

    return z_p, L_voorland, lambda_voorland, W_voorland, L_kwelweg, dh_c, h_exit, d_deklaag, dh_red
