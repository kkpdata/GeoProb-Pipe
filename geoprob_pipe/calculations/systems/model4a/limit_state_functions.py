from geoprob_pipe.calculations.limit_states.piping_lm import (
    limit_state_model4a)


# noinspection PyPep8Naming
def calc_Z_u(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float,
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        top_zand: float, kD_wvp: float, D_wvp: float, d70: float,
        gamma_sat_deklaag: float, c_voorland: float, c_achterland: float,
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float,
        modelfactor_ml: float, i_c_h: float, r_c_deklaag: float, d70_m: float,
        gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """

    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit,
        L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand,
        kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland,
        c_achterland=c_achterland, modelfactor_u=modelfactor_u,
        modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d,
        modelfactor_aniso=modelfactor_aniso, modelfactor_ml=modelfactor_ml,
        i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m,
        gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
        gamma_water=gamma_water)[0]


# noinspection PyPep8Naming
def calc_Z_h(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float,
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        top_zand: float, kD_wvp: float, D_wvp: float, d70: float,
        gamma_sat_deklaag: float, c_voorland: float, c_achterland: float,
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float,
        modelfactor_ml: float, i_c_h: float, r_c_deklaag: float, d70_m: float,
        gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r""" Wrapper over de grenstoestandfunctie voor heave zodat deze bruikbaar
    is voor de Probabilistic Library.

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit,
        L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand,
        kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland,
        c_achterland=c_achterland, modelfactor_u=modelfactor_u,
        modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d,
        modelfactor_aniso=modelfactor_aniso, modelfactor_ml=modelfactor_ml,
        i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m,
        gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
        gamma_water=gamma_water)[1]


# noinspection PyPep8Naming
def calc_Z_p(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float,
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        top_zand: float, kD_wvp: float, D_wvp: float, d70: float,
        gamma_sat_deklaag: float, c_voorland: float, c_achterland: float,
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float,
        modelfactor_ml: float, i_c_h: float, r_c_deklaag: float, d70_m: float,
        gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit,
        L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand,
        kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland,
        c_achterland=c_achterland, modelfactor_u=modelfactor_u,
        modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d,
        modelfactor_aniso=modelfactor_aniso, modelfactor_ml=modelfactor_ml,
        i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m,
        gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
        gamma_water=gamma_water)[2]


# noinspection PyPep8Naming
def calc_Z_project(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float,
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        top_zand: float, kD_wvp: float, D_wvp: float, d70: float,
        gamma_sat_deklaag: float, c_voorland: float, c_achterland: float,
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float,
        modelfactor_ml: float, i_c_h: float, r_c_deklaag: float, d70_m: float,
        gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit,
        L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand,
        kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland,
        c_achterland=c_achterland, modelfactor_u=modelfactor_u,
        modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d,
        modelfactor_aniso=modelfactor_aniso, modelfactor_ml=modelfactor_ml,
        i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m,
        gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
        gamma_water=gamma_water)[3]


MODEL_NAMES = {
    calc_Z_h.__name__: "Heave",
    calc_Z_u.__name__: "Uplift",
    calc_Z_p.__name__: "Piping",
}
