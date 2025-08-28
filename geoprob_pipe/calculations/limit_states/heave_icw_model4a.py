import geoprob_pipe.calculations.physical_components.piping as pc_piping
from typing import Tuple


# noinspection PyPep8Naming
def z_heave(
        L_achterland: float,
        c_voorland: float,
        c_achterland: float,
        L_intrede: float,
        L_but: float,
        L_bit: float,
        polderpeil: float,
        buitenwaterstand: float,
        mv_exit: float,
        top_zand: float,
        kD_wvp: float,
        modelfactor_h: float,
        i_c_h: float,
        D_wvp: float,
        **_,
) -> Tuple[float, float, float, float, float, float, float]:
    r"""Grenstoestandfunctie voor het mechanisme heave. """

    lengte_voorland = pc_piping.calc_lengte_voorland(
        L_intrede=L_intrede,
        L_but=L_but,
    )

    r_exit = pc_piping.calc_r_exit_model4a(
        kD_wvp=kD_wvp,
        D_wvp=D_wvp,
        c_voorland=c_voorland,
        c_achterland=c_achterland,
        L_but=L_but,
        L_bit=L_bit,
        L_achterland=L_achterland,
        L_voorland=lengte_voorland
    )

    phi_exit = pc_piping.calc_phi_exit(
        polderpeil=polderpeil,
        r_exit=r_exit,
        buitenwaterstand=buitenwaterstand
    )

    h_exit = pc_piping.calc_h_exit(
        polderpeil=polderpeil,
        mv_exit=mv_exit
    )

    d_deklaag = pc_piping.calc_d_deklaag(
        mv_exit=mv_exit,
        top_zand=top_zand
    )

    i_exit = pc_piping.calc_i_exit(
        phi_exit=phi_exit,
        h_exit=h_exit,
        d_deklaag=d_deklaag
    )

    z_h = (modelfactor_h * i_c_h) - i_exit

    return z_h, lengte_voorland, r_exit, phi_exit, h_exit, d_deklaag, i_exit


